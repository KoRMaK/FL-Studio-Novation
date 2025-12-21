from itertools import islice

from script.constants import Faders


class ControlChangeRateLimiter:
    def __init__(
        self,
        action_dispatcher,
        *,
        number_of_controls=8,
        frequency_threshold=10,
        minimum_sampling_time=1,
        maximum_sampling_time=30,
        max_skips_per_control=2,
        min_control_value=0.0,
        max_control_value=1.0,
    ):
        self.action_dispatcher = action_dispatcher
        self.number_of_controls = number_of_controls
        self.control_change_request_counter = {}
        self.skipped_change_requests_per_control = {}
        self.timer_ticks = 0
        self.frequency_threshold = frequency_threshold
        self.minimum_sampling_time = minimum_sampling_time
        self.maximum_sampling_time = maximum_sampling_time
        self.max_skips_per_control = max_skips_per_control
        self.min_control_value = min_control_value
        self.max_control_value = max_control_value

    def start(self):
        self.action_dispatcher.subscribe(self)

    def stop(self):
        self.action_dispatcher.unsubscribe(self)

    def handle_TimerEventAction(self, action):
        self.timer_ticks += 1

    def forward_control_change_event(self, destination, value):
        if destination not in self.control_change_request_counter:
            self.control_change_request_counter[destination] = 0
        self.control_change_request_counter[destination] += 1

        if not self._reached_minimum_sampling_time():
            self._reset_skip_counter(destination)
            return True

        if self._exceeds_maximum_sampling_time():
            self._reset_counters()
            return True

        if self._is_edge_value(value):
            self._reset_skip_counter(destination)
            return True

        if self._exceeds_desired_change_frequency(destination) and not self._reached_maximum_of_skipped_events(
            destination
        ):
            self._increase_skip_counter(destination)
            return False
        self._reset_skip_counter(destination)
        return True

    def reset(self):
        self._reset_counters()

    def _increase_skip_counter(self, destination):
        if destination not in self.skipped_change_requests_per_control:
            self.skipped_change_requests_per_control[destination] = 0
        self.skipped_change_requests_per_control[destination] += 1

    def _reset_skip_counter(self, destination):
        self.skipped_change_requests_per_control[destination] = 0

    def _control_change_frequency(self, destination):
        return self.control_change_request_counter[destination] / self.timer_ticks

    def _exceeds_desired_change_frequency(self, destination):
        return self._control_change_frequency(destination) * self._number_of_active_faders > self.frequency_threshold

    def _reached_maximum_of_skipped_events(self, destination):
        if destination not in self.skipped_change_requests_per_control:
            return False
        return self.skipped_change_requests_per_control[destination] > self.max_skips_per_control

    def _reached_minimum_sampling_time(self):
        return self.timer_ticks > self.minimum_sampling_time

    def _exceeds_maximum_sampling_time(self):
        return self.timer_ticks > self.maximum_sampling_time

    def _is_edge_value(self, value):
        return value == self.min_control_value or value == self.max_control_value

    @property
    def _number_of_active_faders(self):
        active_controls = (
            active_control for active_control in self.control_change_request_counter if active_control != 0
        )
        return len(list(islice(active_controls, Faders.NumRegularFaders.value)))

    def _reset_counters(self):
        self.control_change_request_counter.clear()
        self.skipped_change_requests_per_control.clear()
        self.timer_ticks = 0
