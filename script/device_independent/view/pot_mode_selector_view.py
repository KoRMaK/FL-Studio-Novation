from script.colours import Colours
from script.device_independent.util_view.view import View


class PotModeSelectorView(View):
    """
    Handles Shift + Device Pad (Pad 1, top-left) to activate Plugin pot mode.
    Hold Shift button and press Pad 1 (Device pad) to toggle Plugin mode on/off.
    - Plugin mode active: Pad 1 shows bright white
    - Plugin mode inactive: Pad 1 shows dim light
    """

    def __init__(self, action_dispatcher, pad_led_writer, device_manager, product_defs, model):
        super().__init__(action_dispatcher)
        self.pad_led_writer = pad_led_writer
        self.device_manager = device_manager
        self.product_defs = product_defs
        self.model = model
        self.shift_pressed = False  # Shift button state
        self.plugin_mode_active = False  # Track if Plugin mode is active

    def _on_show(self):
        # Initialize - update LED based on current mode
        self._update_mode_indicator_led()

    def _on_hide(self):
        # Turn off mode indicator LED for Pad 1
        self.pad_led_writer.set_pad_colour(0, Colours.off)

    def handle_ButtonPressedAction(self, action):
        # Track Shift button state
        if self.product_defs.IsShiftButton(action.button):
            self.shift_pressed = True

    def handle_ButtonReleasedAction(self, action):
        # Release Shift button
        if self.product_defs.IsShiftButton(action.button):
            self.shift_pressed = False

    def handle_PadPressAction(self, action):
        # Only handle Pad 1 (Device pad, index 0) when Undo/Shift is held
        if not self.shift_pressed or action.pad != 0:
            return

        # Toggle Plugin mode on/off
        if self.plugin_mode_active:
            # Turn off Plugin mode, return to Volume mode
            self.plugin_mode_active = False
            self.device_manager.select_pot_layout(self.product_defs.PotLayout.Volume.value)
        else:
            # Turn on Plugin mode
            self.plugin_mode_active = True
            self.device_manager.select_pot_layout(self.product_defs.PotLayout.Plugin.value)

        self._update_mode_indicator_led()

    def handle_PotLayoutChangedAction(self, action):
        # Update plugin mode state when pot layout changes from hardware or other sources
        if action.layout == self.product_defs.PotLayout.Plugin.value:
            self.plugin_mode_active = True
        else:
            # Any other mode (Volume or Pan) deactivates plugin mode
            self.plugin_mode_active = False

        self._update_mode_indicator_led()

    def _update_mode_indicator_led(self):
        """Update Pad 1 LED to show Plugin mode status - brighter when active"""
        if self.plugin_mode_active:
            self.pad_led_writer.set_pad_colour(0, Colours.pad_pressed)  # Bright white - Plugin mode ON
        else:
            self.pad_led_writer.set_pad_colour(0, (40, 40, 40))  # Dim - Plugin mode OFF
