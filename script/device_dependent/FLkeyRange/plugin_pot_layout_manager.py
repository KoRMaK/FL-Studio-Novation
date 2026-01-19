from script.constants import Pots
from script.device_independent.view import PluginParameterScreenView, PluginParameterView
from script.plugin import plugin_parameter_mappings


class PluginPotLayoutManager:
    def __init__(self, action_dispatcher, fl, screen_writer, model=None, product_defs=None, button_led_writer=None):
        control_to_index = {
            Pots.FirstControlIndex.value + control: index for index, control in enumerate(range(Pots.Num.value))
        }
        self.views = {
            PluginParameterView(
                action_dispatcher,
                fl,
                plugin_parameter_mappings,
                control_to_index=control_to_index,
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
                model=model
            ),
        }

    def show(self):
        for view in self.views:
            view.show()

    def hide(self):
        for view in self.views:
            view.hide()

    def focus_windows(self):
        pass
