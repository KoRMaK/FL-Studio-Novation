from script.colours import Colours
from script.constants import LedLightingType, SysEx


class KeyboardControllerLedWriter:
    def __init__(self, sender, product_defs):
        self.sender = sender
        self.product_defs = product_defs
        self.sysex_led_update_header = SysEx.MessageHeader.value + [
            product_defs.Constants.NovationProductId.value,
            0x01,
        ]
        self.shift_pressed = False
        self._shift_button_led_states = {}
        self._button_led_states = {}
        self._cached_led_updates = {}
        self._caching = False
        self.gamma = 2.25
        self._initialise_button_led_states()

    @staticmethod
    def brightness(r, g, b):
        return max(r, g, b)

    def _initialise_button_led_states(self):
        self._caching = True
        for button in self.product_defs.ButtonToLedIndex.keys():
            self.set_button_colour(button, Colours.off)
            self._button_led_states = dict(
                list(self._shift_button_led_states.items()) + list(self._button_led_states.items())
            )
            self._shift_button_led_states = dict(
                list(self._button_led_states.items()) + list(self._shift_button_led_states.items())
            )
            self._cached_led_updates = {}
        self._caching = False

    def set_pad_colour(self, pad, colour: (Colours.Item, int, tuple)):
        if pad is None:
            return

        if isinstance(colour, Colours.Item):
            colour = colour.value

        target = self.product_defs.Constants.LightingTargetNote.value

        if isinstance(colour, int):
            self._cached_led_updates[(target, pad)] = (
                target | self.product_defs.Constants.LightingTypeStatic.value,
                pad,
                colour,
            )
        elif isinstance(colour, tuple):
            colour = self.convert_from_8_bit_to_7_bit(*colour)
            colour = self.apply_gamma_correction(self.gamma, *colour)
            self._cached_led_updates[(target, pad)] = (
                target | self.product_defs.Constants.LightingTypeRGB.value,
                pad,
                *colour,
            )

        if not self._caching:
            self._send_cached_led_updates()

    @staticmethod
    def convert_from_8_bit_to_7_bit(red, green, blue):
        return red // 2, green // 2, blue // 2

    def apply_gamma_correction(self, gamma, red, green, blue):
        # Calculate the brightness before correction
        brightness_before = self.brightness(red, green, blue)

        if brightness_before == 0:
            return red, green, blue

        # Apply gamma correction
        red = 128 * ((red / 128) ** gamma)
        green = 128 * ((green / 128) ** gamma)
        blue = 128 * ((blue / 128) ** gamma)

        # Calculate brightness after correction
        brightness_after = self.brightness(red, green, blue)
        brightness_correction_factor = brightness_before / brightness_after
        # Bring colour back to original brightness
        red = red * brightness_correction_factor
        green = green * brightness_correction_factor
        blue = blue * brightness_correction_factor

        return int(round(red)), int(round(green)), int(round(blue))

    def set_button_colour(self, button, colour, *, lighting_type=LedLightingType.Static):
        led_index = self.product_defs.ButtonToLedIndex.get(button)
        if led_index is None:
            return

        target = self.product_defs.Constants.LightingTargetCC.value

        if lighting_type == LedLightingType.Pulsing:
            led_update = (target | self.product_defs.Constants.LightingTypePulsing.value, led_index, int(colour))

        elif lighting_type == LedLightingType.RGB and isinstance(colour, tuple):
            colour = self.convert_from_8_bit_to_7_bit(*colour)
            colour = self.apply_gamma_correction(self.gamma, *colour)
            led_update = (
                target | self.product_defs.Constants.LightingTypeRGB.value,
                led_index,
                *colour,
            )
        else:
            led_update = (target | self.product_defs.Constants.LightingTypeStatic.value, led_index, int(colour))

        shift_pressed = self.shift_pressed
        is_shift_button = self.product_defs.IsShiftButton(button)
        if self.product_defs.ForwardButtonLedGivenShift(button, shift_pressed):
            self._cached_led_updates[(target, led_index)] = led_update

        if is_shift_button:
            self._shift_button_led_states[(target, led_index)] = led_update
        else:
            self._button_led_states[(target, led_index)] = led_update

        if not self._caching:
            self._send_cached_led_updates()

    def start_caching_led_updates(self):
        self._caching = True

    def stop_caching_led_updates(self):
        self._caching = False
        self._send_cached_led_updates()

    def _send_cached_led_updates(self):
        if not self._cached_led_updates:
            return

        message = self.sysex_led_update_header.copy()
        for led_update in self._cached_led_updates.values():
            message.extend([*led_update])

        self._cached_led_updates.clear()
        self.sender.send_sysex(message)

    def shift_modifier_pressed(self):
        self.shift_pressed = True
        self._cached_led_updates.update(self._shift_button_led_states)

    def shift_modifier_released(self):
        self.shift_pressed = False
        self._cached_led_updates.update(self._button_led_states)
