class FLKeyRangeDeviceManager:
    sysex_message_header = [0x00, 0x20, 0x29, 0x02]
    set_tempo_command = 0x0A

    def __init__(self, sender, product_defs):
        self.sender = sender
        self.product_defs = product_defs

    def select_pot_layout(self, layout):
        self.sender.send_message(*self.product_defs.SurfaceEvent.PotLayout.value, layout)

    def return_to_previous_pot_layout(self):
        self.sender.send_message(
            *self.product_defs.SurfaceEvent.PotLayout.value, self.product_defs.PotLayout.Revert.value
        )

    def set_tempo(self, tempo):
        msb = (int(tempo) >> 7) & 0x7F
        lsb = int(tempo) & 0x7F
        set_tempo_sysex_message = self.sysex_message_header + [
            self.product_defs.Constants.NovationProductId.value,
            self.set_tempo_command,
            msb,
            lsb,
        ]
        self.sender.send_sysex(set_tempo_sysex_message)
