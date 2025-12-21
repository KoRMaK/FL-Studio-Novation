from script.constants import DeviceId

from .flkey_device_setup import FLkeyDeviceSetup
from .flkeymini_device_setup import FLkeyMiniDeviceSetup
from .launchkey_device_setup import LaunchkeyDeviceSetup
from .launchkeymini_device_setup import LaunchkeyMiniDeviceSetup

__all__ = ["make_device_setup"]


def make_device_setup(device_id, sender, product_defs):
    """Instantiates and returns the relevant implementation of DeviceSetup.

    Args:
        device_id: Device for which to return an implementation of DeviceSetup.
        sender: required by DeviceSetup instance to control hardware.

    Returns:
        Instance of a DeviceSetup implementation.
    """
    if device_id == DeviceId.FLkey37 or device_id == DeviceId.FLkey49 or device_id == DeviceId.FLkey61:
        return FLkeyDeviceSetup(sender, product_defs)
    if device_id == DeviceId.FLkeyMini:
        return FLkeyMiniDeviceSetup(sender, product_defs)
    if device_id == DeviceId.LaunchkeyMini:
        return LaunchkeyMiniDeviceSetup(sender, product_defs)
    if device_id == DeviceId.Launchkey or device_id == DeviceId.Launchkey88:
        return LaunchkeyDeviceSetup(sender, product_defs)
    return None
