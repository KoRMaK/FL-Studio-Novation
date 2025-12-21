from .generic_fl_setup import GenericFLSetup

__all__ = ["make_fl_setup"]


def make_fl_setup(device_id, fl):
    """Instantiates and returns the relevant implementation of FLSetup

    Args:
        device_id: Device for which to return an implementation of FLSetup
        fl: required by FLSetup instance to set initial FL Studio settings

    Returns:
        Instance of a FLSetup implementation.
    """
    return GenericFLSetup(fl)
