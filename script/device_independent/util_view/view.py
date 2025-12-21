class View:
    def __init__(self, action_dispatcher):
        self.action_dispatcher = action_dispatcher

    def show(self):
        self.action_dispatcher.subscribe(self)
        self._on_show()

    def _on_show(self):
        pass

    def hide(self):
        self._on_hide()
        self.action_dispatcher.unsubscribe(self)

    def _on_hide(self):
        pass
