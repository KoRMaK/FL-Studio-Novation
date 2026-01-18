from script.colours import Colours
from script.device_independent.util_view.view import View


class PotModeSelectorView(View):
    """
    Handles Undo + Pad presses to select pot modes (when in Drum pad mode).
    Hold Undo button and press:
    - Pad 1 (index 0): Volume mode (dim light when not selected, bright when selected)
    - Pad 2 (index 1): Plugin mode (dim light when not selected, bright when selected)
    - Pad 3 (index 2): Pan mode (dim light when not selected, bright when selected)
    """

    def __init__(self, action_dispatcher, pad_led_writer, device_manager, product_defs, model):
        super().__init__(action_dispatcher)
        self.pad_led_writer = pad_led_writer
        self.device_manager = device_manager
        self.product_defs = product_defs
        self.model = model
        self.shift_pressed = False  # Undo button acts as shift
        self.current_pot_mode = self.product_defs.PotLayout.Volume  # Default

    def _on_show(self):
        # Initialize - update LEDs based on current mode
        self._update_mode_indicator_leds()

    def _on_hide(self):
        # Turn off mode indicator LEDs
        for pad in range(3):
            self.pad_led_writer.set_pad_colour(pad, Colours.off)

    def handle_ButtonPressedAction(self, action):
        # Use Undo button as Shift modifier
        if action.button == self.product_defs.Button.Undo:
            self.shift_pressed = True

    def handle_ButtonReleasedAction(self, action):
        # Release Undo/Shift modifier
        if action.button == self.product_defs.Button.Undo:
            self.shift_pressed = False

    def handle_PadPressAction(self, action):
        # Only handle pads 1-3 (indices 0-2) when Undo/Shift is held
        if not self.shift_pressed or action.pad > 2:
            return

        # Pad 1 (index 0) -> Volume mode
        if action.pad == 0:
            self.current_pot_mode = self.product_defs.PotLayout.Volume
            self.device_manager.select_pot_layout(self.product_defs.PotLayout.Volume.value)
            self._update_mode_indicator_leds()

        # Pad 2 (index 1) -> Plugin mode
        elif action.pad == 1:
            self.current_pot_mode = self.product_defs.PotLayout.Plugin
            self.device_manager.select_pot_layout(self.product_defs.PotLayout.Plugin.value)
            self._update_mode_indicator_leds()

        # Pad 3 (index 2) -> Pan mode
        elif action.pad == 2:
            self.current_pot_mode = self.product_defs.PotLayout.Pan
            self.device_manager.select_pot_layout(self.product_defs.PotLayout.Pan.value)
            self._update_mode_indicator_leds()

    def handle_PotLayoutChangedAction(self, action):
        # Update current mode when pot layout changes from hardware
        if action.layout == self.product_defs.PotLayout.Volume.value:
            self.current_pot_mode = self.product_defs.PotLayout.Volume
        elif action.layout == self.product_defs.PotLayout.Plugin.value:
            self.current_pot_mode = self.product_defs.PotLayout.Plugin
        elif action.layout == self.product_defs.PotLayout.Pan.value:
            self.current_pot_mode = self.product_defs.PotLayout.Pan

        self._update_mode_indicator_leds()

    def _update_mode_indicator_leds(self):
        """Update pad LEDs to show current pot mode - brighter for selected mode"""
        # Pad 1: Volume mode indicator
        if self.current_pot_mode == self.product_defs.PotLayout.Volume:
            self.pad_led_writer.set_pad_colour(0, Colours.pad_pressed)  # Bright white
        else:
            self.pad_led_writer.set_pad_colour(0, (40, 40, 40))  # Dim

        # Pad 2: Plugin mode indicator
        if self.current_pot_mode == self.product_defs.PotLayout.Plugin:
            self.pad_led_writer.set_pad_colour(1, Colours.pad_pressed)  # Bright white
        else:
            self.pad_led_writer.set_pad_colour(1, (40, 40, 40))  # Dim

        # Pad 3: Pan mode indicator
        if self.current_pot_mode == self.product_defs.PotLayout.Pan:
            self.pad_led_writer.set_pad_colour(2, Colours.pad_pressed)  # Bright white
        else:
            self.pad_led_writer.set_pad_colour(2, (40, 40, 40))  # Dim
