from script.colour_utils import scale_colour
from util.enum import Enum


class Colours(Enum):
    off = 0
    available = 1
    button_pressed = 3
    button_toggle_on = 3
    channel_rack_pad_selected = 3
    channel_rack_pad_pressed = 21
    fpc_orange = 108
    fpc_blue = 38
    fruity_slicer_purple = 86, 84, 255
    instrument_pad_pressed = 3
    pad_pressed = 255, 255, 255
    slicex_pink = 56
    exit_step_edit_latch_mode = 3
    mixer_track_audible = 25
    mixer_track_suspended = 27
    pattern_selected = 3
    step_pitch_step_latched = scale_colour((211, 255, 151), 1.0)
    step_pitch_step_on = scale_colour((175, 225, 120), 0.30)
    step_pitch_step_off = scale_colour((175, 225, 120), 0.05)
    step_velocity_step_latched = scale_colour((106, 233, 255), 1.0)
    step_velocity_step_on = scale_colour((114, 173, 207), 0.35)
    step_velocity_step_off = scale_colour((8, 108, 157), 0.05)
    step_release_step_latched = scale_colour((98, 255, 181), 1.0)
    step_release_step_on = scale_colour((48, 201, 118), 0.35)
    step_release_step_off = scale_colour((4, 151, 60), 0.05)
    step_pitch_fine_step_latched = scale_colour((255, 86, 114), 1.0)
    step_pitch_fine_step_on = scale_colour((217, 44, 62), 0.35)
    step_pitch_fine_step_off = scale_colour((205, 28, 46), 0.05)
    step_pan_step_latched = scale_colour((203, 120, 255), 1.0)
    step_pan_step_on = scale_colour((139, 72, 191), 0.35)
    step_pan_step_off = scale_colour((114, 48, 171), 0.05)
    step_mod_x_step_latched = scale_colour((126, 255, 56), 1.0)
    step_mod_x_step_on = scale_colour((74, 177, 24), 0.35)
    step_mod_x_step_off = scale_colour((48, 153, 2), 0.05)
    step_mod_y_step_latched = scale_colour((255, 211, 56), 1.0)
    step_mod_y_step_on = scale_colour((187, 149, 24), 0.35)
    step_mod_y_step_off = scale_colour((165, 124, 4), 0.025)
    step_shift_step_latched = scale_colour((255, 131, 56), 1.0)
    step_shift_step_on = scale_colour((229, 98, 28), 0.35)
    step_shift_step_off = scale_colour((201, 64, 2), 0.05)
