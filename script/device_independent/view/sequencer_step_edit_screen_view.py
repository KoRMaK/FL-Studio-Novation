from script.constants import StepEditParameters
from script.device_independent.util_view import View


class SequencerStepEditScreenView(View):
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    notes_per_octave = 12
    percentage_max = 100
    cents_max = 1200

    def __init__(self, action_dispatcher, screen_writer, fl):
        super().__init__(action_dispatcher)
        self.screen_writer = screen_writer
        self.fl = fl
        self.name_for_parameter = {
            StepEditParameters.Pitch.value: "Note pitch",
            StepEditParameters.Velocity.value: "Velocity",
            StepEditParameters.Release.value: "Release",
            StepEditParameters.PitchFine.value: "Fine pitch",
            StepEditParameters.Pan.value: "Panning",
            StepEditParameters.ModX.value: "Mod X",
            StepEditParameters.ModY.value: "Mod Y",
            StepEditParameters.Shift.value: "Shift",
        }

    def handle_SequencerStepEditParameterChangedAction(self, action):
        name = self.name_for_parameter[action.parameter]
        value_string = self._calculate_value_string_for_parameter(action.value, action.parameter)
        self.screen_writer.display_parameter(action.control, name=name, value=value_string)

    def _calculate_value_string_for_parameter(self, value, parameter):
        if parameter == StepEditParameters.Pitch.value:
            octave = value // self.notes_per_octave
            note = self.note_names[value % self.notes_per_octave]
            return f"{note}{octave}"

        normalized_value = self._calculate_normalized_value(value, parameter)

        if (
            parameter == StepEditParameters.Velocity.value
            or parameter == StepEditParameters.Release.value
            or parameter == StepEditParameters.ModX.value
            or parameter == StepEditParameters.ModY.value
        ):
            return f'{format(normalized_value * self.percentage_max, ".0f")}%'

        if parameter == StepEditParameters.PitchFine.value:
            return f'{format(normalized_value * self.cents_max, ".0f")} cents'
        if parameter == StepEditParameters.Pan.value:
            if abs(normalized_value) < 1e-6:
                return "C"
            if normalized_value < 0:
                return f'{format(abs(normalized_value) * self.percentage_max, ".0f")}L'
            return f'{format(abs(normalized_value) * self.percentage_max, ".0f")}R'
        if parameter == StepEditParameters.Shift.value:
            return f'{format(normalized_value, ".2f")}'
        return None

    def _calculate_normalized_value(self, value, parameter):
        normalized_value = (value - parameter.minimum) / parameter.maximum
        if parameter.is_bipolar:
            return normalized_value * 2 - 1
        return normalized_value
