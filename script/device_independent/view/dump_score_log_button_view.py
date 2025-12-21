from script.actions import FunctionTriggeredAction
from script.constants import ButtonFunction
from script.device_independent.util_view.view import View


class DumpScoreLogButtonView(View):
    default_dump_score_log_duration_in_minutes = 5
    default_dump_score_log_duration_in_seconds = default_dump_score_log_duration_in_minutes * 60

    def __init__(self, action_dispatcher, fl, product_defs):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.product_defs = product_defs

    def handle_ButtonPressedAction(self, action):
        if action.button == self.product_defs.FunctionToButton.get("DumpScoreLog"):
            self.fl.dump_score_log(self.default_dump_score_log_duration_in_seconds)
            self.action_dispatcher.dispatch(FunctionTriggeredAction(function=ButtonFunction.DumpScoreLog))
