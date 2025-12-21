def clamp(value, min_value, max_value):
    """
    Clamp `value` to the range: `min_value <= value <= max_value`.

    If `value` is below `min_value`, `min_value` will be returned.

    If `value` is above `max_value`, `max_value` will be returned.

    Otherwise `value` will be returned unaltered.
    """
    return max(min(value, max_value), min_value)


# Takes a normalised unidirectional value (0.0 <= normalised_uni_value <= 1.0)
# and converts it to it's normalised bidirectional equivalent (-1.0 <= normalised_uni_value <= 1.0)
def normalised_unipolar_to_bipolar(normalised_uni_value):
    return (normalised_uni_value * 2.0) - 1.0


def normalise(*, value, lower_bound, upper_bound):
    return (value - lower_bound) / (upper_bound - lower_bound)
