from script.device_dependent.common import (
    MixerPanPotLayoutManager,
    MixerVolumeFaderLayoutManager,
    MixerVolumePotLayoutManager,
)
from script.device_dependent.FLkeyRange import (
    ChannelRackPadLayoutManager,
    CustomPadLayoutManager,
    InstrumentPadLayoutManager,
    MomentaryPotLayoutManager,
    PluginPotLayoutManager,
    SequencerPadLayoutManager,
)
from script.device_independent.fl_gui.fl_window_manager import FLWindowManager
from script.device_independent.view import (
    AnalogLabPresetButtonView,
    ButtonFunctionScreenView,
    ChannelSelectedScreenView,
    CloneCurrentPatternView,
    DiscardedSurfaceInteractionNotificationView,
    DumpScoreLogButtonView,
    MetronomeButtonView,
    MixerBankView,
    MixerMasterVolumeView,
    MixerSoloMuteScreenView,
    MixerTrackPluginSelectedScreenView,
    MixerTrackPluginSelectView,
    MixerTrackSelectedScreenView,
    MixerTrackSelectView,
    MixerVolumeScreenView,
    PatternSelectScreenView,
    QuantiseButtonView,
    RedoButtonView,
    ScaleModelController,
    SelectNewPatternView,
    SequencerPageResetController,
    SequencerStepEditScreenView,
    ShowHighlightsView,
    TapTempoButtonView,
    TransportPlayPauseButtonView,
    TransportRecordButtonView,
    TransportStopButtonView,
    UndoButtonView,
)
from script.model import Model
from util.command_dispatcher import CommandDispatcher

from .channel_pan_pot_layout_manager import ChannelPanPotLayoutManager
from .channel_volume_fader_layout_manager import ChannelVolumeFaderLayoutManager
from .channel_volume_pot_layout_manager import ChannelVolumePotLayoutManager
from .patterns_pad_layout_manager import PatternsPadLayoutManager
from .plugin_fader_layout_manager import PluginFaderLayoutManager
from .scale_chord_pad_layout_manager import ScaleChordPadLayoutManager
from .user_chord_pad_layout_manager import UserChordPadLayoutManager


