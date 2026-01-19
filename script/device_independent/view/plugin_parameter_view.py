from script.actions import PluginParameterValueChangedAction, PluginParameterPageChangedAction
from script.constants import PluginParameterType
from script.device_independent.util_view.view import View
from script.device_independent.view.control_change_rate_limiter import ControlChangeRateLimiter
from script.fl_constants import PluginType, RefreshFlags
from util.deadzone_value_converter import DeadzoneValueConverter


class PluginParameterView(View):
    channel_selection_flags = RefreshFlags.ChannelSelection.value | RefreshFlags.ChannelGroup.value
    mixer_track_selection_flags = RefreshFlags.MixerSelection.value

    def __init__(self, action_dispatcher, fl, plugin_parameters, *, control_to_index, channel_selection_manager=None, model=None, product_defs=None, button_led_writer=None):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.plugin_parameters = plugin_parameters
        self.control_to_index = control_to_index
        self.channel_selection_manager = channel_selection_manager
        self.model = model
        self.product_defs = product_defs
        self.button_led_writer = button_led_writer
        self.parameters_for_index = []
        self.deadzone_converters_for_index = []
        self.action_dispatcher = action_dispatcher
        self.reset_pickup_on_first_movement = False
        self.control_change_rate_limiter = ControlChangeRateLimiter(action_dispatcher)
        self.all_parameters = []  # Store all available parameters for current plugin
        self.total_pages = 0

    def _on_show(self):
        self.control_change_rate_limiter.start()
        if self.model:
            self.model.plugin_parameter_active_page = 0
        self._update_plugin_parameters()
        self.reset_pickup_on_first_movement = True
        self._update_page_button_leds()

    def _on_hide(self):
        self.control_change_rate_limiter.stop()
        self._turn_off_page_button_leds()

    def handle_ChannelSelectAction(self, action):
        # Reset to first page when changing channels
        if self.model:
            self.model.plugin_parameter_active_page = 0
        self._update_plugin_parameters()
        self.reset_pickup_on_first_movement = True
        self._update_page_button_leds()

    def handle_PresetChangedAction(self, action):
        # Reset to first page when preset changes
        if self.model:
            self.model.plugin_parameter_active_page = 0
        self._update_plugin_parameters()
        self.reset_pickup_on_first_movement = True
        self._update_page_button_leds()

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
                self._update_page_button_leds()
        else:
            # Legacy behavior: use global FL Studio selection
            selected_plugin_type = self.fl.get_selected_plugin_type()
            if selected_plugin_type == PluginType.Instrument and action.flags & self.channel_selection_flags:
                # Reset to first page when plugin changes
                if self.model:
                    self.model.plugin_parameter_active_page = 0
                self._update_plugin_parameters()
                self._update_page_button_leds()
            if selected_plugin_type == PluginType.Effect and action.flags & self.mixer_track_selection_flags:
                # Reset to first page when plugin changes
                if self.model:
                    self.model.plugin_parameter_active_page = 0
                self._update_plugin_parameters()
                self._update_page_button_leds()

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

            # Calculate pagination
            num_controls = len(self.control_to_index)
            self.total_pages = (len(self.all_parameters) + num_controls - 1) // num_controls if self.all_parameters else 0

            # Get current page from model, or use 0 if no model
            current_page = self.model.plugin_parameter_active_page if self.model else 0

            # Ensure current page is valid
            if current_page >= self.total_pages:
                current_page = 0
                if self.model:
                    self.model.plugin_parameter_active_page = 0

            # Slice parameters for current page
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

    def handle_ButtonPressedAction(self, action):
        if not self.product_defs or not self.model:
            return

        # Handle page navigation with mixer bank buttons
        if action.button == self.product_defs.FunctionToButton.get("MixerBankLeft"):
            self._navigate_to_previous_page()
        elif action.button == self.product_defs.FunctionToButton.get("MixerBankRight"):
            self._navigate_to_next_page()

    def _navigate_to_previous_page(self):
        if not self.model or self.model.plugin_parameter_active_page <= 0:
            return

        self.model.plugin_parameter_active_page -= 1
        self._update_plugin_parameters()
        self.reset_pickup_on_first_movement = True
        self._update_page_button_leds()
        self.action_dispatcher.dispatch(PluginParameterPageChangedAction())

    def _navigate_to_next_page(self):
        if not self.model or self.model.plugin_parameter_active_page >= self.total_pages - 1:
            return

        self.model.plugin_parameter_active_page += 1
        self._update_plugin_parameters()
        self.reset_pickup_on_first_movement = True
        self._update_page_button_leds()
        self.action_dispatcher.dispatch(PluginParameterPageChangedAction())

    def _update_page_button_leds(self):
        """Update mixer bank button LEDs to indicate page availability"""
        if not self.button_led_writer or not self.product_defs or not self.model:
            return

        from script.colours import Colours

        # Previous page button (left)
        prev_available = self.model.plugin_parameter_active_page > 0
        prev_colour = Colours.available if prev_available else Colours.off
        self.button_led_writer.set_button_colour(
            self.product_defs.FunctionToButton.get("MixerBankLeft"), prev_colour
        )

        # Next page button (right)
        next_available = self.model.plugin_parameter_active_page < self.total_pages - 1
        next_colour = Colours.available if next_available else Colours.off
        self.button_led_writer.set_button_colour(
            self.product_defs.FunctionToButton.get("MixerBankRight"), next_colour
        )

    def _turn_off_page_button_leds(self):
        """Turn off mixer bank button LEDs"""
        if not self.button_led_writer or not self.product_defs:
            return

        from script.colours import Colours

        self.button_led_writer.set_button_colour(
            self.product_defs.FunctionToButton.get("MixerBankLeft"), Colours.off
        )
        self.button_led_writer.set_button_colour(
            self.product_defs.FunctionToButton.get("MixerBankRight"), Colours.off
        )
