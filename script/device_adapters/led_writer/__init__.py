from script.constants import DeviceId

from .empty_led_writer import EmptyLedWriter
from .keyboard_controller_led_writer import KeyboardControllerLedWriter

__all__ = ["make_led_writer"]


def make_led_writer(device_id, sender, product_defs):
    """Instantiates and returns the relevant implementation of LedWriter.

    Args:
        device_id: Device for which to return an implementation of LedWriter.
        sender: required by LedWriter instance to control hardware.

    Returns:
        Instance of a LedWriter implementation.
    """
    if (
        device_id == DeviceId.FLkey37
        or device_id == DeviceId.FLkey49
        or device_id == DeviceId.FLkey61
        or device_id == DeviceId.FLkeyMini
        or device_id == DeviceId.LaunchkeyMini
        or device_id == DeviceId.Launchkey
        or device_id == DeviceId.Launchkey88
    ):
        return KeyboardControllerLedWriter(sender, product_defs)
    return EmptyLedWriter(sender, product_defs)
