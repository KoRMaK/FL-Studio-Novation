from script.notification_writer import NotificationWriter
from util.print import print_to_script_output
from util.timer import Timer


class FlApiVersionCheckController:
    timer_events_between_messages = 30

    def __init__(self, action_dispatcher, product_defs, fl):
        self.product_defs = product_defs
        self.fl = fl
        self.notification_timer = Timer(
            action_dispatcher, on_finished=self._keep_showing_incompatible_version_message_in_hint_panel
        )

    def check_version(self):
        try:
            minimum_api_version = self.product_defs.Constants.MinimumApiVersion.value
        except AttributeError:
            return

        api_version = self.fl.get_api_version()
        if api_version < minimum_api_version:
            self._handle_validation_failed(minimum_version_required=minimum_api_version, version_found=api_version)

    def _handle_validation_failed(self, *, minimum_version_required, version_found):
        device_name = self.product_defs.Constants.DisplayedDeviceName
        print_to_script_output(
            f"FL Studio API version required: {minimum_version_required}. Version found: {version_found}"
        )
        print_to_script_output(
            f"{device_name} requires a more recent version of FL Studio. Please update to the latest version."
        )
        self._keep_showing_incompatible_version_message_in_hint_panel()

    def _keep_showing_incompatible_version_message_in_hint_panel(self):
        device_name = self.product_defs.Constants.DisplayedDeviceName
        NotificationWriter.notify_incompatible_fl_studio_version(self.fl, device_name=device_name)
        self.notification_timer.start(self.timer_events_between_messages)
