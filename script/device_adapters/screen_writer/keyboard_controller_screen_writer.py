from script.constants import SysEx


class KeyboardControllerScreenWriter:
    pot_screen_index_offset = 0x38
    fader_screen_index_offset = 0x50

    def __init__(self, sender, product_defs):
        self.sender = sender
        self.product_defs = product_defs
        sysex_message_header = SysEx.MessageHeader.value + [product_defs.Constants.NovationProductId.value]
        self.clear_custom_text_message = sysex_message_header + [0x06]
        self.set_parameter_name_message_header = sysex_message_header + [0x07]
        self.set_parameter_value_message_header = sysex_message_header + [0x08]
        self.set_temporary_display_upper_row_header = sysex_message_header + [0x09, 0x00]
        self.set_temporary_display_lower_row_header = sysex_message_header + [0x09, 0x01]

    def display_parameter_name(self, control_index, name):
        if (pot_index := self.product_defs.ControlIndexToPotIndex.get(control_index)) is not None:
            screen_control_index = self.pot_screen_index_offset + pot_index
        else:
            screen_control_index = (
                self.fader_screen_index_offset + self.product_defs.ControlIndexToFaderIndex[control_index]
            )

        set_parameter_name_message = (
            self.set_parameter_name_message_header
            + [screen_control_index]
            + list(name.encode(encoding="ascii", errors="replace"))
        )
        self.sender.send_sysex(set_parameter_name_message)

    def display_parameter_value(self, control_index, value):
        if (pot_index := self.product_defs.ControlIndexToPotIndex.get(control_index)) is not None:
            screen_control_index = self.pot_screen_index_offset + pot_index
        else:
            screen_control_index = (
                self.fader_screen_index_offset + self.product_defs.ControlIndexToFaderIndex[control_index]
            )

        set_parameter_value_message = (
            self.set_parameter_value_message_header
            + [screen_control_index]
            + list(value.encode(encoding="ascii", errors="replace"))
        )
        self.sender.send_sysex(set_parameter_value_message)

    def display_notification(self, primary_text="", secondary_text=""):
        set_temporary_display_upper_row_message = self.set_temporary_display_upper_row_header + list(
            primary_text.encode(encoding="ascii", errors="replace")
        )
        self.sender.send_sysex(set_temporary_display_upper_row_message)
        set_temporary_display_lower_row_message = self.set_temporary_display_lower_row_header + list(
            secondary_text.encode(encoding="ascii", errors="replace")
        )
        self.sender.send_sysex(set_temporary_display_lower_row_message)
