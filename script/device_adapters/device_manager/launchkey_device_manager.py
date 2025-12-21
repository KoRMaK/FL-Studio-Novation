class LaunchkeyDeviceManager:
    def __init__(self, sender, product_defs):
        self.sender = sender
        self.product_defs = product_defs

    def select_pot_layout(self, layout):
        self.sender.send_message(*self.product_defs.SurfaceEvent.PotLayout.value, layout)
