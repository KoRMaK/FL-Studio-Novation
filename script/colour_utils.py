def scale_colour(values, scalar):
    return tuple([int(value * scalar) for value in values])


def clamp_brightness(values, *, minimum=0, maximum=255):
    r, g, b = values
    brightness = max(r, g, b)

    if maximum < brightness < minimum and brightness != 0:
        target = minimum if brightness < minimum else maximum
        correction = target / brightness
        r = r * correction
        g = g * correction
        b = b * correction
    return r, g, b
