from script.action_generators.surface_action_generator.surface_actions import ButtonPressedAction, ButtonReleasedAction


class KeyboardControllerCommonButtonActionGenerator:
    def __init__(self, get_button_for_event, modifier_event):
        self.get_button_for_event = get_button_for_event
        self.modifier_event = modifier_event
        self.modifier_button_is_held = False
        self.held_buttons = set()

    def handle_midi_event(self, fl_event):
        event = fl_event.status, fl_event.data1
        button = self.get_button_for_event(event, modifier_button_is_held=self.modifier_button_is_held)

        is_press_event = fl_event.data2 != 0

        actions = []

        if event == self.modifier_event:
            if is_press_event:
                actions.extend(self._handle_modifier_press_event())
            else:
                actions.extend(self._handle_modifier_release_event())

        if button is None:
            return actions

        if is_press_event:
            actions.extend(self._handle_button_pressed(event, button))
        else:
            actions.extend(self._handle_button_released(event, button))
        return actions

    def _handle_button_pressed(self, event, button):
        if event == self.modifier_event:
            return self._handle_modifier_button_pressed(button)
        return self._handle_non_modifier_button_pressed(button)

    def _handle_button_released(self, event, button):
        if event == self.modifier_event:
            return self._handle_modifier_button_released(button)
        return self._handle_non_modifier_button_released(button)

    def _handle_modifier_press_event(self):
        self.modifier_button_is_held = True
        return self.generate_release_actions_for_all_held_buttons()

    def _handle_modifier_release_event(self):
        self.modifier_button_is_held = False
        return self.generate_release_actions_for_all_held_buttons()

    @staticmethod
    def _handle_modifier_button_pressed(button):
        return [ButtonPressedAction(button=button)]

    @staticmethod
    def _handle_modifier_button_released(button):
        return [ButtonReleasedAction(button=button)]

    def _handle_non_modifier_button_pressed(self, button):
        self.held_buttons.add(button)
        return [ButtonPressedAction(button=button)]

    def _handle_non_modifier_button_released(self, button):
        if button in self.held_buttons:
            return [ButtonReleasedAction(button=button)]
        return []

    def generate_release_actions_for_all_held_buttons(self):
        actions = []
        for button in self.held_buttons:
            actions.append(ButtonReleasedAction(button=button))
        self.held_buttons.clear()
        return actions
