from script.constants import Faders
from script.device_independent.view import PluginParameterScreenView, PluginParameterView
from script.plugin import plugin_parameter_mappings


class PluginFaderLayoutManager:
    def __init__(self, action_dispatcher, fl, screen_writer):
        control_to_index = {
            Faders.FirstControlIndex.value + control: index
            for index, control in enumerate(range(Faders.NumRegularFaders.value))
        }
        self.views = {
            PluginParameterView(action_dispatcher, fl, plugin_parameter_mappings, control_to_index=control_to_index),
            PluginParameterScreenView(
                action_dispatcher, fl, screen_writer, plugin_parameter_mappings, control_to_index=control_to_index
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
