from script.actions import PluginParameterValueChangedAction, PluginParameterPageChangedAction, CustomCcValueChangedAction
from script.constants import PluginParameterType
import script.device_adapters.fl_to_application_adapter.fl_to_application_adapter as fl_adapter
from script.device_independent.util_view.view import View
from script.device_independent.view.control_change_rate_limiter import ControlChangeRateLimiter
from script.fl_constants import PluginType, RefreshFlags
from util.deadzone_value_converter import DeadzoneValueConverter

try:
    import channels
    import device
    import general
    import midi
except ImportError:
    pass


class PluginParameterView(View):
    channel_selection_flags = RefreshFlags.ChannelSelection.value | RefreshFlags.ChannelGroup.value
    mixer_track_selection_flags = RefreshFlags.MixerSelection.value
    CUSTOM_PAGE_CC_START = 4096 + 52  # Custom page CC
    HYBRID_PAGE_CC_KNOBS = [
        {'controlNum': 23, 'midiChan': 11, 'port': 0},
        {'controlNum': 24, 'midiChan': 11, 'port': 0},
    ]
    HYBRID_PAGE_NUM_PARAMS = 6  # First 6 knobs are plugin params, last 2 are CC pass-thru

    def __init__(self, action_dispatcher, fl, plugin_parameters, *, control_to_index, channel_selection_manager=None, model=None):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.plugin_parameters = plugin_parameters
        self.control_to_index = control_to_index
        self.channel_selection_manager = channel_selection_manager
        self.model = model
        self.parameters_for_index = []
        self.deadzone_converters_for_index = []
        self.action_dispatcher = action_dispatcher
        self.reset_pickup_on_first_movement = False
        self.control_change_rate_limiter = ControlChangeRateLimiter(action_dispatcher)
        self.all_parameters = []  # Store all available parameters for current plugin
        self.total_pages = 0
        self.is_custom_page = False  # Track if we're on the custom CC page
        self.is_hybrid_page = False  # Track if we're on the hybrid page

    def _on_show(self):
        self.control_change_rate_limiter.start()
        if self.model:
            self.model.plugin_parameter_active_page = 0
        self._update_plugin_parameters()
        self.reset_pickup_on_first_movement = True

    def _on_hide(self):
        self.control_change_rate_limiter.stop()

    def handle_ChannelSelectAction(self, action):
        # Reset to first page when changing channels
        if self.model:
            self.model.plugin_parameter_active_page = 0
        self._update_plugin_parameters()
        self.reset_pickup_on_first_movement = True

    def handle_PresetChangedAction(self, action):
        # Reset to first page when preset changes
        if self.model:
            self.model.plugin_parameter_active_page = 0
        self._update_plugin_parameters()
        self.reset_pickup_on_first_movement = True

    def handle_PluginParameterPageChangedAction(self, action):
        # Update parameters when page changed externally (e.g., from pad press)
        self._update_plugin_parameters()
        self.reset_pickup_on_first_movement = True

    def handle_OnRefreshAction(self, action):
        if not action.flags & (self.channel_selection_flags | self.mixer_track_selection_flags):
            return

        # When using independent channel selection, check the Launchkey's selected channel
        if self.channel_selection_manager:
            channel = self._get_selected_channel()
            if channel is not None and action.flags & self.channel_selection_flags:
                # Reset to first page when plugin changes
                if self.model:
                    self.model.plugin_parameter_active_page = 0
                # Update when the Launchkey's selected channel changes
                self._update_plugin_parameters()
        else:
            # Legacy behavior: use global FL Studio selection
            selected_plugin_type = self.fl.get_selected_plugin_type()
            if selected_plugin_type == PluginType.Instrument and action.flags & self.channel_selection_flags:
                # Reset to first page when plugin changes
                if self.model:
                    self.model.plugin_parameter_active_page = 0
                self._update_plugin_parameters()
            if selected_plugin_type == PluginType.Effect and action.flags & self.mixer_track_selection_flags:
                # Reset to first page when plugin changes
                if self.model:
                    self.model.plugin_parameter_active_page = 0
                self._update_plugin_parameters()

    def _get_selected_channel(self):
        """Get the selected channel, using channel_selection_manager if available"""
        if self.channel_selection_manager:
            return self.channel_selection_manager.get_active_channel()
        return None

    def _update_plugin_parameters(self):
        self.control_change_rate_limiter.reset()

        # Get plugin name based on channel selection
        if self.channel_selection_manager:
            channel = self._get_selected_channel()
            if channel is not None:
                plugin = self.fl.get_plugin_for_channel(channel)
            else:
                plugin = None
        else:
            plugin = self.fl.get_selected_plugin()

        if plugin in self.plugin_parameters:
            # Store all parameters for pagination
            self.all_parameters = self.plugin_parameters[plugin]

            # Calculate pagination (plugin parameter pages only, not including custom pages)
            num_controls = len(self.control_to_index)
            plugin_pages = (len(self.all_parameters) + num_controls - 1) // num_controls if self.all_parameters else 0
            self.total_pages = plugin_pages + 2  # +1 for hybrid page, +1 for custom page

            # Get current page from model, or use 0 if no model
            current_page = self.model.plugin_parameter_active_page if self.model else 0

            # Ensure current page is valid (including hybrid + custom pages)
            if current_page >= self.total_pages:
                current_page = 0
                if self.model:
                    self.model.plugin_parameter_active_page = 0

            # Check if we're on the hybrid page or custom page
            self.is_custom_page = (current_page == plugin_pages)
            self.is_hybrid_page = (current_page == plugin_pages + 1)

            if self.is_custom_page:
                # Custom page: create placeholder parameters for CC control
                self.parameters_for_index = [None] * num_controls
                self.deadzone_converters_for_index = [None] * num_controls
            elif self.is_hybrid_page:
                # Hybrid page: last 6 params + 2 CC pass-thru knobs
                num_params = self.HYBRID_PAGE_NUM_PARAMS
                last_params = self.all_parameters[-num_params:] if len(self.all_parameters) >= num_params else list(self.all_parameters)
                # Pad to 6 if fewer params available, then add 2 None slots for CC knobs
                while len(last_params) < num_params:
                    last_params.insert(0, None)
                self.parameters_for_index = last_params + [None] * len(self.HYBRID_PAGE_CC_KNOBS)
                self.deadzone_converters_for_index = [None] * len(self.parameters_for_index)
                for index, parameter in enumerate(self.parameters_for_index[:num_params]):
                    if parameter and parameter.deadzone_centre:
                        self.deadzone_converters_for_index[index] = DeadzoneValueConverter(
                            maximum=1.0, centre=parameter.deadzone_centre, width=parameter.deadzone_width
                        )
            else:
                # Regular plugin parameter page
                start_index = current_page * num_controls
                end_index = start_index + num_controls
                parameters = self.all_parameters[start_index:end_index]

                self.parameters_for_index = parameters
                self.deadzone_converters_for_index = [None] * len(self.parameters_for_index)
                for index, parameter in enumerate(self.parameters_for_index):
                    if parameter and parameter.deadzone_centre:
                        self.deadzone_converters_for_index[index] = DeadzoneValueConverter(
                            maximum=1.0, centre=parameter.deadzone_centre, width=parameter.deadzone_width
                        )
        else:
            self.all_parameters = []
            self.parameters_for_index = []
            self.deadzone_converters_for_index = []
            self.total_pages = 0
            self.is_custom_page = False
            self.is_hybrid_page = False

    def handle_ControlChangedAction(self, action):
        index = self.control_to_index.get(action.control)
        if index is None or index >= len(self.parameters_for_index):
            return

        if self.reset_pickup_on_first_movement:
            self.reset_pickup_on_first_movement = False
            if not self.is_custom_page and not self.is_hybrid_page:
                self._reset_pickup()
            elif self.is_hybrid_page:
                self._reset_pickup()  # Reset pickup for the 6 real params on hybrid page

        # If on custom page, send CC message directly
        if self.is_custom_page:
            self._send_custom_cc(index, action.position, action.fl_event)
            return

        # If on hybrid page, route based on knob index
        if self.is_hybrid_page and index >= self.HYBRID_PAGE_NUM_PARAMS:
            self._send_hybrid_cc(index, action.position, action.fl_event)
            return

        parameter = self.parameters_for_index[index]

        if parameter is not None:
            position = action.position
            deadzone = self.deadzone_converters_for_index[index]
            if deadzone:
                position = deadzone(action.position)
            self._update_value_for_plugin_parameter(parameter, action.control, position)

    def _update_value_for_plugin_parameter(self, parameter, control, position):
        if self.control_change_rate_limiter.forward_control_change_event(parameter.index, position):
            # Get the channel to use (if using independent selection)
            # print(f"parameter.parameter_type {parameter.parameter_type}")
            # print(f"parameter {parameter}")
            channel = self._get_selected_channel() if self.channel_selection_manager else None

            if parameter.parameter_type == PluginParameterType.Channel:
                self.fl.channel.set_parameter_value(parameter.index, position, group_channel=channel)
            elif parameter.parameter_type == PluginParameterType.Plugin:
                self.fl.plugin.set_parameter_value(parameter.index, position, group_channel=channel)

            self.action_dispatcher.dispatch(
                PluginParameterValueChangedAction(parameter=parameter, control=control, value=position)
            )

    def _reset_pickup(self):
        # Get the channel to use (if using independent selection)
        channel = self._get_selected_channel() if self.channel_selection_manager else None

        # On hybrid page, only reset pickup for the real param knobs (first 6), not CC knobs
        params_to_reset = self.parameters_for_index[:self.HYBRID_PAGE_NUM_PARAMS] if self.is_hybrid_page else self.parameters_for_index
        for parameter in params_to_reset:
            if parameter is not None and parameter.parameter_type is PluginParameterType.Plugin:
                self.fl.reset_parameter_pickup(parameter.index, group_channel=channel)

    def _send_custom_cc(self, index, position, fl_event=None):
        print(f"fl_event {fl_event.midiChan} {fl_event.controlNum} {fl_event.data1} {fl_event.data2}")
        """Send CC message for custom page (CC 4096+)"""

        """
        Args:
            index: Control index (0-7 for pots)
            position: Normalized position (0.0-1.0)
            fl_event: Original FL event data object (if available)
        """
        # fl_event.handled = False
        # fl_event.midiChan = 0
        # fl_event.controlNum = 52
        # print(f"fl_event {fl_event.midiChan} {fl_event.controlNum} {fl_event.data1} {fl_event.data2}")
        # self.device.processMIDICC(fl_event)
        # return

        channel = self._get_selected_channel() if self.channel_selection_manager else None

        # Calculate CC number (52-59 for the custom page)
        # Calculate CC number (4096 + index)
        cc_number = self.CUSTOM_PAGE_CC_START + index

        # Convert position (0.0-1.0) to MIDI value (0-127)
        midi_value_127 = int(position * 127)


        # Modify the eventData to contain our custom CC message
        fl_event.controlNum = cc_number - 4096  # Convert back to raw CC number (52-59)
        fl_event.controlVal = midi_value_127
        fl_event.midiChan = 0  # Send on channel 1 (0-indexed)

        # Leaving this here as an example, although we dont really need it
        # self.device.processMIDICC(fl_event)

        self.fl.plugin.set_parameter_value(cc_number, position, group_channel=channel)

        self.action_dispatcher.dispatch(
            CustomCcValueChangedAction(
                control=list(self.control_to_index.keys())[index],
                cc_number=fl_event.controlNum,
                midi_channel=fl_event.midiChan,
                port=0,
                value=midi_value_127,
            )
        )

    def _send_hybrid_cc(self, index, position, fl_event=None):
        fl_event.handled = False
        fl_adapter.skip_claiming_handled = True
        return
        """Send CC message for hybrid page pass-thru knobs (knobs 6-7)."""
        if fl_event is None:
            return
        #fl_event2 = fl_event.copy(port=4)
        cc_knob = self.HYBRID_PAGE_CC_KNOBS[index - self.HYBRID_PAGE_NUM_PARAMS]
        fl_event.status = 0xBF
        fl_event.controlNum = 0x1C #cc_knob['controlNum']
        fl_event.controlVal = int(position * 127)
        fl_event.midiChan = 32767 #cc_knob['midiChan']
        #fl_event.port = 4
        fl_event.handled = False
        status = 0xBF  # CC on MIDI channel 1
        device.midiOutMsg(status | (fl_event.controlNum << 8) | (fl_event.controlVal << 16))
        device.processMIDICC(fl_event)
        message = (0xBF | fl_event.midiChan) | (fl_event.controlNum << 8) | (fl_event.controlVal << 16) | (4 << 24)
        device.forwardMIDICC(message, 0)
        device.midiOutMsg(message)
        fl_adapter.skip_claiming_handled = True