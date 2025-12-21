from script.actions import SequencerStepEditParameterChangeAttemptedAction, SequencerStepEditParameterChangedAction
from script.constants import StepEditParameters
from script.device_independent.util_view.view import View
from script.fl_constants import UndoType
from util.deadzone_value_converter import DeadzoneValueConverter
from util.timer import Timer


class SequencerStepEditView(View):
    timer_events_between_stored_undo_states = 12

    def __init__(self, action_dispatcher, fl, model, *, control_to_index):
        super().__init__(action_dispatcher)
        self.action_dispatcher = action_dispatcher
        self.fl = fl
        self.model = model
        self.control_to_index = control_to_index
        self.parameter_for_index = {
            0: StepEditParameters.Pitch.value,
            1: StepEditParameters.Velocity.value,
            2: StepEditParameters.Release.value,
            3: StepEditParameters.PitchFine.value,
            4: StepEditParameters.Pan.value,
            5: StepEditParameters.ModX.value,
            6: StepEditParameters.ModY.value,
            7: StepEditParameters.Shift.value,
        }
        self.deadzone_value_converter = DeadzoneValueConverter(maximum=1.0, centre=0.5, width=0.10)
        self.value_offset_per_step_for_shift_parameter = self.fl.get_recording_pulses_per_second()
        self.most_recent_parameter_with_undo_state_stored = None
        self.undo_timer = Timer(action_dispatcher)

    def handle_ControlChangedAction(self, action):
        index = self.control_to_index.get(action.control)
        parameter = self.parameter_for_index.get(index)
        if parameter is None:
            return

        editable_steps = self._get_editable_steps()
        if editable_steps:
            value = self._calculate_value_for_parameter(parameter, action.position)
            if self._new_value_requires_step_update(editable_steps, parameter, value):
                self._set_step_parameter_for_steps(editable_steps, parameter, value)
                self.action_dispatcher.dispatch(
                    SequencerStepEditParameterChangedAction(control=action.control, parameter=parameter, value=value)
                )
        self.action_dispatcher.dispatch(SequencerStepEditParameterChangeAttemptedAction(parameter=parameter))

    def _calculate_value_for_parameter(self, parameter, normalized_value):
        value = normalized_value
        if parameter.is_bipolar:
            value = self.deadzone_value_converter(value)
        return round(value * (parameter.maximum - parameter.minimum) + parameter.minimum)

    def _get_editable_steps(self):
        return self.model.sequencer.step_edit_group.get_steps()

    def _new_value_requires_step_update(self, editable_steps, parameter, value):
        return any(value != self.fl.get_step_parameter(step, parameter.index) for step in editable_steps)

    def _set_step_parameter_for_steps(self, steps, parameter, value):
        self._store_undo_state_for_parameter(parameter)
        for step in steps[:-1]:
            self._set_step_parameter(step, parameter, value, updateGraphEditor=False)
        self._set_step_parameter(steps[-1], parameter, value, updateGraphEditor=True)
        self.most_recently_edited_parameter = parameter

    def _set_step_parameter(self, step, parameter, value, *, updateGraphEditor=True):
        if parameter.index == StepEditParameters.Shift.value.index:
            value = value + self.value_offset_per_step_for_shift_parameter * step
        self.fl.set_step_parameter(step, parameter.index, value, updateGraphEditor=updateGraphEditor)

    def _store_undo_state_for_parameter(self, parameter):
        if self.undo_timer.finished() or self.most_recent_parameter_with_undo_state_stored != parameter:
            self.fl.store_current_state_in_undo_history(UndoType.PianoRoll.value, "Graph editor change")
            self.most_recent_parameter_with_undo_state_stored = parameter
        self.undo_timer.start(self.timer_events_between_stored_undo_states)
