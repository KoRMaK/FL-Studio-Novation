from util.math import clamp


class ValueWithRange:
    def __init__(self, *, lower_bound=0, upper_bound):
        """
        Args:
            lower_bound: The lowest possible value.
            upper_bound: The highest possible value.
        """
        self.value = lower_bound
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def increment(self):
        """
        Increment this value by one; Bounded by the upper and lower bound.
        Returns:
            True, if this caused the value to change.
        """
        if self.reached_upper_bound():
            return False
        return self.set_value(self.value + 1)

    def decrement(self):
        """
        Decrement this value by one; Bounded by the upper and lower bound.
        Returns:
            True, if this caused the value to change.
        """
        if self.reached_lower_bound():
            return False
        return self.set_value(self.value - 1)

    def set_value(self, new_value):
        """
        Set value to a specific new value.

        Args:
            new_value: The new value to set value to.

        Returns:
            True, if this caused the value to change.
        """
        old_value = self.value
        self.value = clamp(new_value, self.lower_bound, self.upper_bound)
        return self.value != old_value

    def set_range(self, *, lower_bound=0, upper_bound):
        """
        Sets the range this value can inhibit.

        Args:
            lower_bound: The lowest possible value.
            upper_bound: The highest possible value.

        Returns:
            True, if this caused the value to change.
        """
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        return self.set_value(self.value)

    def reached_lower_bound(self):
        """Return True, if this value has reached the lower bound of the set range"""
        return self.value == self.lower_bound

    def reached_upper_bound(self):
        """Return True, if this value has reached the upper bound of the set range"""
        return self.value == self.upper_bound
