from script.constants import PatternSelectionMethod
from script.device_independent.util_view import View


class PatternSelectScreenView(View):
    def __init__(self, action_dispatcher, fl, screen_writer):
        super().__init__(action_dispatcher)
        self.fl = fl
        self.screen_writer = screen_writer

    def handle_PatternSelectedAction(self, action):
        if action.method is PatternSelectionMethod.ThroughNew:
            self.screen_writer.display_notification(primary_text="New Pattern")
        elif action.method is PatternSelectionMethod.ThroughClone:
            self.screen_writer.display_notification(primary_text="Clone Pattern")
        elif action.method is PatternSelectionMethod.Explicit:
            index = self.fl.get_selected_pattern_index()
            name = self.fl.get_pattern_name(index)
            self.screen_writer.display_notification(primary_text="Pattern", secondary_text=name)
