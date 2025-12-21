from script.actions import DefaultInstrumentLayoutMappingChangedAction
from script.constants import Pads, Scales
from script.device_independent.util_view import View
from script.model import DefaultInstrumentLayout


class DefaultInstrumentLayoutScaledMappingController(View):
    semitones_per_octave = 12
    note_offsets_for_chromatic_keyboard_mapping = [None, 1, 3, None, 6, 8, 10, None, 0, 2, 4, 5, 7, 9, 11, 12]

    def __init__(self, action_dispatcher, model):
        super().__init__(action_dispatcher)
        self.action_dispatcher = action_dispatcher
        self.model = model

    def _is_root_or_octave(self, note):
        return abs(note - self.model.scale.root) % self.semitones_per_octave == 0

    def _on_show(self):
        self._update_note_offset_mapping()

    def handle_ScaleModelChangedAction(self, action):
        self._update_note_offset_mapping()

    def _update_note_offset_mapping(self):
        enabled, scale_type, scale_root = self.model.scale.enabled, self.model.scale.type, self.model.scale.root
        self.model.default_instrument_layout.note_offset_for_pad = self._make_note_offset_for_pad_mapping(
            enabled, scale_type, scale_root
        )
        self.action_dispatcher.dispatch(DefaultInstrumentLayoutMappingChangedAction())

    def _make_note_offset_for_pad_mapping(self, enabled, scale_type, scale_root):
        if not enabled:
            return self._make_chromatic_note_offset_for_pad_mapping(scale_root)
        return self._make_scaled_note_offset_for_pad_mapping(scale_type, scale_root)

    def _make_chromatic_note_offset_for_pad_mapping(self, scale_root):
        note_offset_for_pad = {}
        for pad, note in enumerate(self.note_offsets_for_chromatic_keyboard_mapping):
            if note is None:
                continue
            note_offset_for_pad[pad] = DefaultInstrumentLayout.Note(scale_root + note)
        return note_offset_for_pad

    def _make_scaled_note_offset_for_pad_mapping(self, scale_type, scale_root):
        scale_notes = Scales.get(scale_type).copy()
        scale_notes.append(self.semitones_per_octave)
        note_offset_for_pad = {}

        for pad, note in enumerate(scale_notes):
            note = scale_root + note
            note_offset_for_pad[pad] = DefaultInstrumentLayout.Note(note, is_primary=self._is_root_or_octave(note))

        for pad, note in enumerate(scale_notes):
            pad += Pads.Num.value // 2
            note = -self.semitones_per_octave + scale_root + note
            note_offset_for_pad[pad] = DefaultInstrumentLayout.Note(note, is_primary=self._is_root_or_octave(note))

        return note_offset_for_pad
