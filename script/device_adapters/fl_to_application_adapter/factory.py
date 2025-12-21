from script.action_generators.fl_action_generator import FLActionGenerator
from script.action_generators.surface_action_generator import make_surface_action_generator
from script.device_adapters.device_manager import make_device_manager
from script.device_adapters.device_setup import make_device_setup
from script.device_adapters.fl_setup import make_fl_setup
from script.device_adapters.fl_to_application_adapter.fl_to_application_adapter import FLToApplicationAdapter
from script.device_adapters.led_writer import make_led_writer
from script.device_adapters.screen_writer import make_screen_writer
from script.device_dependent import make_application
from script.firmware_version_validation_controller import FirmwareVersionValidationController
from script.fl import FL
from script.fl_api_version_check_controller import FlApiVersionCheckController
from script.product_defs import make_product_defs
from script.sender import Sender
from util.action_dispatcher import ActionDispatcher


def make_fl_to_application_adapter(device_id):
    """Instantiates the entire application and returns an FlToApplicationAdapter

    Args:
        device_id: Device for which to return an FlToApplicationAdapter

    Returns:
        An FlToApplicationAdapter
    """
    # Get product definitions
    product_defs = make_product_defs(device_id)

    # Create utilities
    sender = Sender()

    # Create driven/secondary actors
    fl = FL()
    device_setup = make_device_setup(device_id, sender, product_defs)
    fl_setup = make_fl_setup(device_id, fl)
    led_writer = make_led_writer(device_id, sender, product_defs)
    screen_writer = make_screen_writer(device_id, sender, product_defs)
    device_manager = make_device_manager(device_id, sender, product_defs)

    def reset_device_adapters():
        screen_writer.reset()

    # Create application
    action_dispatcher = ActionDispatcher()
    firmware_version_validation_controller = FirmwareVersionValidationController(
        action_dispatcher, product_defs, fl, sender
    )
    fl_api_version_check_controller = FlApiVersionCheckController(action_dispatcher, product_defs, fl)
    application = make_application(
        device_id, led_writer, led_writer, fl, action_dispatcher, screen_writer, device_manager, product_defs
    )

    # Create driver/primary actors
    surface_action_generator = make_surface_action_generator(device_id, action_dispatcher, product_defs)
    fl_action_generator = FLActionGenerator(action_dispatcher, fl)

    # Create fl to application adapter
    return FLToApplicationAdapter(
        device_setup,
        fl_setup,
        application,
        led_writer,
        fl,
        action_dispatcher,
        surface_action_generator,
        fl_action_generator,
        firmware_version_validation_controller,
        fl_api_version_check_controller,
        reset_device_adapters,
    )
