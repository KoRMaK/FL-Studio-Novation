from script.device_independent.util_view.single_button_view import SingleButtonView
from script.device_independent.util_view.view import View
from util.value_with_range import ValueWithRange


class ArrowButtonView(View):
    def __init__(
        self,
        action_dispatcher,
        button_led_writer,
        product_defs,
        *,
        decrement_button,
        increment_button,
        last_page=0,
        on_page_changed=None,
        on_page_change_attempted=None,
    ):
        super().__init__(action_dispatcher)
        self.value = ValueWithRange(upper_bound=last_page)
        self.decrement_button_view = SingleButtonView(
            button_led_writer, product_defs, decrement_button, is_available=lambda: not self.value.reached_lower_bound()
        )
        self.increment_button_view = SingleButtonView(
            button_led_writer, product_defs, increment_button, is_available=lambda: not self.value.reached_upper_bound()
        )
        self.on_page_changed = on_page_changed
        self.on_page_change_attempt = on_page_change_attempted

    @property
    def active_page(self):
        return self.value.value

    def set_active_page(self, page):
        self.value.set_value(page)
        self.redraw_leds()

    def set_page_range(self, first_page, last_page, *, notify_on_page_change=False):
        if self.value.set_range(lower_bound=first_page, upper_bound=last_page):
            if notify_on_page_change and self.on_page_changed:
                self.on_page_changed()
        self.redraw_leds()

    def handle_ButtonPressedAction(self, action):
        if action.button == self.increment_button_view.button:
            self._press_increment_button()
        elif action.button == self.decrement_button_view.button:
            self._press_decrement_button()

    def handle_ButtonReleasedAction(self, action):
        if action.button == self.increment_button_view.button:
            self._release_increment_button()
        elif action.button == self.decrement_button_view.button:
            self._release_decrement_button()

    def redraw_leds(self):
        self.increment_button_view.redraw()
        self.decrement_button_view.redraw()

    def _on_show(self):
        self.increment_button_view.show()
        self.decrement_button_view.show()

    def _on_hide(self):
        self.increment_button_view.hide()
        self.decrement_button_view.hide()

    def _increment(self):
        if self.value.increment() and self.on_page_changed:
            self.on_page_changed()
        if self.on_page_change_attempt:
            self.on_page_change_attempt()
        self.redraw_leds()

    def _decrement(self):
        if self.value.decrement() and self.on_page_changed:
            self.on_page_changed()
        if self.on_page_change_attempt:
            self.on_page_change_attempt()
        self.redraw_leds()

    def _press_increment_button(self):
        self.increment_button_view.set_pressed()
        self._increment()

    def _press_decrement_button(self):
        self.decrement_button_view.set_pressed()
        self._decrement()

    def _release_increment_button(self):
        self.increment_button_view.set_not_pressed()

    def _release_decrement_button(self):
        self.decrement_button_view.set_not_pressed()
