import csv
import numpy as np
import collections
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import scipy.stats as st


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


def sum_pos_neg(prediction_grid):
    sum_neg = 0
    sum_pos = 0
    for i in prediction_grid:
        for j in i:
            if j < 0:
                sum_neg += j
            else:
                sum_pos += j
    return sum_neg, sum_pos


def map_limits(map_name):
    """
    Map Limits
    Each map has a unique upper limit for recorded coordinates. Note that not every map's bounds are listed
    in the PUBG API documentation, in these cases a default value of 800000 is returned.

    Returns:
        (int): upper limit
    """

    match map_name:
        case 'erangel':
            return 816000
        case 'miramar':
            return 816000
        case 'vikendi':
            return 612000
        case 'sanhok':
            return 408000
        case 'karakin':
            return 204000
        case _:
            return 800000


def extract_coords(file_path, axis, range_min=None, range_max=None, start_time=None, stop_time=None):
    """
    Extract Coords
    Retrieve frames of coordinates along a given axis from a recording file.

    Args:
        file_path (str): location of file to extract from
        axis (str): Axis from which coordinates will be extracted
        range_min (int): Start index for slicing frames from file. Indexing starts from 1 and includes header row.
        range_max (int): Last index for slicing frames from. Indexing starts from 1 and includes header row.
        start_time (str): Start retrieving frames at this timestamp.
        stop_time (str): Stop retrieving frames at this timestamp. This timestamp is not included in returned dictionary.

    Returns:
        coords (dict): Dictionary where keys are timestamps and values are lists of coordinates.
    """
    columns = []
    coords = {}
    start_time_digits = 26      # By default, get timestamps to a specificity of seconds.
    stop_time_digits = 26

    csv_file = open(file_path, 'r')
    csv_reader = csv.reader(csv_file, delimiter=',')

    # Get a list of the column #'s containing the axis of interest.
    for i in csv_reader:
        for column, j in enumerate(i):
            if j[-1] == axis:
                columns.append(column)
        break

    # Get indices of start and stop timestamps.
    # Note that if there are multiple of the same timestamp, the last initial matching timestamp and
    # the first matching stop timestamp are indexed.
    if start_time is not None and stop_time is not None:
        temp_file = open(file_path, 'r')
        temp_reader = csv.reader(temp_file, delimiter=',')

        start_time_digits = len(start_time)
        stop_time_digits = len(stop_time)

        for i, row in enumerate(temp_reader):
            if str(row[0])[:start_time_digits] == start_time:
                range_min = i + 1
            if str(row[0])[:stop_time_digits] == stop_time:
                range_max = i + 1
                break

    # Make dictionary with timestamps as keys and list of coordinates as values.
    # Fill any missing coordinates with zero.
    for count, row in enumerate(csv_reader):
        if range_min is None or range_max is None:
            coords[str(row[0])[:start_time_digits]] = []
        elif (range_min - 2) <= count < (range_max - 2):
            coords[str(row[0])[:start_time_digits]] = []
        else:
            continue
        for i in range(len(columns)):
            if columns[i] > (len(row) - 1):
                coords[str(row[0])[:start_time_digits]].append(.00001)
            elif row[columns[i]] == '' or row[columns[i]] is None:
                coords[str(row[0])[:start_time_digits]].append(.00001)
            else:
                coords[str(row[0])[:start_time_digits]].append(float(row[columns[i]]))

    return coords


def perform_kde(coords_x, coords_y, bandwidth=.2, scale=1, res=100j):
    """
    Perform KDE

    Args:
        coords_x (list):
        coords_y (list):
        bandwidth: width of the kernel
        scale (int): Final size of x, y axes
        res (complex): res^2 is equal to the number of points at which the KDE will be evaluated.
        Higher number results in higher quality image at the cost of performance.

    Returns:
        kernel: Scipy KDE object
        xx: X values at which KDE was tested.
        yy: Y values at which KDE was tested.
        z: Output (height) of KDE at tested points.
    """
    xx, yy = np.mgrid[0:scale:res, 0:scale:res]
    test_positions = np.vstack([xx.ravel(), yy.ravel()])
    coords = np.vstack([coords_x, coords_y])

    kernel = st.gaussian_kde(coords, bw_method=bandwidth)

    z = np.reshape(kernel.evaluate(test_positions).T, xx.shape)

    return kernel, xx, yy, z


