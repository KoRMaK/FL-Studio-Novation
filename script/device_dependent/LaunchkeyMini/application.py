from script.device_dependent.common import MixerPanPotLayoutManager, MixerVolumePotLayoutManager
from script.device_dependent.LaunchkeyRange import DrumPadLayoutManager
from script.device_independent.fl_gui.fl_window_manager import FLWindowManager
from script.device_independent.view import (
    ChannelSelectNameHighlightView,
    ChannelSelectView,
    DiscardedSurfaceInteractionNotificationView,
    MixerBankView,
    TransportPlayStopButtonView,
    TransportRecordButtonView,
)
from script.model import Model
from util.command_dispatcher import CommandDispatcher


class Application:
    def __init__(
        self, pad_led_writer, button_led_writer, fl, action_dispatcher, screen_writer, device_manager, product_defs
    ):
        self.active_pot_layout_manager = None
        self.active_pad_layout_manager = None
        self.pad_led_writer = pad_led_writer
        self.button_led_writer = button_led_writer
        self.fl = fl
        self.action_dispatcher = action_dispatcher
        self.command_dispatcher = CommandDispatcher()
        self.screen_writer = screen_writer
        self.product_defs = product_defs
        self.model = None

        self.global_views = set()
        self.fl_window_manager = FLWindowManager(action_dispatcher, fl)

    def init(self):
        self.active_pad_layout_manager = None
        self.active_pot_layout_manager = None
        self.model = Model()
        self.action_dispatcher.subscribe(self)

        self.global_views = {
            ChannelSelectNameHighlightView(self.action_dispatcher, self.fl, self.model),
            ChannelSelectView(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs),
            DiscardedSurfaceInteractionNotificationView(self.action_dispatcher, self.fl, self.screen_writer),
            MixerBankView(
                self.action_dispatcher,
                self.command_dispatcher,
                self.button_led_writer,
                self.fl,
                self.product_defs,
                self.model,
            ),
            TransportRecordButtonView(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs),
            TransportPlayStopButtonView(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs),
        }
        for view in self.global_views:
            view.show()

    def deinit(self):
        if self.active_pot_layout_manager:
            self.active_pot_layout_manager.hide()

        if self.active_pad_layout_manager:
            self.active_pad_layout_manager.hide()

        for view in self.global_views:
            view.hide()

        self.action_dispatcher.unsubscribe(self)

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

    def _create_pad_layout_manager(self, layout):
        if layout == self.product_defs.PadLayout.Drum:
            return DrumPadLayoutManager(
                self.action_dispatcher,
                self.pad_led_writer,
                self.button_led_writer,
                self.fl,
                self.product_defs,
                self.model,
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
