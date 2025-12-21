from script.action_generators.surface_action_generator.surface_actions import ControlChangedAction


class KeyboardControllerCommonPotActionGenerator:
    MaxMidiValue = 127

    def __init__(self, product_defs):
        self.product_defs = product_defs

    def handle_midi_event(self, fl_event):
        pot_event_status, pot_first_index = self.product_defs.SurfaceEvent.PotFirst.value
        _, pot_last_index = self.product_defs.SurfaceEvent.PotLast.value
        if fl_event.status == pot_event_status and pot_first_index <= fl_event.data1 <= pot_last_index:
            pot = fl_event.data1 - pot_first_index
            normalised_position = fl_event.data2 / self.MaxMidiValue
            if (control := self.product_defs.PotIndexToControlIndex.get(pot)) is not None:
                return [ControlChangedAction(control=control, position=normalised_position)]
        return []
