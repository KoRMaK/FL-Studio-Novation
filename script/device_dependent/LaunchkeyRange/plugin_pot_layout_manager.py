from script.commands import RequestDisableMixerBankingCommand, RequestEnableMixerBankingCommand
from script.constants import Pots
from script.device_independent.view import PluginParameterScreenView, PluginParameterView
from script.plugin import plugin_parameter_mappings


class PluginPotLayoutManager:
    def __init__(self, action_dispatcher, fl, screen_writer, channel_selection_manager=None, model=None, product_defs=None, button_led_writer=None, command_dispatcher=None):
        control_to_index = {
            Pots.FirstControlIndex.value + control: index for index, control in enumerate(range(Pots.Num.value))
        }
        self.command_dispatcher = command_dispatcher
        self.views = {
            PluginParameterView(
                action_dispatcher,
                fl,
                plugin_parameter_mappings,
                control_to_index=control_to_index,
                channel_selection_manager=channel_selection_manager,
                model=model,
                product_defs=product_defs,
                button_led_writer=button_led_writer
            ),
            PluginParameterScreenView(
                action_dispatcher,
                fl,
                screen_writer,
                plugin_parameter_mappings,
                control_to_index=control_to_index,
                channel_selection_manager=channel_selection_manager,
                model=model
            ),
        }

    def show(self):
        # Disable mixer banking so the mixer bank buttons can be used for parameter pagination
        if self.command_dispatcher:
            self.command_dispatcher.dispatch(RequestDisableMixerBankingCommand())

        for view in self.views:
            view.show()

    def hide(self):
        for view in self.views:
            view.hide()

        # Re-enable mixer banking for the next pot mode (Volume/Pan)
        if self.command_dispatcher:
            self.command_dispatcher.dispatch(RequestEnableMixerBankingCommand())

    def focus_windows(self):
        pass