def plot_heatmap(z_values, scale=1, timestamp=00, overpred_factor=None, map=None, x=None, y=None, colors=['black']):
    """
    Plot Heatmap

    Args:
        z_values: Heatmap image.
        scale (int): Axes size
        map: background image
        timestamp:
        x: List of x coordinates. Each list contained in list graphed with color of same index in colors.
        y: List of y coordinates. Each list contained in list graphed with x coordinates of corresponding index.
        colors: Graph list x[i] in color colors[i].

    Returns:
        fig:
        ax:
    """
    fig, ax = plt.subplots()

    plt.title('(Prediction Density) - (Actual Coordinate Density)\n' +
              'Overprediction Factor: {}\n'.format(overpred_factor) +
              'Timestamp: {0}'.format(timestamp))
    plt.xlabel('X')
    plt.ylabel('Y')

    ax.set_xlim(0, scale)
    ax.set_ylim(0, scale)

    if map is not None:
        ax.imshow(map, extent=[0, scale, 0, scale])
    im = ax.imshow(np.rot90(z_values), extent=[0, scale, 0, scale], cmap='RdBu', vmin=-1, vmax=1, alpha=.7)
    plt.colorbar(im)

    for i, coords in enumerate(x):
        ax.scatter(x[i], y[i], facecolor=colors[i], s=2)

    return fig, ax


def user_interface():
    recording_csv = 'PlayerPositions\player_pos_6_28_22_1337.csv'
    prediction_csv = 'Predictions\predictions_6_28_22_1337.csv'
    start_time = '2022-06-28 13:44:44'
    stop_time = '2022-06-28 13:54:40'
    map_path = 'Assets\sanhok-map.jpg'
    bandwidth = .2
    scale = 3
    # graph_path = 'Graphs/{}.jpg'
    draw_fig = False

    map = mpimg.imread(map_path)
    limit = map_limits(map_path[7:-8])

    prd_x = extract_coords(prediction_csv, 'x', start_time=start_time, stop_time=stop_time)
    prd_y = extract_coords(prediction_csv, 'y', start_time=start_time, stop_time=stop_time)

    rec_x = extract_coords(recording_csv, 'x', start_time=start_time, stop_time=stop_time)
    rec_y = extract_coords(recording_csv, 'y', start_time=start_time, stop_time=stop_time)
    print(rec_x)
    print(rec_x)

    inp = input('Save figure? y / n / YES_all / NO_all: ')

    # Graph each set of coordinates from extractions
    for count, key in enumerate(rec_x):
        print(key)
        if key in rec_y:
            if key in prd_x:
                if key in prd_y:
                    rec_x[key] = normalize(rec_x[key], 0, limit)    # Prep data / normalize actual coords to map limits
                    rec_y[key] = normalize(rec_y[key], 0, limit)
                    mirror_axis(rec_y[key])     # Prep data / recordings' origin at top left; flip before graphing
                    mirror_axis(prd_y[key])
                    prd_x[key] = [i * scale for i in prd_x[key]]    # Prep data / scaling help make KDE clearer
                    prd_y[key] = [i * scale for i in prd_y[key]]
                    rec_x[key] = [i * scale for i in rec_x[key]]
                    rec_y[key] = [i * scale for i in rec_y[key]]

                    x_coords = [rec_x[key], prd_x[key]]     # Stack recordings/predictions for simpler data management
                    y_coords = [rec_y[key], prd_y[key]]

                    prd_kernel, prd_xx, prd_yy, prd_z = perform_kde(prd_x[key], prd_y[key], .2, scale, 200j)
                    rec_kernel, rec_xx, rec_yy, rec_z = perform_kde(rec_x[key], rec_y[key], .2, scale, 200j)

                    sum_neg, sum_pos = sum_pos_neg(prd_z - rec_z)
                    overpred_factor = normalize([sum_pos], mini=0, maxi=4400)
                    # print('Overprediction factor: ', overpred_factor)

                    fig, ax = plot_heatmap((prd_z - rec_z), scale, map=map, timestamp=key, overpred_factor=overpred_factor, x=x_coords, y=y_coords, colors=['red', 'blue'])

                    file_timestamp = key.translate({ord(c): None for c in '- :'})   # Reformat timestamp for filename
                    match inp:
                        case 'y':
                            plt.savefig('Graphs/heatmap_{}'.format(file_timestamp), dpi=200)
                            if draw_fig:
                                plt.show()
                            inp = input('Save figure? y / n / YES_all / NO_all: ')
                        case 'YES_all':
                            plt.savefig('Graphs/heatmap_{}'.format(file_timestamp), dpi=200)
                            if draw_fig:
                                plt.show()
                        case 'n':
                            if draw_fig:
                                plt.show()
                            inp = input('Save figure? y / n / YES_all / NO_all: ')
                        case _:
                            if draw_fig:
                                plt.show()
                            pass
                    plt.close()


user_interface()
