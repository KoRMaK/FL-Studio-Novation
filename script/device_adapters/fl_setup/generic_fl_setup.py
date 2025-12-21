class GenericFLSetup:
    def __init__(self, fl):
        self.fl = fl

    def handle_first_time_connected(self):
        if not self.fl.loop_record_is_active():
            self.fl.toggle_loop_record()

        self.fl.enable_master_sync()
