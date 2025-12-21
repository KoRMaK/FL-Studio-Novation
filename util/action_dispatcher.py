class ActionDispatcher:
    def __init__(self):
        self._callback_lists_for_actions = {}

    def subscribe(self, subscriber):
        callbacks = ActionDispatcher._extract_callbacks(subscriber)

        for action_name, callback in callbacks.items():
            # Get callback list if key exists, otherwise set and return an empty list
            callback_list = self._callback_lists_for_actions.setdefault(action_name, [])
            if callback not in callback_list:
                callback_list.append(callback)

    def unsubscribe(self, subscriber):
        callbacks = ActionDispatcher._extract_callbacks(subscriber)

        for action_name, callback in callbacks.items():
            callback_list = self._callback_lists_for_actions.get(action_name, [])
            if callback in callback_list:
                callback_list.remove(callback)

    def dispatch(self, action):
        action_name = action.__class__.__name__
        callback_list = self._callback_lists_for_actions.get(action_name)

        if not callback_list:
            return

        callback_list_copy = callback_list.copy()

        for callback in callback_list_copy:
            # Ensure callback was not unsubscribed as side effect of other callback in dispatch loop
            if callback in callback_list:
                callback(action)

    @staticmethod
    def _extract_callbacks(subscriber):
        return {
            attr_name.lstrip("handle_"): getattr(subscriber, attr_name)
            for attr_name in dir(subscriber)
            if ActionDispatcher._is_action_callback(subscriber, attr_name)
        }

    @staticmethod
    def _is_action_callback(subscriber, attr_name):
        return (
            attr_name.startswith("handle_")
            and attr_name.endswith("Action")
            and callable(getattr(subscriber, attr_name))
        )
