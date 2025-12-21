from script.action_generators.surface_action_generator.surface_actions import SurfaceInteractionDiscardedAction


class SurfaceActionGeneratorWrapper:
    def __init__(self, action_dispatcher, action_generator):
        self.action_dispatcher = action_dispatcher
        self.action_generator = action_generator
        self._suspended_action_types = ()

    def handle_midi_event(self, fl_event):
        actions = self.action_generator.handle_midi_event(fl_event)
        if actions:
            for action in actions:
                self.dispatch(action)

    def dispatch(self, action):
        if self._suspended_action_types and isinstance(action, self._suspended_action_types):
            self.action_dispatcher.dispatch(SurfaceInteractionDiscardedAction(discarded_action=action))
            return

        self.action_dispatcher.dispatch(action)

    def set_suspended_actions(self, actions):
        self._suspended_action_types = tuple(action.get_type() for action in actions)
