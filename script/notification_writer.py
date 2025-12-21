class NotificationWriter:
    @staticmethod
    def notify_old_firmware(fl):
        fl.ui.set_hint_message("Update Launchkey for new functionality\r\n" "Visit Novation Components")

    @staticmethod
    def notify_incompatible_fl_studio_version(fl, *, device_name):
        fl.ui.set_hint_message(
            f"{device_name} requires a more recent version of FL Studio\r\n" "Please update to the latest version"
        )
