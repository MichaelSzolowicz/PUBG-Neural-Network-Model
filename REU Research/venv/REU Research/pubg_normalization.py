def normalize(values, mini=None, maxi=None):
    if mini is None:
        mini = min(values)
    if maxi is None:
        maxi = max(values)

    for i, value in enumerate(values):
        values[i] = ((value - mini) / (maxi - mini))

    return values


def mirror_axis(values):
    for i in range(len(values)):
        values[i] = abs(values[i] - 1)


def map_limits(map_name):
    """
    Map Limits
        Each map has a unique upper limit for recorded coordinates. Note that not every map's bounds are listed
        in the PUBG API documentation, in these cases a default value of 816000 is returned.
    Returns:
        (int): upper limit
    """

    match map_name:
        case 'erangel', 'ergl':
            return 816000
        case 'miramar', 'mrmr':
            return 816000
        case 'vikendi', 'vknd':
            return 612000
        case 'sanhok', 'snhk':
            return 408000
        case 'karakin', 'krkn':
            return 204000
        case _:
            return 816000
