from script.action_generators.surface_action_generator.surface_actions import (
    ScaleDisabledAction,
    ScaleEnabledAction,
    ScaleRootChangedAction,
    ScaleTypeChangedAction,
)


class KeyboardControllerCommonScaleActionGenerator:
    def __init__(self, product_defs):
        self.product_defs = product_defs

    def handle_midi_event(self, fl_event):
        event_type = fl_event.status, fl_event.data1
        if event_type == self.product_defs.SurfaceEvent.ScaleModeEnabled:
            if fl_event.data2 == 0:
                return [ScaleDisabledAction()]
            return [ScaleEnabledAction()]
        if event_type == self.product_defs.SurfaceEvent.ScaleTypeChanged:
            return [ScaleTypeChangedAction(scale_index=fl_event.data2)]
        if event_type == self.product_defs.SurfaceEvent.ScaleRootChanged:
            scale_root = fl_event.data2 % 12
            return [ScaleRootChangedAction(scale_root=scale_root)]
        return []
