def cache_led_updates(func):
    """
    Decorator for functions that want to cache all
    led updates and consolidate them into one update
    at the end of the function call.

    Note: Instance of decorated function must have an `led_cache` attribute
          that implements the `start_caching_led_updates` and
          `stop_caching_led_updates` functions.
    """

    def wrapper_cache_led_updates(self, *args, **kwargs):
        self.led_cache.start_caching_led_updates()
        func(self, *args, **kwargs)
        self.led_cache.stop_caching_led_updates()

    return wrapper_cache_led_updates


def detect_status_change(func, *, get_status, on_change):
    """
    Decorator for checking the result of a function and calling the provided callback when it changes

    Note: Will create an attribute named `_status` on the instance.
    """

    def wrapper(self, *args, **kwargs):
        if not hasattr(self, "_status"):
            self._status = None
        previous_status = self._status
        self._status = get_status(self)
        if previous_status is not self._status:
            on_change(self)
        func(self, *args, **kwargs)

    return wrapper


def suppress_unsafe_api_error(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:  # noqa: PIE786
            if "unsafe" not in str(e).lower():
                raise e

    return wrapper
