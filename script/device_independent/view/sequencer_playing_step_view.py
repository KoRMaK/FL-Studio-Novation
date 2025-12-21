from script.device_independent.util_view.view import View


class SequencerPlayingStepView(View):
    def __init__(self, action_dispatcher, model, view):
        super().__init__(action_dispatcher)
        self.model = model
        self.view = view

    def handle_PlayingStepChangedAction(self, action):
        old_playing_step = self.model.sequencer.playing_step
        self.model.sequencer.playing_step = action.step
        self.view.redraw(steps=[old_playing_step, self.model.sequencer.playing_step])
