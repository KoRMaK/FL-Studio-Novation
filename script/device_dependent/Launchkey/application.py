from script.device_dependent.common import (
    MixerPanPotLayoutManager,
    MixerVolumeFaderLayoutManager,
    MixerVolumePotLayoutManager,
)
from script.device_dependent.LaunchkeyRange import DrumPadLayoutManager, PluginPotLayoutManager
from script.device_independent.channel_selection_manager import ChannelSelectionManager
from script.device_independent.fl_gui.fl_window_manager import FLWindowManager
from script.device_independent.view import (
    AnalogLabPresetButtonView,
    ChannelSelectedScreenView,
    ChannelSelectNameHighlightView,
    ChannelSelectView,
    DiscardedSurfaceInteractionNotificationView,
    MetronomeButtonView,
    MixerBankView,
    MixerMasterVolumeView,
    MixerVolumeScreenView,
    PotModeSelectorView,
    TransportPlayPauseButtonView,
    TransportRecordButtonView,
    TransportStopButtonView,
    UndoButtonView,
)
from script.model import Model
from util.command_dispatcher import CommandDispatcher


class Application:
    def __init__(
        self, pad_led_writer, button_led_writer, fl, action_dispatcher, screen_writer, device_manager, product_defs
    ):
        self.active_pot_layout_manager = None
        self.active_pad_layout_manager = None
        self.active_fader_layout_manager = None
        self.pad_led_writer = pad_led_writer
        self.button_led_writer = button_led_writer
        self.fl = fl
        self.action_dispatcher = action_dispatcher
        self.command_dispatcher = CommandDispatcher()
        self.screen_writer = screen_writer
        self.product_defs = product_defs
        self.device_manager = device_manager
        self.model = None
        self.channel_selection_manager = None

        self.global_views = set()
        self.fl_window_manager = FLWindowManager(action_dispatcher, fl)
        self.on_first_time_fader_layout_selected = None

    def init(self):
        self.active_pad_layout_manager = None
        self.active_pot_layout_manager = None
        self.active_fader_layout_manager = None
        self.model = Model()
        self.on_first_time_fader_layout_selected = self._select_pan_pot_layout

        # Initialize independent channel selection for Launchkey
        self.channel_selection_manager = ChannelSelectionManager(self.model, self.fl)
        self.channel_selection_manager.sync_with_fl_studio_ui()

        self.action_dispatcher.subscribe(self)

        self.global_views = {
            AnalogLabPresetButtonView(self.action_dispatcher, self.fl, self.product_defs, self.channel_selection_manager),
            ChannelSelectedScreenView(self.action_dispatcher, self.screen_writer, self.fl, self.channel_selection_manager),
            ChannelSelectNameHighlightView(self.action_dispatcher, self.fl, self.model, self.channel_selection_manager),
            ChannelSelectView(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs, self.channel_selection_manager),
            DiscardedSurfaceInteractionNotificationView(self.action_dispatcher, self.fl, self.screen_writer),
            TransportPlayPauseButtonView(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs),
            TransportStopButtonView(self.action_dispatcher, self.fl, self.product_defs),
            TransportRecordButtonView(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs),
            MetronomeButtonView(self.action_dispatcher, self.fl, self.product_defs),
            MixerBankView(
                self.action_dispatcher,
                self.command_dispatcher,
                self.button_led_writer,
                self.fl,
                self.product_defs,
                self.model,
            ),
            MixerMasterVolumeView(self.action_dispatcher, self.fl),
            MixerVolumeScreenView(self.action_dispatcher, self.screen_writer, self.fl),
            PotModeSelectorView(self.action_dispatcher, self.pad_led_writer, self.device_manager, self.product_defs, self.model),
            UndoButtonView(self.action_dispatcher, self.fl, self.product_defs),
        }
        for view in self.global_views:
            view.show()

    def deinit(self):
        if self.active_pot_layout_manager:
            self.active_pot_layout_manager.hide()

        if self.active_pad_layout_manager:
            self.active_pad_layout_manager.hide()

        if self.active_fader_layout_manager:
            self.active_fader_layout_manager.hide()

        for view in self.global_views:
            view.hide()

        self.action_dispatcher.unsubscribe(self)

    def _select_pan_pot_layout(self):
        self.device_manager.select_pot_layout(self.product_defs.PotLayout.Pan.value)

    def handle_PadLayoutChangedAction(self, action):
        if self.active_pad_layout_manager:
            self.active_pad_layout_manager.hide()

        self.active_pad_layout_manager = self._create_pad_layout_manager(action.layout)
        if self.active_pad_layout_manager:
            self.active_pad_layout_manager.show()

    def handle_PotLayoutChangedAction(self, action):
        if self.active_pot_layout_manager:
            self.active_pot_layout_manager.hide()

        self.active_pot_layout_manager = self._create_pot_layout_manager(action.layout)
        if self.active_pot_layout_manager:
            self.active_pot_layout_manager.show()
            self.active_pot_layout_manager.focus_windows()

    def handle_FaderLayoutChangedAction(self, action):
        if self.on_first_time_fader_layout_selected:
            self.on_first_time_fader_layout_selected()
            self.on_first_time_fader_layout_selected = None

        if self.active_fader_layout_manager:
            self.active_fader_layout_manager.hide()

        self.active_fader_layout_manager = self._create_fader_layout_manager(action.layout)
        if self.active_fader_layout_manager:
            self.active_fader_layout_manager.show()
            self.active_fader_layout_manager.focus_windows()

    def _create_pad_layout_manager(self, layout):
        if layout == self.product_defs.PadLayout.Drum:
            return DrumPadLayoutManager(
                self.action_dispatcher,
                self.pad_led_writer,
                self.button_led_writer,
                self.fl,
                self.product_defs,
                self.model,
                self.channel_selection_manager,
            )
        return None

    def _create_pot_layout_manager(self, layout):
        if layout == self.product_defs.PotLayout.Volume:
            return MixerVolumePotLayoutManager(
                self.action_dispatcher,
                self.command_dispatcher,
                self.fl,
                self.screen_writer,
                self.model,
                self.fl_window_manager,
            )
        if layout == self.product_defs.PotLayout.Plugin:
            return PluginPotLayoutManager(
                self.action_dispatcher,
                self.fl,
                self.screen_writer,
                self.channel_selection_manager,
            )
        if layout == self.product_defs.PotLayout.Pan:
            return MixerPanPotLayoutManager(
                self.action_dispatcher,
                self.command_dispatcher,
                self.fl,
                self.screen_writer,
                self.model,
                self.fl_window_manager,
            )
        return None

    def _create_fader_layout_manager(self, layout):
        if layout == self.product_defs.FaderLayout.Volume:
            return MixerVolumeFaderLayoutManager(
                self.action_dispatcher,
                self.command_dispatcher,
                self.product_defs,
                self.fl,
                self.model,
                self.button_led_writer,
                self.fl_window_manager,
            )
        return None
