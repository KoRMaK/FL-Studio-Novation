from script.firmware_version_validator import FirmwareVersionValidator
from script.notification_writer import NotificationWriter
from util.timer import Timer


class FirmwareVersionValidationController:
    timer_events_between_old_firmware_notifications = 30

    def __init__(self, action_dispatcher, product_defs, fl, sender):
        self.fl = fl
        self.validator = FirmwareVersionValidator(product_defs, sender)
        self.notification_timer = Timer(action_dispatcher, on_finished=self._on_notification_timer_finished)
        self.on_success_callback = None

    def validation_is_success(self):
        return self.validator.validation_is_success

    def start_validation(self, *, on_success_callback):
        self.on_success_callback = on_success_callback
        self.validator.start_validation(on_finished=self._on_validation_finished)

    def handle_midi_event(self, fl_event):
        self.validator.handle_midi_event(fl_event)

    def abort_validation(self):
        self.validator.abort_validation()
        self.on_success_callback = None

    def _on_validation_finished(self):
        if self.validator.validation_is_success:
            self.on_success_callback()
        else:
            self._handle_validation_failure()

    def _handle_validation_failure(self):
        self.notification_timer.start(self.timer_events_between_old_firmware_notifications)

    def _on_notification_timer_finished(self):
        NotificationWriter.notify_old_firmware(self.fl)
        self.notification_timer.start(self.timer_events_between_old_firmware_notifications)
