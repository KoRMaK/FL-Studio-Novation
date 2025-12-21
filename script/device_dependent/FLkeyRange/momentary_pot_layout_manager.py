from script.constants import Pots
from script.device_independent.view import SequencerStepEditView


class MomentaryPotLayoutManager:
    def __init__(self, action_dispatcher, fl, model):
        control_to_index = {
            Pots.FirstControlIndex.value + control: index for index, control in enumerate(range(Pots.Num.value))
        }
        self.views = [SequencerStepEditView(action_dispatcher, fl, model, control_to_index=control_to_index)]

    def show(self):
        for view in self.views:
            view.show()

    def hide(self):
        for view in self.views:
            view.hide()

    def focus_windows(self):
        pass
