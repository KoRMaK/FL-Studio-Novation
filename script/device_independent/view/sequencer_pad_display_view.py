from script.colour_utils import clamp_brightness
from script.colours import Colours
from script.constants import Pads, SequencerStepEditState, StepEditParameters
from script.device_independent.util_view.view import View


class SequencerPadDisplayView(View):
    num_steps_per_page = Pads.Num.value
    min_channel_colour_brightness = 100

    colour_for_step_edit_parameter_index = {
        StepEditParameters.Pitch.value.index: [
            Colours.step_pitch_step_latched,
            Colours.step_pitch_step_on,
            Colours.step_pitch_step_off,
        ],
        StepEditParameters.Velocity.value.index: [
            Colours.step_velocity_step_latched,
            Colours.step_velocity_step_on,
            Colours.step_velocity_step_off,
        ],
        StepEditParameters.Release.value.index: [
            Colours.step_release_step_latched,
            Colours.step_release_step_on,
            Colours.step_release_step_off,
        ],
        StepEditParameters.PitchFine.value.index: [
            Colours.step_pitch_fine_step_latched,
            Colours.step_pitch_fine_step_on,
            Colours.step_pitch_fine_step_off,
        ],
        StepEditParameters.Pan.value.index: [
            Colours.step_pan_step_latched,
            Colours.step_pan_step_on,
            Colours.step_pan_step_off,
        ],
        StepEditParameters.ModX.value.index: [
            Colours.step_mod_x_step_latched,
            Colours.step_mod_x_step_on,
            Colours.step_mod_x_step_off,
        ],
        StepEditParameters.ModY.value.index: [
            Colours.step_mod_y_step_latched,
            Colours.step_mod_y_step_on,
            Colours.step_mod_y_step_off,
        ],
        StepEditParameters.Shift.value.index: [
            Colours.step_shift_step_latched,
            Colours.step_shift_step_on,
            Colours.step_shift_step_off,
        ],
    }

    def __init__(self, action_dispatcher, pad_led_writer, fl, model):
        super().__init__(action_dispatcher)
        self.pad_led_writer = pad_led_writer
        self.fl = fl
        self.model = model

    def redraw(self, *, steps=None):
        if steps is None:
            steps = range(self._step_for_pad(0), self._step_for_pad(Pads.Num.value))
        elif isinstance(steps, int):
            steps = [steps]

        for step in steps:
            self._update_led_for_step(step)

    def _on_show(self):
        self._update_all_leds()

    def _on_hide(self):
        self._turn_off_leds()

    def _step_for_pad(self, pad):
        return self.model.sequencer_active_page * self.num_steps_per_page + pad

    def _pad_for_step(self, step):
        pad = step - (self.model.sequencer_active_page * self.num_steps_per_page)
        if 0 <= pad < self.num_steps_per_page:
            return pad
        return None

    def _channel_colour(self):
        return clamp_brightness(self.fl.get_channel_colour(), minimum=self.min_channel_colour_brightness)

    def _dim_channel_colour(self):
        return tuple(component // 4 for component in self._channel_colour())

    def _bright_channel_colour(self):
        return self._channel_colour()

    def _colour_for_step_in_step_edit_latch_mode(self, step):
        parameter_index = self.model.sequencer.step_edit_group.displayed_step_edit_parameter
        if step in self.model.sequencer.step_edit_group.get_steps():
            return self.colour_for_step_edit_parameter_index[parameter_index][0]
        if self.fl.get_step_active(step):
            return self.colour_for_step_edit_parameter_index[parameter_index][1]
        return self.colour_for_step_edit_parameter_index[parameter_index][2]

    def _colour_for_pad(self, pad):
        step = self._step_for_pad(pad)

        if not self.fl.is_any_channel_selected():
            return Colours.off

        if self.model.sequencer.step_edit_state == SequencerStepEditState.EditLatch:
            return self._colour_for_step_in_step_edit_latch_mode(step)

        if step == self.model.sequencer.playing_step:
            return Colours.pad_pressed.value
        if self.model.sequencer.step_edit_group.edited and step in self.model.sequencer.step_edit_group.get_steps():
            parameter_index = self.model.sequencer.step_edit_group.displayed_step_edit_parameter
            return self.colour_for_step_edit_parameter_index[parameter_index][0]
        if step in self.model.sequencer.held_steps:
            return Colours.pad_pressed.value
        if self.fl.get_step_active(step):
            return self._bright_channel_colour()
        return self._dim_channel_colour()

    def _update_led_for_step(self, step):
        if step is not None:
            pad = self._pad_for_step(step)
            if pad is not None:
                self._update_led_for_pad(pad)

    def _update_led_for_pad(self, pad):
        colour = self._colour_for_pad(pad)
        self.pad_led_writer.set_pad_colour(pad, colour)

    def _update_all_leds(self):
        for pad in range(Pads.Num.value):
            self._update_led_for_pad(pad)

    def _turn_off_leds(self):
        for pad in range(Pads.Num.value):
            self.pad_led_writer.set_pad_colour(pad, Colours.off)
