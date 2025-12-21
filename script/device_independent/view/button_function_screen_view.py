from script.constants import ButtonFunction
from script.device_independent.util_view import View


class ButtonFunctionScreenView(View):
    def __init__(self, action_dispatcher, screen_writer, fl):
        super().__init__(action_dispatcher)
        self.screen_writer = screen_writer
        self.fl = fl

    def handle_TransportRecordStateChangedAction(self, action):
        record_is_enabled = self.fl.transport_is_recording()
        self.screen_writer.display_notification("Record", "On" if record_is_enabled else "Off")

    def handle_TransportPlaybackStateChangedAction(self, action):
        if self.fl.transport_is_playing():
            state = "Play"
        elif self.fl.transport_is_paused():
            state = "Pause"
        else:
            state = "Stop"

        self.screen_writer.display_notification("Transport", state)

    def handle_MetronomeStateChangedAction(self, action):
        metronome_is_enabled = self.fl.metronome_is_enabled()
        self.screen_writer.display_notification("Metronome", "On" if metronome_is_enabled else "Off")

    def handle_FunctionTriggeredAction(self, action):
        if action.function is ButtonFunction.Quantise:
            channel_name = self.fl.get_channel_name(self.fl.selected_channel())
            self.screen_writer.display_notification(channel_name, "Quantise")
        elif action.function is ButtonFunction.Undo:
            self.screen_writer.display_notification("Action Undo")
        elif action.function is ButtonFunction.Redo:
            self.screen_writer.display_notification("Action Redo")
        elif action.function is ButtonFunction.DumpScoreLog:
            self.screen_writer.display_notification("Dump Score Log", "Last 5 Minutes")
