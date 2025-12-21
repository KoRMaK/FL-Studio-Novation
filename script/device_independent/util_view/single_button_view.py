from script.colours import Colours


class SingleButtonView:
    def __init__(
        self,
        button_led_writer,
        product_defs,
        button_function,
        *,
        pressed_colour=Colours.button_pressed,
        is_available=None,
        available_colour=Colours.available,
    ):
        """
        Args:
            button_led_writer:  Used to update button led.
            product_defs:       Used to get the button index for the button function.
            button_function:    Used to retrieve the button index.
            pressed_colour:     Colour to use when button is in a pressed state.
            is_available:       Function/Predicate to evaluate to determine whether this button is not available.
                                If this isn't supplied, then it's assumed the button is always available.
            available_colour:   Colour to use when button is available (but not pressed).
        """
        self.button_led_writer = button_led_writer
        self.product_defs = product_defs
        self.button_function = button_function
        self.pressed_colour = pressed_colour
        self.available_colour = available_colour
        self.is_available = is_available
        self.is_pressed = False

    def set_pressed(self):
        self.is_pressed = True
        self.redraw()

    def set_not_pressed(self):
        if self.is_pressed:
            self.is_pressed = False
            self.redraw()

    def show(self):
        self.redraw()

    def hide(self):
        self._turn_off_led()

    def redraw(self):
        self._update_led()

    @property
    def button(self):
        return self.product_defs.FunctionToButton.get(self.button_function)

    @property
    def _colour(self):
        if self.is_available and not self.is_available():
            return Colours.off

        if self.is_pressed:
            return self.pressed_colour
        return self.available_colour

    def _update_led(self):
        self.button_led_writer.set_button_colour(self.button, self._colour)

    def _turn_off_led(self):
        self.button_led_writer.set_button_colour(self.button, Colours.off)
