class LaunchkeyDeviceSetup:
    def __init__(self, sender, product_defs):
        self.sender = sender
        self.product_defs = product_defs

    def init(self):
        self._enter_daw_mode()
        self._select_pot_layout_pan()
        self._select_pad_layout_drum()
        self._select_fader_layout_volume()

    def deinit(self):
        self._exit_daw_mode()

    def _enter_daw_mode(self):
        self.sender.send_message(*self.product_defs.SurfaceEvent.EnterDawMode.value)

    def _exit_daw_mode(self):
        self.sender.send_message(*self.product_defs.SurfaceEvent.ExitDawMode.value)

    def _select_pot_layout_pan(self):
        self.sender.send_message(
            *self.product_defs.SurfaceEvent.PotLayout.value, self.product_defs.PotLayout.Volume.value
        )

    def _select_pad_layout_drum(self):
        self.sender.send_message(
            *self.product_defs.SurfaceEvent.PadLayout.value, self.product_defs.PadLayout.Drum.value
        )

    def _select_fader_layout_volume(self):
        # Selecting Volume as the very first layout won't generate a response.
        # This is a known issue and selecting another layout first (send A) is
        # a workaround.
        self.sender.send_message(
            *self.product_defs.SurfaceEvent.FaderLayout.value, self.product_defs.FaderLayout.SendA.value
        )
        self.sender.send_message(
            *self.product_defs.SurfaceEvent.FaderLayout.value, self.product_defs.FaderLayout.Volume.value
        )
