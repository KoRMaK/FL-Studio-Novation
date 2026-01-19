from math import isclose

from script.constants import PluginParameterType
from script.device_independent.util_view.view import View
from script.fl_constants import PluginType, RefreshFlags


class PluginParameterScreenView(View):
    channel_selection_flags = RefreshFlags.ChannelSelection.value | RefreshFlags.ChannelGroup.value
    mixer_track_selection_flags = RefreshFlags.MixerSelection.value

    def __init__(self, action_dispatcher, fl, screen_writer, plugin_parameters, *, control_to_index, channel_selection_manager=None, model=None):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.screen_writer = screen_writer
        self.plugin_parameters = plugin_parameters
        self.control_to_index = control_to_index
        self.channel_selection_manager = channel_selection_manager
        self.model = model
        self.all_parameters = []  # Store all available parameters for current plugin

    def _on_show(self):
        self._update_plugin_parameters()

    def _on_hide(self):
        self._set_primary_text_for_all_controls("")

    def handle_ChannelSelectAction(self, action):
        self._update_plugin_parameters()

    def handle_PluginParameterPageChangedAction(self, action):
        self._update_plugin_parameters()

    def handle_PresetChangedAction(self, action):
        self._update_plugin_parameters()

    def handle_OnRefreshAction(self, action):
        if not action.flags & (self.channel_selection_flags | self.mixer_track_selection_flags):
            return

        # When using independent channel selection, check the Launchkey's selected channel
        if self.channel_selection_manager:
            channel = self._get_selected_channel()
            if channel is not None and action.flags & self.channel_selection_flags:
                # Update when the Launchkey's selected channel changes
                self._update_plugin_parameters()
        else:
            # Legacy behavior: use global FL Studio selection
            selected_plugin_type = self.fl.get_selected_plugin_type()
            if selected_plugin_type == PluginType.Instrument and action.flags & self.channel_selection_flags:
                self._update_plugin_parameters()
            if selected_plugin_type == PluginType.Effect and action.flags & self.mixer_track_selection_flags:
                self._update_plugin_parameters()

    def _get_selected_channel(self):
        """Get the selected channel, using channel_selection_manager if available"""
        if self.channel_selection_manager:
            return self.channel_selection_manager.get_active_channel()
        return None

    def _update_plugin_parameters(self):
        # Get plugin name based on channel selection
        if self.channel_selection_manager:
            channel = self._get_selected_channel()
            if channel is not None:
                plugin = self.fl.get_plugin_for_channel(channel)
            else:
                plugin = None
        else:
            plugin = self.fl.get_selected_plugin()

        plugin_parameters = self.plugin_parameters.get(plugin)
        if plugin_parameters is None:
            self.all_parameters = []
            self._set_primary_text_for_all_controls("Not Used")
        else:
            # Store all parameters for pagination
            self.all_parameters = plugin_parameters

            # Calculate pagination
            num_controls = len(self.control_to_index)
            current_page = self.model.plugin_parameter_active_page if self.model else 0

            # Slice parameters for current page
            start_index = current_page * num_controls
            end_index = start_index + num_controls

            for control, index in self.control_to_index.items():
                # Map control index to paginated parameter index
                paginated_index = start_index + index
                if paginated_index >= len(plugin_parameters) or plugin_parameters[paginated_index] is None:
                    self._set_primary_text_for_control(control, "Not Used")

    def _set_primary_text_for_control(self, control, text):
        self.screen_writer.display_parameter(control, name=text, value="")

    def _set_primary_text_for_all_controls(self, text):
        for control, _ in self.control_to_index.items():
            self._set_primary_text_for_control(control, text)

    def _get_parameter_name_and_value(self, parameter, action_value):
        if parameter is None:
            return "Not Used", "-"

        # Get the channel to use (if using independent selection)
        channel = self._get_selected_channel() if self.channel_selection_manager else None

        name = self.fl.get_parameter_name(parameter.index, group_channel=channel) if parameter.name is None else parameter.name

        if parameter.discrete_regions:
            value = self._get_region_name_for_value(parameter.discrete_regions, action_value)
        elif parameter.parameter_type is PluginParameterType.Channel:
            minimum, maximum = (0, 100) if parameter.deadzone_centre is None else (-100, 100)
            value = self._normalised_value_to_percentage_string(action_value, minimum=minimum, maximum=maximum)
        else:
            value = self.fl.get_parameter_value_as_string(
                parameter.index, group_channel=channel
            ) or self._normalised_value_to_percentage_string(self.fl.get_parameter_value(parameter.index, group_channel=channel))

        return name, value

    def handle_PluginParameterValueChangedAction(self, action):
        name, value = self._get_parameter_name_and_value(action.parameter, action.value)
        self.screen_writer.display_parameter(action.control, name=name, value=value)

    def _get_region_name_for_value(self, discrete_regions, value):
        for lower_boundary, name in reversed(discrete_regions):
            if isclose(lower_boundary, value, abs_tol=1e-6) or lower_boundary < value:
                return name
        return ""

    def _normalised_value_to_percentage_string(self, normalised_value, *, minimum=0, maximum=100, num_decimals=0):
        value = (maximum - minimum) * normalised_value + minimum
        return f'{format(value, f".{num_decimals}f")}%'
