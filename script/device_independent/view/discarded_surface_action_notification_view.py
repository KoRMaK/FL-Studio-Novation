from script.action_generators.surface_action_generator.surface_actions import ControlChangedAction
from script.device_independent.util_view import View


class DiscardedSurfaceInteractionNotificationView(View):
    def __init__(self, action_dispatcher, fl, screen_writer):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.screen_writer = screen_writer
        self.controls_moved_while_interaction_suspended = None

    def _on_show(self):
        self.controls_moved_while_interaction_suspended = set()

    def handle_SurfaceInteractionDiscardedAction(self, action):
        if isinstance(action.discarded_action, ControlChangedAction.get_type()):
            self.handle_blocked_control_action(control_index=action.discarded_action.control)
        else:
            self.handle_blocked_other_action()

        self.fl.ui.set_hint_message("FL Studio is busy. Please close dialog first.")

    def handle_DeviceInteractionResumedAction(self, action):
        self.fl.ui.set_hint_message("")
        self.reset_displayed_notification()
        self.reset_displayed_parameters()

    def reset_displayed_notification(self):
        self.screen_writer.display_notification()

    def reset_displayed_parameters(self):
        for control_index in self.controls_moved_while_interaction_suspended:
            self.screen_writer.display_parameter(control_index, name="", value="")
        self.controls_moved_while_interaction_suspended = set()

    def handle_blocked_control_action(self, control_index):
        self.screen_writer.display_parameter(control_index, name="FL Studio is", value="busy :(")
        self.controls_moved_while_interaction_suspended.add(control_index)

    def handle_blocked_other_action(self):
        self.screen_writer.display_notification(primary_text="FL Studio is", secondary_text="busy :(")
