from script.constants import DeviceId

from .FLkey import Application as FLkeyApplication  # noqa: F401
from .FLkeyMini import Application as FLkeyMiniApplication  # noqa: F401
from .Launchkey import Application as LaunchkeyApplication  # noqa: F401
from .LaunchkeyMini import Application as LaunchkeyMiniApplication  # noqa: F401

__all__ = ["make_application"]


def make_application(
    device_id, pad_led_writer, button_led_writer, fl, action_dispatcher, screen_writer, device_manager, product_defs
):
    device_to_application_class = {
        DeviceId.FLkeyMini: globals()["FLkeyMiniApplication"],
        DeviceId.FLkey37: globals()["FLkeyApplication"],
        DeviceId.FLkey49: globals()["FLkeyApplication"],
        DeviceId.FLkey61: globals()["FLkeyApplication"],
        DeviceId.LaunchkeyMini: globals()["LaunchkeyMiniApplication"],
        DeviceId.Launchkey: globals()["LaunchkeyApplication"],
        DeviceId.Launchkey88: globals()["LaunchkeyApplication"],
    }

    application_class = device_to_application_class[device_id]

    return application_class(
        pad_led_writer, button_led_writer, fl, action_dispatcher, screen_writer, device_manager, product_defs
    )
