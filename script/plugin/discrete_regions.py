def make_equal_discrete_regions(*, names):
    """Returns a list of discrete regions as tuples (lower_boundary, name)
    where lower_boundary indicates the start of that region (inclusive)

    Note: Each region will have the same width, except the first and last region which are centered around
          zero and one respectively
    """
    return [((1.0 / (len(names) - 1) / 2) * max(0, index * 2 - 1), name) for index, name in enumerate(names)]


def make_discrete_regions_from_midpoints(*, names, midpoints):
    """
    Makes a list of discrete regions as tuples (lower_boundary, name)
    where lower_boundary indicates the start of that region (inclusive)

    Args:
        names: The name of each region in order
        midpoints: The midpoint of each region in order
    """
    lower_boundaries = [midpoints[0]]
    lower_boundaries.extend([(midpoints[index - 1] + midpoints[index]) / 2 for index in range(1, len(midpoints))])
    return [(lower_boundary, name) for lower_boundary, name in zip(lower_boundaries, names)]
