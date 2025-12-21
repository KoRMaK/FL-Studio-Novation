class Timer:
    def __init__(self, action_dispatcher, *, on_finished=None):
        self.action_dispatcher = action_dispatcher
        self.on_finished = on_finished
        self.duration_in_timer_events = 0
        self.number_of_events_passed = self.duration_in_timer_events

    def start(self, duration_in_timer_events):
        self.duration_in_timer_events = duration_in_timer_events
        self.number_of_events_passed = 0
        self.action_dispatcher.subscribe(self)

    def stop(self):
        self.action_dispatcher.unsubscribe(self)

    def finished(self):
        return self.number_of_events_passed >= self.duration_in_timer_events

    def _handle_duration_reached(self):
        self.stop()
        if self.on_finished:
            self.on_finished()

    def handle_TimerEventAction(self, action):
        self.number_of_events_passed += 1
        if self.finished():
            self._handle_duration_reached()
