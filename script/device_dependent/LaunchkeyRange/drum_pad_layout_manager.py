from script.actions import FlGuiChannelSelectAction
from script.constants import ModoDrumPadMapping, ModoDrumPadColors
from script.device_independent import view
from script.device_independent.view import Fpc, FpcBankView, ModoDrum
from script.fl_constants import InstrumentPlugin, RefreshFlags
from util.mapped_pad_led_writer import MappedPadLedWriter


class DrumPadLayoutManager:
    def __init__(self, action_dispatcher, pad_led_writer, button_led_writer, fl, product_defs, model, channel_selection_manager=None):
        self.action_dispatcher = action_dispatcher
        self.button_led_writer = button_led_writer
        self.fl = fl
        self.product_defs = product_defs
        self.model = model
        self.channel_selection_manager = channel_selection_manager
        self.pad_led_writer = MappedPadLedWriter(
            pad_led_writer, product_defs.Constants.NotesForPadLayout.value[product_defs.PadLayout.Drum]
        )
        self.channel_selection_dependent_views = {
            view.ChannelSelectNameHighlightView(self.action_dispatcher, self.fl, model, channel_selection_manager),
        }
        self.channel_selection_independent_views = {
            view.AnalogLabPadView(self.action_dispatcher, self.pad_led_writer, self.fl, channel_selection_manager),
            view.ChannelSelectView(self.action_dispatcher, button_led_writer, self.fl, product_defs, channel_selection_manager),
        }

        # Track current plugin and channel for dynamic view switching
        self.selected_channel = None
        self.selected_plugin = None
        self.active_instrument_view = None
        self.active_plugin_bank_view = None

    def show(self):
        self.action_dispatcher.subscribe(self)

        self.model.default_instrument_layout.note_offset_for_pad = {
            pad: self.model.default_instrument_layout.Note(note)
            for pad, note in enumerate([4, 5, 6, 7, 12, 13, 14, 15, 0, 1, 2, 3, 8, 9, 10, 11])
        }

        # Check if any channel is selected (using independent selection if available)
        if self.channel_selection_manager:
            has_selection = self.channel_selection_manager.get_active_channel() is not None
        else:
            has_selection = self.fl.is_any_channel_selected()

        if has_selection:
            self._handle_channel_selected()
            for global_view in self.channel_selection_dependent_views:
                global_view.show()

        for global_view in self.channel_selection_independent_views:
            global_view.show()

    def hide(self):
        # Check if any channel is selected (using independent selection if available)
        if self.channel_selection_manager:
            has_selection = self.channel_selection_manager.get_active_channel() is not None
        else:
            has_selection = self.fl.is_any_channel_selected()

        if has_selection:
            for global_view in self.channel_selection_dependent_views:
                global_view.hide()

        for global_view in self.channel_selection_independent_views:
            global_view.hide()

        # Hide active instrument view
        if self.active_instrument_view:
            self.active_instrument_view.hide()
            self.active_instrument_view = None

        # Hide active bank view
        if self.active_plugin_bank_view:
            self.active_plugin_bank_view.hide()
            self.active_plugin_bank_view = None

        self.model.default_instrument_layout.note_offset_for_pad = {}

        self.action_dispatcher.unsubscribe(self)

    def handle_OnRefreshAction(self, action):
        # Check if any channel is selected (using independent selection if available)
        if self.channel_selection_manager:
            has_selection = self.channel_selection_manager.get_active_channel() is not None
        else:
            has_selection = self.fl.is_any_channel_selected()

        if has_selection:
            if action.flags & RefreshFlags.ChannelSelection.value or action.flags & RefreshFlags.ChannelGroup.value:
                self._handle_channel_selected()
                self.action_dispatcher.dispatch(FlGuiChannelSelectAction())

    def handle_ChannelSelectionToggleAction(self, action):
        if action.any_channel_selected:
            self._handle_channel_selected()
            for global_view in self.channel_selection_dependent_views:
                global_view.show()
        else:
            # Hide active instrument view when channel is unselected
            if self.active_instrument_view:
                self.active_instrument_view.hide()
                self.active_instrument_view = None
            # Hide active bank view when channel is unselected
            if self.active_plugin_bank_view:
                self.active_plugin_bank_view.hide()
                self.active_plugin_bank_view = None
            for global_view in self.channel_selection_dependent_views:
                global_view.hide()

    def _handle_channel_selected(self):
        """Handle channel selection and detect plugin changes"""
        # Determine which channel is selected
        if self.channel_selection_manager:
            current_channel = self.channel_selection_manager.get_active_channel()
        else:
            current_channel = self.fl.get_selected_global_channel() if self.fl.is_any_channel_selected() else None

        if current_channel is None:
            return

        # Get the plugin for the selected channel
        current_plugin = self.fl.get_plugin_for_channel(current_channel)

        # Check if plugin changed
        if current_channel == self.selected_channel and current_plugin == self.selected_plugin:
            return

        self.selected_channel = current_channel
        self.selected_plugin = current_plugin
        self._handle_plugin_changed()

    def _handle_plugin_changed(self):
        """Handle plugin change by switching views"""
        if self.active_instrument_view:
            self.active_instrument_view.hide()
        if self.active_plugin_bank_view:
            self.active_plugin_bank_view.hide()

        self.active_instrument_view = self._create_instrument_view_for_plugin(self.selected_plugin)
        self.active_instrument_view.show()

        self.active_plugin_bank_view = self._create_bank_view_for_plugin(self.selected_plugin)
        self.active_plugin_bank_view.show()

    def _create_instrument_view_for_plugin(self, plugin):
        """Create appropriate view based on detected plugin"""
        if plugin == InstrumentPlugin.Fpc.value:
            return Fpc(
                self.action_dispatcher,
                self.pad_led_writer,
                self.fl,
                self.model,
                self.channel_selection_manager
            )
        if plugin == InstrumentPlugin.ModoDrum.value:
            return ModoDrum(
                self.action_dispatcher,
                self.pad_led_writer,
                self.fl,
                self.model,
                ModoDrumPadMapping,
                ModoDrumPadColors if ModoDrumPadColors else None
            )
        # Default view for all other plugins
        return view.Default(self.action_dispatcher, self.pad_led_writer, self.fl, self.model, self.channel_selection_manager)

    def _create_bank_view_for_plugin(self, plugin):
        """Create appropriate bank view based on detected plugin"""
        if plugin == InstrumentPlugin.Fpc.value:
            return FpcBankView(self.action_dispatcher, self.button_led_writer, self.product_defs, self.model)
        if plugin == InstrumentPlugin.ModoDrum.value:
            return FpcBankView(self.action_dispatcher, self.button_led_writer, self.product_defs, self.model)
        # Default bank view for all other plugins
        return view.DefaultBankView(self.action_dispatcher, self.button_led_writer, self.product_defs, self.model)
