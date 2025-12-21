from script.action_generators.surface_action_generator.surface_actions import PadPressAction, PadReleaseAction
from util import midi


class KeyboardControllerCommonPadActionGenerator:
    def __init__(self, product_defs):
        self.product_defs = product_defs

    def pad_for_note(self, note):
        return self.product_defs.Constants.PadForLayoutNote.value.get(note)

    def handle_midi_event(self, fl_event):
        if midi.is_note_message(fl_event):
            note, velocity = fl_event.data1, fl_event.data2
            pad = self.pad_for_note(note)

            if pad is not None:
                if velocity != 0:
                    return [PadPressAction(pad=pad, velocity=velocity)]
                return [PadReleaseAction(pad=pad)]
        return []
