from script.constants import DeviceId

from .keyboard_controller_screen_writer import KeyboardControllerScreenWriter
from .screen_writer_wrapper import ScreenWriterWrapper

__all__ = ["make_screen_writer"]


def make_screen_writer(device_id, sender, product_defs):
    """Instantiates and returns the relevant implementation of ScreenWriter.

    Args:
        device_id: Device for which to return an implementation of ScreenWriter.
        sender: required by LedWriter instance to control hardware.

    Returns:
        Instance of a ScreenWriter implementation.
    """
    if device_id == DeviceId.FLkey37 or device_id == DeviceId.FLkey49 or device_id == DeviceId.FLkey61:
        return ScreenWriterWrapper(KeyboardControllerScreenWriter(sender, product_defs))
    if device_id == DeviceId.Launchkey or device_id == DeviceId.Launchkey88:
        return ScreenWriterWrapper(KeyboardControllerScreenWriter(sender, product_defs))
    return ScreenWriterWrapper(None)
