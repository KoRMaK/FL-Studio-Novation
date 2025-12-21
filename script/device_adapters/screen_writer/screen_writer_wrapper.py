class ScreenWriterWrapper:
    def __init__(self, screen_writer):
        self.screen_writer = screen_writer
        self.most_recently_used_display_parameter_args = None
        self.most_recently_used_display_parameter_name_args = None
        self.most_recently_used_display_parameter_value_args = None

    def reset(self):
        self.most_recently_used_display_parameter_name_args = None
        self.most_recently_used_display_parameter_value_args = None

    def display_parameter(self, control_index, name, value):
        if self.screen_writer:
            args = (control_index, name, value)
            if args != self.most_recently_used_display_parameter_args:
                self.most_recently_used_display_parameter_args = args
                self.screen_writer.display_parameter_name(control_index, name)
                self.screen_writer.display_parameter_value(control_index, value)

    def display_parameter_name(self, control_index, name):
        if self.screen_writer:
            args = (control_index, name)
            if args != self.most_recently_used_display_parameter_name_args:
                self.most_recently_used_display_parameter_name_args = args
                self.screen_writer.display_parameter_name(*args)

    def display_parameter_value(self, control_index, value):
        if self.screen_writer:
            args = (control_index, value)
            if args != self.most_recently_used_display_parameter_value_args:
                self.most_recently_used_display_parameter_value_args = args
                self.screen_writer.display_parameter_value(*args)

    def display_notification(self, primary_text="", secondary_text=""):
        if self.screen_writer:
            self.screen_writer.display_notification(primary_text, secondary_text)
