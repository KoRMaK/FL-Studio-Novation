class DeviceSetupExample:
    """Device Setup Example

    The Device Setup class prepares the hardware device for interaction with the device
    adapters and action generators. (E.g., activate DAW mode on the device)

    On script exit it will return the device to a
    default state. (E.g., deactivate DAW mode on the device)
    """

    def __init__(self, sender, product_defs):
        """
        Args:
            sender: Used to communicate with hardware
            product_defs: Used to determine the available surface events
        """

    def init(self):
        """
        Prepares the hardware device for interaction with the device adapters
        and action generators. (E.g., activates DAW mode on the device)
        """

    def deinit(self):
        """
        Returns the device to a default state. (E.g., deactivate DAW mode on the device)
        """
