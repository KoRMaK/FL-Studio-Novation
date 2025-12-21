class FLkeyDeviceSetup:
    def __init__(self, sender, product_defs):
        self.sender = sender
        self.product_defs = product_defs

    def init(self):
        self._enter_daw_mode()
        self._select_pot_layout_channel_volume()
        self._select_pad_layout_channel_rack()
        self._select_fader_layout_mixer_volume()
        self._query_scale_mode_settings()

    def deinit(self):
        self._exit_daw_mode()

    def _enter_daw_mode(self):
        self.sender.send_message(*self.product_defs.SurfaceEvent.EnterDawMode.value)

    def _exit_daw_mode(self):
        self.sender.send_message(*self.product_defs.SurfaceEvent.ExitDawMode.value)

    def _select_pot_layout_channel_volume(self):
        self.sender.send_message(
            *self.product_defs.SurfaceEvent.PotLayout.value, self.product_defs.PotLayout.ChannelVolume.value
        )

    def _select_pad_layout_channel_rack(self):
        self.sender.send_message(
            *self.product_defs.SurfaceEvent.PadLayout.value, self.product_defs.PadLayout.ChannelRack.value
        )

    def _query_scale_mode_settings(self):
        self.sender.send_message(*self.product_defs.SurfaceEvent.QueryScaleModeEnabled.value)
        self.sender.send_message(*self.product_defs.SurfaceEvent.QueryScaleType.value)
        self.sender.send_message(*self.product_defs.SurfaceEvent.QueryScaleRoot.value)

    def _select_fader_layout_mixer_volume(self):
        self.sender.send_message(
            *self.product_defs.SurfaceEvent.FaderLayout.value, self.product_defs.FaderLayout.MixerVolume.value
        )
