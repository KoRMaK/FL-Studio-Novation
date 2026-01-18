from script.actions import PluginParameterValueChangedAction
from script.constants import PluginParameterType
from script.device_independent.util_view.view import View
from script.device_independent.view.control_change_rate_limiter import ControlChangeRateLimiter
from script.fl_constants import PluginType, RefreshFlags
from util.deadzone_value_converter import DeadzoneValueConverter


class PluginParameterView(View):
    channel_selection_flags = RefreshFlags.ChannelSelection.value | RefreshFlags.ChannelGroup.value
    mixer_track_selection_flags = RefreshFlags.MixerSelection.value

    def __init__(self, action_dispatcher, fl, plugin_parameters, *, control_to_index, channel_selection_manager=None):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.plugin_parameters = plugin_parameters
        self.control_to_index = control_to_index
        self.channel_selection_manager = channel_selection_manager
        self.parameters_for_index = []
        self.deadzone_converters_for_index = []
        self.action_dispatcher = action_dispatcher
        self.reset_pickup_on_first_movement = False
        self.control_change_rate_limiter = ControlChangeRateLimiter(action_dispatcher)

    def _on_show(self):
        self.control_change_rate_limiter.start()
        self._update_plugin_parameters()
        self.reset_pickup_on_first_movement = True

    def _on_hide(self):
        self.control_change_rate_limiter.stop()

    def handle_ChannelSelectAction(self, action):
        self._update_plugin_parameters()
        self.reset_pickup_on_first_movement = True

    def handle_PresetChangedAction(self, action):
        self.reset_pickup_on_first_movement = True

    def handle_OnRefreshAction(self, action):
        if not action.flags & (self.channel_selection_flags | self.mixer_track_selection_flags):
            return

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
            parameters = self.plugin_parameters[plugin]
            self.parameters_for_index = parameters[: len(self.control_to_index)]
            self.deadzone_converters_for_index = [None] * len(self.parameters_for_index)
            for index, parameter in enumerate(self.parameters_for_index):
                if parameter and parameter.deadzone_centre:
                    self.deadzone_converters_for_index[index] = DeadzoneValueConverter(
                        maximum=1.0, centre=parameter.deadzone_centre, width=parameter.deadzone_width
                    )
        else:
            self.parameters_for_index = []
            self.deadzone_converters_for_index = []

    def handle_ControlChangedAction(self, action):
        index = self.control_to_index.get(action.control)
        if index is None or index >= len(self.parameters_for_index):
            return

        if self.reset_pickup_on_first_movement:
            self.reset_pickup_on_first_movement = False
            self._reset_pickup()

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

        for parameter in self.parameters_for_index:
            if parameter is not None and parameter.parameter_type is PluginParameterType.Plugin:
                self.fl.reset_parameter_pickup(parameter.index, group_channel=channel)
