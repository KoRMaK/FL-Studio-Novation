import version
from script.action_generators.fl_action_generator.fl_actions import (
    DeviceInteractionResumedAction,
    DeviceInteractionSuspendedAction,
)
from script.action_generators.surface_action_generator.surface_actions import (
    ButtonPressedAction,
    ButtonReleasedAction,
    ControlChangedAction,
    PadPressAction,
    PadReleaseAction,
)
from script.fl_constants import ProjectLoadStatus
from util.decorators import cache_led_updates, detect_status_change
from util.print import print_to_script_output


def detect_api_unsafe_status_change(func):
    return detect_status_change(
        func,
        get_status=lambda self: self.get_api_unsafe_status(),
        on_change=lambda self: self.handle_api_unsafe_status_change(),
    )


class FLToApplicationAdapter:
    def __init__(
        self,
        device_setup,
        fl_setup,
        application,
        led_update_cache,
        fl,
        action_dispatcher,
        surface_action_generator,
        fl_action_generator,
        firmware_version_validation_controller,
        fl_api_version_check_controller,
        reset_device_adapters,
    ):
        self.device_setup = device_setup
        self.fl_setup = fl_setup
        self.application = application
        self.led_update_cache = led_update_cache
        self.fl = fl
        self.action_dispatcher = action_dispatcher
        self.surface_action_generator = surface_action_generator
        self.fl_action_generator = fl_action_generator
        self.firmware_version_validation_controller = firmware_version_validation_controller
        self.fl_api_version_check_controller = fl_api_version_check_controller
        self.reset_device_adapters = reset_device_adapters

    @property
    def led_cache(self):
        return self.led_update_cache

    @detect_api_unsafe_status_change
    @cache_led_updates
    def on_init(self):
        self._print_script_version()
        self.fl_api_version_check_controller.check_version()
        self.firmware_version_validation_controller.start_validation(on_success_callback=self._do_initialisation)

    def _do_initialisation(self):
        if self.firmware_version_validation_controller.validation_is_success():
            self.reset_device_adapters()
            self.device_setup.init()
            self.application.init()

    @detect_api_unsafe_status_change
    @cache_led_updates
    def on_deinit(self):
        self.firmware_version_validation_controller.abort_validation()
        self._do_deinitialisation()

    def _do_deinitialisation(self):
        if self.firmware_version_validation_controller.validation_is_success():
            self.application.deinit()
            self.device_setup.deinit()

    @detect_api_unsafe_status_change
    @cache_led_updates
    def on_midi(self, fl_event):
        self.surface_action_generator.handle_midi_event(fl_event)
        self.firmware_version_validation_controller.handle_midi_event(fl_event)
        fl_event.handled = True

    @detect_api_unsafe_status_change
    @cache_led_updates
    def on_refresh(self, flags):
        self.fl_action_generator.handle_refresh_event(flags)

    @detect_api_unsafe_status_change
    @cache_led_updates
    def on_idle(self):
        self.fl_action_generator.handle_idle_event()

    @detect_api_unsafe_status_change
    @cache_led_updates
    def on_dirty_channel(self, channel, update_type):
        self.fl_action_generator.handle_dirty_channel_event(channel, update_type)

    @detect_api_unsafe_status_change
    @cache_led_updates
    def on_dirty_mixer_track(self, index):
        self.fl_action_generator.handle_dirty_mixer_track_event(index)

    def on_project_load(self, status):
        if status == ProjectLoadStatus.LoadStart:
            self._do_deinitialisation()
        if status == ProjectLoadStatus.LoadFinished:
            self._do_initialisation()

    @detect_api_unsafe_status_change
    @cache_led_updates
    def on_first_connect(self):
        self.fl_setup.handle_first_time_connected()

    def _print_script_version(self):
        print_to_script_output("version: {}".format(version.value))

    def get_api_unsafe_status(self):
        return self.fl.api_is_unsafe()

    def handle_api_unsafe_status_change(self):
        if self.get_api_unsafe_status():
            self.surface_action_generator.set_suspended_actions(
                {
                    ControlChangedAction,
                    ButtonPressedAction,
                    ButtonReleasedAction,
                    PadPressAction,
                    PadReleaseAction,
                }
            )

            self.action_dispatcher.dispatch(DeviceInteractionSuspendedAction())
        else:
            self.surface_action_generator.set_suspended_actions({})
            self.action_dispatcher.dispatch(DeviceInteractionResumedAction())
            self.fl_action_generator.refresh_all()
