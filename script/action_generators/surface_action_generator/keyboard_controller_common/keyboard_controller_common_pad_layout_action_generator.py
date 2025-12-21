from script.action_generators.surface_action_generator.surface_actions import PadLayoutChangedAction


class KeyboardControllerCommonPadLayoutActionGenerator:
    def __init__(self, product_defs):
        self.product_defs = product_defs

    def handle_midi_event(self, fl_event):
        event_type = fl_event.status, fl_event.data1
        if event_type == self.product_defs.SurfaceEvent.PadLayout.value:
            return [PadLayoutChangedAction(layout=fl_event.data2)]
        return []