class Application:
    def __init__(
        self, pad_led_writer, button_led_writer, fl, action_dispatcher, screen_writer, device_manager, product_defs
    ):
        self.active_pad_layout_manager = None
        self.active_pot_layout_manager = None
        self.active_fader_layout_manager = None
        self.pad_led_writer = pad_led_writer
        self.button_led_writer = button_led_writer
        self.fl = fl
        self.action_dispatcher = action_dispatcher
        self.command_dispatcher = CommandDispatcher()
        self.screen_writer = screen_writer
        self.device_manager = device_manager
        self.product_defs = product_defs
        self.model = None

        self.global_views = set()
        self.fl_window_manager = FLWindowManager(action_dispatcher, fl)

    def init(self):
        self.active_pad_layout_manager = None
        self.active_pot_layout_manager = None
        self.active_fader_layout_manager = None
        self.model = Model()
        self.action_dispatcher.subscribe(self)

        self.global_views = {
            AnalogLabPresetButtonView(self.action_dispatcher, self.fl, self.product_defs),
            ButtonFunctionScreenView(self.action_dispatcher, self.screen_writer, self.fl),
            ChannelSelectedScreenView(self.action_dispatcher, self.screen_writer, self.fl),
            DumpScoreLogButtonView(self.action_dispatcher, self.fl, self.product_defs),
            MetronomeButtonView(self.action_dispatcher, self.fl, self.product_defs),
            MixerSoloMuteScreenView(self.action_dispatcher, self.fl, self.screen_writer),
            MixerBankView(
                self.action_dispatcher,
                self.command_dispatcher,
                self.button_led_writer,
                self.fl,
                self.product_defs,
                self.model,
            ),
            CloneCurrentPatternView(self.action_dispatcher, self.product_defs, self.fl, self.button_led_writer),
            DiscardedSurfaceInteractionNotificationView(self.action_dispatcher, self.fl, self.screen_writer),
            MixerMasterVolumeView(self.action_dispatcher, self.fl),
            MixerTrackPluginSelectView(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs),
            MixerTrackPluginSelectedScreenView(self.action_dispatcher, self.screen_writer, self.fl),
            MixerTrackSelectView(
                self.action_dispatcher, self.product_defs, self.model, self.button_led_writer, self.fl
            ),
            MixerTrackSelectedScreenView(self.action_dispatcher, self.screen_writer, self.fl),
            MixerVolumeScreenView(self.action_dispatcher, self.screen_writer, self.fl),
            PatternSelectScreenView(self.action_dispatcher, self.fl, self.screen_writer),
            QuantiseButtonView(self.action_dispatcher, self.fl, self.product_defs),
            RedoButtonView(self.action_dispatcher, self.fl, self.product_defs),
            ScaleModelController(self.action_dispatcher, self.product_defs, self.model),
            SelectNewPatternView(self.action_dispatcher, self.product_defs, self.fl, self.button_led_writer),
            SequencerPageResetController(self.action_dispatcher, self.model, self.fl),
            SequencerStepEditScreenView(self.action_dispatcher, self.screen_writer, self.fl),
            ShowHighlightsView(self.action_dispatcher, self.product_defs, self.model),
            TapTempoButtonView(self.action_dispatcher, self.fl, self.product_defs),
            TransportPlayPauseButtonView(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs),
            TransportRecordButtonView(self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs),
            TransportStopButtonView(self.action_dispatcher, self.fl, self.product_defs),
            UndoButtonView(self.action_dispatcher, self.fl, self.product_defs),
        }
        for view in self.global_views:
            view.show()

    def deinit(self):
        if self.active_fader_layout_manager:
            self.active_fader_layout_manager.hide()

        if self.active_pad_layout_manager:
            self.active_pad_layout_manager.hide()

        if self.active_pot_layout_manager:
            self.active_pot_layout_manager.hide()

        for view in self.global_views:
            view.hide()

        self.action_dispatcher.unsubscribe(self)

    def handle_TempoChangedAction(self, action):
        self.device_manager.set_tempo(self.fl.get_tempo())
        if self.fl.get_master_sync_enabled():
            self.screen_writer.display_notification(primary_text="Tempo (External)")

    def handle_ButtonPressedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("TapTempo"):
            if self.fl.get_master_sync_enabled():
                self.screen_writer.display_notification(primary_text="Tempo (External)")

        if action.button == self.product_defs.FunctionToButton.get("ShiftModifier"):
            self.button_led_writer.shift_modifier_pressed()

    def handle_ButtonReleasedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("ShiftModifier"):
            self.button_led_writer.shift_modifier_released()

    def handle_PadLayoutChangedAction(self, action):
        if self.active_pad_layout_manager:
            self.active_pad_layout_manager.hide()

        self.active_pad_layout_manager = self._create_pad_layout_manager(action.layout)
        if self.active_pad_layout_manager:
            self.active_pad_layout_manager.show()

    def handle_PotLayoutChangedAction(self, action):
        skip_window_focusing = isinstance(self.active_pot_layout_manager, MomentaryPotLayoutManager)

        if self.active_pot_layout_manager:
            self.active_pot_layout_manager.hide()

        self.active_pot_layout_manager = self._create_pot_layout_manager(action.layout)
        if self.active_pot_layout_manager:
            self.active_pot_layout_manager.show()
            if not skip_window_focusing:
                self.active_pot_layout_manager.focus_windows()

    def handle_FaderLayoutChangedAction(self, action):
        if self.active_fader_layout_manager:
            self.active_fader_layout_manager.hide()

        self.active_fader_layout_manager = self._create_fader_layout_manager(action.layout)
        if self.active_fader_layout_manager:
            self.active_fader_layout_manager.show()
            self.active_fader_layout_manager.focus_windows()

    def _create_pad_layout_manager(self, layout):
        if layout == self.product_defs.PadLayout.ChannelRack:
            return ChannelRackPadLayoutManager(
                self.action_dispatcher,
                self.pad_led_writer,
                self.button_led_writer,
                self.screen_writer,
                self.fl,
                self.product_defs,
                self.model,
                self.fl_window_manager,
            )
        if layout == self.product_defs.PadLayout.Instrument:
            return InstrumentPadLayoutManager(
                self.action_dispatcher,
                self.pad_led_writer,
                self.button_led_writer,
                self.screen_writer,
                self.fl,
                self.product_defs,
                self.model,
            )
        if layout == self.product_defs.PadLayout.Sequencer:
            return SequencerPadLayoutManager(
                self.action_dispatcher,
                self.command_dispatcher,
                self.pad_led_writer,
                self.button_led_writer,
                self.screen_writer,
                self.fl,
                self.product_defs,
                self.model,
                self.device_manager,
                self.fl_window_manager,
            )
        if layout == self.product_defs.PadLayout.Patterns:
            return PatternsPadLayoutManager(
                self.action_dispatcher,
                self.product_defs,
                self.fl,
                self.model,
                self.pad_led_writer,
                self.button_led_writer,
                self.fl_window_manager,
            )
        if layout == self.product_defs.PadLayout.ScaleChord:
            return ScaleChordPadLayoutManager(
                self.action_dispatcher,
                self.button_led_writer,
                self.screen_writer,
                self.fl,
                self.product_defs,
                self.model,
            )
        if layout == self.product_defs.PadLayout.UserChord:
            return UserChordPadLayoutManager(
                self.action_dispatcher, self.button_led_writer, self.fl, self.product_defs, self.model
            )
        if layout == self.product_defs.PadLayout.Custom:
            return CustomPadLayoutManager(
                self.action_dispatcher,
                self.button_led_writer,
                self.screen_writer,
                self.fl,
                self.product_defs,
                self.model,
            )

        return None

    def _create_pot_layout_manager(self, layout):
        if layout == self.product_defs.PotLayout.MixerVolume:
            return MixerVolumePotLayoutManager(
                self.action_dispatcher,
                self.command_dispatcher,
                self.fl,
                self.screen_writer,
                self.model,
                self.fl_window_manager,
            )
        if layout == self.product_defs.PotLayout.MixerPan:
            return MixerPanPotLayoutManager(
                self.action_dispatcher,
                self.command_dispatcher,
                self.fl,
                self.screen_writer,
                self.model,
                self.fl_window_manager,
            )
        if layout == self.product_defs.PotLayout.ChannelVolume:
            return ChannelVolumePotLayoutManager(
                self.action_dispatcher, self.fl, self.screen_writer, self.model, self.fl_window_manager
            )
        if layout == self.product_defs.PotLayout.ChannelPan:
            return ChannelPanPotLayoutManager(
                self.action_dispatcher, self.fl, self.screen_writer, self.model, self.fl_window_manager
            )
        if layout == self.product_defs.PotLayout.Plugin:
            return PluginPotLayoutManager(
                self.action_dispatcher,
                self.fl,
                self.screen_writer,
                self.model,
                self.product_defs,
                self.button_led_writer,
            )
        if layout == self.product_defs.PotLayout.Momentary:
            return MomentaryPotLayoutManager(self.action_dispatcher, self.fl, self.model)
        return None

    def _create_fader_layout_manager(self, layout):
        if layout == self.product_defs.FaderLayout.MixerVolume:
            return MixerVolumeFaderLayoutManager(
                self.action_dispatcher,
                self.command_dispatcher,
                self.product_defs,
                self.fl,
                self.model,
                self.button_led_writer,
                self.fl_window_manager,
            )
        if layout == self.product_defs.FaderLayout.Plugin:
            return PluginFaderLayoutManager(self.action_dispatcher, self.fl, self.screen_writer)
        if layout == self.product_defs.FaderLayout.ChannelVolume:
            return ChannelVolumeFaderLayoutManager(
                self.action_dispatcher,
                self.fl,
                self.product_defs,
                self.model,
                self.screen_writer,
                self.button_led_writer,
                self.fl_window_manager,
            )
        return None
