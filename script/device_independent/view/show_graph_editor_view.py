from script.constants import Pads, SequencerStepEditState, StepEditParameters
from script.device_independent.util_view.view import View


class ShowGraphEditorView(View):
    def __init__(self, action_dispatcher, model, fl):
        super().__init__(action_dispatcher)
        self.model = model
        self.fl = fl
        self.most_recent_show_graph_editor_args = None
        self.showing_graph_editor = False

    def _on_hide(self):
        if self.showing_graph_editor:
            self._hide_graph_editor()

    def handle_SequencerStepEditStateChangedAction(self, action):
        if (
            self.model.sequencer.step_edit_state == SequencerStepEditState.EditLatch
            or self.model.sequencer.step_edit_state == SequencerStepEditState.EditQuick
        ):
            self._show_graph_editor(
                self.model.sequencer.step_edit_group.get_steps(),
                self.model.sequencer.step_edit_group.displayed_step_edit_parameter,
            )
        elif self.model.sequencer.step_edit_state == SequencerStepEditState.EditIdle:
            self._hide_graph_editor()

    def handle_SequencerStepEditParameterChangedAction(self, action):
        if self.showing_graph_editor:
            self._show_graph_editor(
                self.model.sequencer.step_edit_group.get_steps(),
                self.model.sequencer.step_edit_group.displayed_step_edit_parameter,
            )

    def handle_SequencerStepEditGroupChangedAction(self, action):
        if self.showing_graph_editor:
            self._show_graph_editor(
                self.model.sequencer.step_edit_group.get_steps(),
                self.model.sequencer.step_edit_group.displayed_step_edit_parameter,
            )

    def handle_SequencerPageChangedAction(self, action):
        if self.showing_graph_editor:
            self._show_graph_editor(
                self.model.sequencer.step_edit_group.get_steps(),
                self.model.sequencer.step_edit_group.displayed_step_edit_parameter,
            )

    def _show_graph_editor(self, steps, parameter_index):
        self.showing_graph_editor = True
        args = steps, parameter_index
        if args == self.most_recent_show_graph_editor_args and parameter_index != StepEditParameters.Pitch.value.index:
            # Return early if we're already showing the graph editor for this parameter and step.
            # However, the graph editor should scroll with the edited pitch so we should call
            # show_graph_editor every time for the pitch parameter.
            return

        first_step_in_current_page = self.model.sequencer_active_page * Pads.Num.value
        last_step_in_current_page = first_step_in_current_page + Pads.Num.value - 1

        steps_on_current_page = list(
            filter(lambda step: first_step_in_current_page <= step <= last_step_in_current_page, steps)
        )

        first_step_to_focus = min(steps_on_current_page) if steps_on_current_page else first_step_in_current_page

        self.fl.show_graph_editor(first_step_to_focus, parameter_index)
        self.most_recent_show_graph_editor_args = args

    def _hide_graph_editor(self):
        self.showing_graph_editor = False
        self.fl.hide_graph_editor()
        self.most_recent_show_graph_editor_args = None
