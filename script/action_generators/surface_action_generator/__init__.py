from script.constants import DeviceId

from .flkey_surface_action_generator import FLkeySurfaceActionGenerator
from .flkeymini_surface_action_generator import FLkeyMiniSurfaceActionGenerator
from .launchkey_surface_action_generator import LaunchkeySurfaceActionGenerator
from .launchkeymini_surface_action_generator import LaunchkeyMiniSurfaceActionGenerator
from .surface_action_generator_wrapper import SurfaceActionGeneratorWrapper

__all__ = ["make_surface_action_generator"]


def make_surface_action_generator(device_id, action_dispatcher, product_defs):
    """Instantiates and returns the relevant implementation of SurfaceActionGenerator.

    Args:
        device_id: Device for which to return an implementation of SurfaceActionGenerator.
        action_dispatcher: required by SurfaceActionGenerator instance dispatch actions.

    Returns:
        Instance of a SurfaceActionGenerator implementation.
    """
    if device_id == DeviceId.FLkey37 or device_id == DeviceId.FLkey49 or device_id == DeviceId.FLkey61:
        return SurfaceActionGeneratorWrapper(action_dispatcher, FLkeySurfaceActionGenerator(product_defs))
    if device_id == DeviceId.FLkeyMini:
        return SurfaceActionGeneratorWrapper(action_dispatcher, FLkeyMiniSurfaceActionGenerator(product_defs))
    if device_id == DeviceId.LaunchkeyMini:
        return SurfaceActionGeneratorWrapper(action_dispatcher, LaunchkeyMiniSurfaceActionGenerator(product_defs))
    if device_id == DeviceId.Launchkey or device_id == DeviceId.Launchkey88:
        return SurfaceActionGeneratorWrapper(action_dispatcher, LaunchkeySurfaceActionGenerator(product_defs))
    return None
