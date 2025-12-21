from script.action_generators.surface_action_generator.surface_actions import ControlChangedAction


class KeyboardControllerCommonFaderActionGenerator:
    MaxMidiValue = 127

    def __init__(self, product_defs):
        self.product_defs = product_defs

    def handle_midi_event(self, fl_event):
        fader_event_status, fader_first_index = self.product_defs.SurfaceEvent.FaderFirst.value
        _, fader_last_index = self.product_defs.SurfaceEvent.FaderLast.value
        if fl_event.status == fader_event_status and fader_first_index <= fl_event.data1 <= fader_last_index:
            fader = fl_event.data1 - fader_first_index
            normalised_position = fl_event.data2 / self.MaxMidiValue
            if (control := self.product_defs.FaderIndexToControlIndex.get(fader)) is not None:
                return [ControlChangedAction(control=control, position=normalised_position)]
        return []
