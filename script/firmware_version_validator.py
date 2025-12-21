from script.constants import SysEx, ValidationState
from util import midi


class FirmwareVersionValidator:
    def __init__(self, product_defs, sender):
        self.product_defs = product_defs
        self.sender = sender

        self.minimum_firmware_version = None
        self.on_finished_callback = None
        self.validation_state = ValidationState.Idle

    def start_validation(self, *, on_finished):
        try:
            self.minimum_firmware_version = self.product_defs.Constants.MinimumFirmwareVersion.value
            self.validation_state = ValidationState.InProgress
            self.on_finished_callback = on_finished
            self._send_device_inquiry()
        except AttributeError:
            self.validation_state = ValidationState.Success
            on_finished()

    def abort_validation(self):
        if self.validation_is_in_progress:
            self.on_success_callback = None
            self.validation_state = ValidationState.Idle

    def handle_midi_event(self, message):
        if not self.validation_is_in_progress:
            return

        self.validation_state = self._do_validation(message)

        if self.validation_is_success or self.validation_is_failure:
            self.on_finished_callback()

    @property
    def validation_is_in_progress(self):
        return self.validation_state == ValidationState.InProgress

    @property
    def validation_is_success(self):
        return self.validation_state == ValidationState.Success

    @property
    def validation_is_failure(self):
        return self.validation_state == ValidationState.Failure

    def _send_device_inquiry(self):
        self.sender.send_sysex(SysEx.DeviceEnquiryRequest.value)

    def _do_validation(self, fl_event):
        sysex = midi.get_sysex(fl_event)

        if sysex and sysex[: len(SysEx.DeviceEnquiryResponseHeader.value)] == SysEx.DeviceEnquiryResponseHeader.value:
            firmware_version = tuple(sysex[11:])
            if firmware_version >= self.minimum_firmware_version:
                return ValidationState.Success
            return ValidationState.Failure

        return ValidationState.InProgress
