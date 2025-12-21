from script.actions import ScaleModelChangedAction
from script.device_independent.util_view.view import View


class ScaleModelController(View):
    def __init__(self, action_dispatcher, product_defs, model):
        super().__init__(action_dispatcher)
        self.product_defs = product_defs
        self.model = model
        self.action_dispatcher = action_dispatcher

    def handle_ScaleEnabledAction(self, action):
        if not self.model.scale.enabled:
            self.model.scale.enabled = True
        self.action_dispatcher.dispatch(ScaleModelChangedAction())

    def handle_ScaleDisabledAction(self, action):
        if self.model.scale.enabled:
            self.model.scale.enabled = False
        self.action_dispatcher.dispatch(ScaleModelChangedAction())

    def handle_ScaleTypeChangedAction(self, action):
        scale_type = self.product_defs.Constants.Scales.value.get(action.scale_index)
        if scale_type is not None:
            self.model.scale.type = scale_type
            self.action_dispatcher.dispatch(ScaleModelChangedAction())

    def handle_ScaleRootChangedAction(self, action):
        if self.model.scale.root != action.scale_root:
            self.model.scale.root = action.scale_root
        self.action_dispatcher.dispatch(ScaleModelChangedAction())
