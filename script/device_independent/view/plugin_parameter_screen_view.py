from math import isclose

from script.constants import PluginParameterType
from script.device_independent.util_view.view import View
from script.fl_constants import PluginType, RefreshFlags


class PluginParameterScreenView(View):
    channel_selection_flags = RefreshFlags.ChannelSelection.value | RefreshFlags.ChannelGroup.value
    mixer_track_selection_flags = RefreshFlags.MixerSelection.value

    def __init__(self, action_dispatcher, fl, screen_writer, plugin_parameters, *, control_to_index):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.screen_writer = screen_writer
        self.plugin_parameters = plugin_parameters
        self.control_to_index = control_to_index

    def _on_show(self):
        self._update_plugin_parameters()

    def _on_hide(self):
        self._set_primary_text_for_all_controls("")

    def handle_OnRefreshAction(self, action):
        if not action.flags & (self.channel_selection_flags | self.mixer_track_selection_flags):
            return

        selected_plugin_type = self.fl.get_selected_plugin_type()
        if selected_plugin_type == PluginType.Instrument and action.flags & self.channel_selection_flags:
            self._update_plugin_parameters()
        if selected_plugin_type == PluginType.Effect and action.flags & self.mixer_track_selection_flags:
            self._update_plugin_parameters()

    def _update_plugin_parameters(self):
        plugin_parameters = self.plugin_parameters.get(self.fl.get_selected_plugin())
        if plugin_parameters is None:
            self._set_primary_text_for_all_controls("Not Used")
        else:
            for control, index in self.control_to_index.items():
                if index >= len(plugin_parameters) or plugin_parameters[index] is None:
                    self._set_primary_text_for_control(control, "Not Used")

    def _set_primary_text_for_control(self, control, text):
        self.screen_writer.display_parameter(control, name=text, value="")

    def _set_primary_text_for_all_controls(self, text):
        for control, _ in self.control_to_index.items():
            self._set_primary_text_for_control(control, text)

    def _get_parameter_name_and_value(self, parameter, action_value):
        if parameter is None:
            return "Not Used", "-"

        name = self.fl.get_parameter_name(parameter.index) if parameter.name is None else parameter.name

        if parameter.discrete_regions:
            value = self._get_region_name_for_value(parameter.discrete_regions, action_value)
        elif parameter.parameter_type is PluginParameterType.Channel:
            minimum, maximum = (0, 100) if parameter.deadzone_centre is None else (-100, 100)
            value = self._normalised_value_to_percentage_string(action_value, minimum=minimum, maximum=maximum)
        else:
            value = self.fl.get_parameter_value_as_string(
                parameter.index
            ) or self._normalised_value_to_percentage_string(self.fl.get_parameter_value(parameter.index))

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
