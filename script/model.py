__all__ = ["Model"]

from script.constants import SequencerStepEditGroup, SequencerStepEditState


class Scale:
    def __init__(self):
        self.enabled = False
        self.type = "minor"
        self.root = 0


class ChannelRack:
    def __init__(self):
        self.active_bank = 0
        self.navigation_mode = None


class Sequencer:
    def __init__(self):
        self.step_edit_group = SequencerStepEditGroup()
        self.held_steps = []
        self.playing_step = None
        self.step_edit_state = SequencerStepEditState.EditIdle


class DefaultInstrumentLayout:
    class Note:
        def __init__(self, value, *, is_primary=True):
            self.value = value
            self.is_primary = is_primary

    def __init__(self):
        self.octave = 5
        self.note_offset_for_pad = {}


class Model:
    def __init__(self):
        self.channel_rack = ChannelRack()
        self.sequencer = Sequencer()
        self.scale = Scale()
        self.default_instrument_layout = DefaultInstrumentLayout()
        self.fpc_active_bank = 0
        self.slice_x_active_bank = 4
        self.sequencer_active_page = 0

        self.mixer_track_active_bank = 0
        self.mixer_tracks_in_active_bank = []
        self.first_mixer_track_index = 1
        self.last_mixer_track_index = 126
        self.mixer_solo_mute_mode = None
        self.channel_solo_mute_mode = None

        self.pattern_select_active_bank = 0

        self.show_all_highlights_active = False
