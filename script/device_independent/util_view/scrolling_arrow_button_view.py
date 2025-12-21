from script.constants import ScrollingSpeed
from script.device_independent.util_view.single_button_view import SingleButtonView
from script.device_independent.util_view.view import View
from util.scroller import Scroller
from util.value_with_range import ValueWithRange


class ScrollingArrowButtonView(View):
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
        speed=ScrollingSpeed.Default.value,
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
        self.on_page_change_attempted = on_page_change_attempted
        self.scroller = Scroller(self._on_scroll_step, speed)

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

    def handle_TimerEventAction(self, action):
        self.scroller.tick()

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
        if self.on_page_change_attempted:
            self.on_page_change_attempted()
        self.redraw_leds()

    def _decrement(self):
        if self.value.decrement() and self.on_page_changed:
            self.on_page_changed()
        if self.on_page_change_attempted:
            self.on_page_change_attempted()
        self.redraw_leds()

    def _press_increment_button(self):
        self.increment_button_view.set_pressed()
        self.scroller.set_active()
        self._increment()

    def _press_decrement_button(self):
        self.decrement_button_view.set_pressed()
        self.scroller.set_active()
        self._decrement()

    def _release_increment_button(self):
        self.increment_button_view.set_not_pressed()
        if not self.decrement_button_view.is_pressed:
            self.scroller.set_not_active()

    def _release_decrement_button(self):
        self.decrement_button_view.set_not_pressed()
        if not self.increment_button_view.is_pressed:
            self.scroller.set_not_active()

    def _on_scroll_step(self):
        if self.increment_button_view.is_pressed:
            self._increment()
        else:
            self._decrement()
