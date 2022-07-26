import csv
import numpy as np
import collections
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import scipy.stats as st
import pubg_normalization as pubg_norm
import datetime

fully_overpredicted = 4400
graphs_path = 'Graphs/heatmap_{}.jpg'


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

def string_to_datetime(timestamp):
    """
    String to Datetime
        Assumes string in format '1111-11-11 11:11:11.111111-1:11'
    Args:
        timestamp:
    Return:
         datetime:
    """
    year = int(timestamp[:4])
    month = int(timestamp[5:7])
    day = int(timestamp[8:10])
    hr = int(timestamp[11:13])
    mins = int(timestamp[14:16])
    sec = int(timestamp[17:19])
    mill = 0

    if timestamp[20:26] != '':      # If milliseconds exist in string, use milliseconds
        mill = int(timestamp[20:26])

    datetimestamp = datetime.time(hr, mins, sec, mill)
    return datetime.datetime.combine(datetime.date(year, month, day), datetimestamp)


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
    start_time_digits = 19      # By default, get timestamps to a specificity of seconds.
    stop_time_digits = 19

    csv_file = open(file_path, 'r')
    csv_reader = csv.reader(csv_file, delimiter=',')

    # Get a list of the column #'s containing the axis of interest.
    for i in csv_reader:
        for num, j in enumerate(i):
            if j[-1] == axis:
                columns.append(num)
        break

    # Get indices of start and stop timestamps.
    if start_time is not None and stop_time is not None:
        temp_file = open(file_path, 'r')
        temp_reader = csv.reader(temp_file, delimiter=',')

        start_time_digits = len(start_time)
        stop_time_digits = len(stop_time)

        range_min = None

        for i, row in enumerate(temp_reader):
            if row[0][:start_time_digits] == start_time:
                range_min = i + 1
            if row[0][:stop_time_digits] == stop_time:
                range_max = i + 1
                break

    # Make dictionary with timestamps as keys and list of coordinates as values.
    # Fill any missing coordinates with .00001.
    for count, row in enumerate(csv_reader):
        if range_min is None or range_max is None:
            coords[str(row[0])[:-6]] = []
        elif (range_min - 2) <= count < (range_max - 2):
            coords[str(row[0])[:-6]] = []
        else:
            continue
        for i in range(len(columns)):
            if columns[i] > (len(row) - 1):
                coords[str(row[0])[:-6]].append(.00001)
            elif row[columns[i]] == '' or row[columns[i]] is None:
                coords[str(row[0])[:-6]].append(.00001)
            else:
                coords[str(row[0])[:-6]].append(float(row[columns[i]]))

    return coords


def perform_kde(coords_x, coords_y, bandwidth=.2, scale=1, res=100j):
    """
    Perform KDE
    Args:
        coords_x (list):
        coords_y (list):
        bandwidth: width of the kernel
        scale (int): Final size of x, y axes
        res (complex): Determines number of tiles over which the KDE will be evaluated.
                       Higher number results in higher quality image at the cost of performance.
    Returns:
        kernel: Scipy KDE object
        xx: Tiles X value at which KDE was tested.
        yy: Tiles Y at which KDE was tested.
        z: Output (height) of KDE at tested tiles.
    """

    xx, yy = np.mgrid[0:scale:res, 0:scale:res]
    test_positions = np.vstack([xx.ravel(), yy.ravel()])
    coords = np.vstack([coords_x, coords_y])

    kernel = st.gaussian_kde(coords, bw_method=bandwidth)

    z = np.reshape(kernel.evaluate(test_positions).T, xx.shape)

    return kernel, xx, yy, z


def plot_heatmap(z_values, scale=1, prd_timestamp=00, rec_timestamp=00, overpred_factor=None, map=None, x=None, y=None, colors=['black']):
    """
    Plot Heatmap
    Args:
        z_values: Heatmap image grid.
        scale: Axes size
        map: background image
        prd_timestamp:
        rec_timestamp:
        x: List of x coordinates. Each list contained in list graphed with color of same index in colors.
        y: List of y coordinates. Each list contained in list graphed with x coordinates of corresponding index.
        colors: Graph list x[i] in color colors[i].
    Returns:
        fig:
        ax:
    """
    fig, ax = plt.subplots()

    plt.title('Prediction Timestamp: {0}\n'.format(prd_timestamp) +
              'Recording Timestamp: {0}\n'.format(rec_timestamp) +
              'Overprediction Factor: {0}'.format(overpred_factor), fontsize=10)
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


def user_interface(recording_csv, prediction_csv, start_time, stop_time, map_path, bandwidth=.2, scale=3, draw_fig=False):
    """
    User Interface
        Performs necessary steps to generate heatmaps, using other functions from pubg_csv.
        Extracts coordinates from recording and prediction files, matches recording and prediction
        timestamps, graphs heatmap, and gives user option to save or discard maps.
    Args:
        recording_csv:
        prediction_csv:
        start_time:
        stop_time:
        map_path:
        bandwidth: Width of the kernel used in KDE
        scale: Size of the generated heatmap
        draw_fig: Whether to show heatmap when generating

    Returns:
        sum_overpred_factor: The sum of each map's overprediction factor
        loops: The number of heatmaps successfully generated
    """
    map = mpimg.imread(map_path)
    limit = pubg_norm.map_limits(map_path[7:-8])

    # Later on, KDE functions will take x/y coords as separate lists.
    prd_x_extraction = extract_coords(prediction_csv, 'x', start_time=start_time, stop_time=stop_time)
    prd_y_extraction = extract_coords(prediction_csv, 'y', start_time=start_time, stop_time=stop_time)
    for key in prd_y_extraction:
        pubg_norm.mirror_axis(prd_y_extraction[key])    # Game uses top left origin, heatmap uses bottom left.
        prd_x_extraction[key] = [i * scale for i in prd_x_extraction[key]]
        prd_y_extraction[key] = [i * scale for i in prd_y_extraction[key]]
    rec_x_extraction = extract_coords(recording_csv, 'x', start_time=start_time, stop_time=stop_time)
    rec_y_extraction = extract_coords(recording_csv, 'y', start_time=start_time, stop_time=stop_time)
    for key in rec_x_extraction:
        pubg_norm.mirror_axis(rec_y_extraction[key])        # Game uses top left origin, heatmap uses bottom left.
        rec_x_extraction[key] = [i * scale for i in rec_x_extraction[key]]
        rec_y_extraction[key] = [i * scale for i in rec_y_extraction[key]]

    # Variables used for loop control
    sum_overpred_factor = 0
    loops = 0
    graph_rec = ''
    prev_graph_rec = ''

    inp = input('Save figure? y / n / YES_all / NO_all: ')

    for graph_prd in prd_x_extraction:
        smallest_diff = datetime.datetime(9999, 1, 1) - string_to_datetime(graph_prd)
        smallest_diff = abs(smallest_diff.total_seconds())

        # For every key in predictions, find the closest key in recording
        for key in rec_x_extraction:
            diff = string_to_datetime(key) - string_to_datetime(graph_prd)
            diff = abs(diff.total_seconds())

            if diff <= smallest_diff:
                smallest_diff = diff
                graph_rec = key
            else:
                break

        # Prevents comparison of multiple predictions against same recording.
        if graph_rec == prev_graph_rec:
            pass    # Use 'continue' to prevent graphing prds which correspond to rec timestamps already graphed.
                    # Use 'passs' to graph every prd.
        elif prev_graph_rec != '':
            del rec_x_extraction[prev_graph_rec]
            del rec_y_extraction[prev_graph_rec]
        prev_graph_rec = graph_rec

        rec_x = rec_x_extraction[graph_rec]     # KDE Functions take x/y coords as separate lists.
        rec_y = rec_y_extraction[graph_rec]
        prd_x = prd_x_extraction[graph_prd]
        prd_y = prd_y_extraction[graph_prd]

        prd_kernel, prd_xx, prd_yy, prd_z = perform_kde(prd_x, prd_y, .2, scale, 200j)
        rec_kernel, rec_xx, rec_yy, rec_z = perform_kde(rec_x, rec_y, .2, scale, 200j)

        sum_neg, sum_pos = sum_pos_neg(prd_z - rec_z)
        overpred_factor = pubg_norm.normalize([sum_pos], mini=0, maxi=fully_overpredicted)
        sum_overpred_factor += overpred_factor[0]
        loops += 1

        x_coords = [rec_x, prd_x]  # plot_heatmaps takes lists of coordinates to simplify function signature
        y_coords = [rec_y, prd_y]
        fig, ax = plot_heatmap((prd_z - rec_z), scale, map=map, prd_timestamp=graph_prd, rec_timestamp=graph_rec,
                               overpred_factor=overpred_factor,  x=x_coords, y=y_coords, colors=['red', 'blue'])
        print('Plotted prd:', graph_prd)

        file_timestamp = str(graph_prd).translate({ord(c): '_' for c in '- :.'})  # Reformat timestamp for filename
        if inp == 'y':
            plt.savefig(graphs_path.format(file_timestamp), dpi=200)
            if draw_fig:
                plt.show()
            inp = input('Save figure? y / n / YES_all / NO_all: ')
        elif inp == 'YES_all':
            plt.savefig(graphs_path.format(file_timestamp), dpi=200)
            if draw_fig:
                plt.show()
        elif inp == 'n':
            if draw_fig:
                plt.show()
            inp = input('Save figure? y / n / YES_all / NO_all: ')
        else:
            if draw_fig:
                plt.show()
            pass
        plt.close()
    return sum_overpred_factor, loops


recording_csv = ['PlayerPositions/player_pos_7_22_1134.csv']
prediction_csv = ['Predictions/predictions_7_22_1134.csv']
start_time = [None]
stop_time  = [None]
map_path = ['Assets/erangel-map.jpg']

sum_overpred_factor = 0
total_loops = 0

for i, file in enumerate(recording_csv):
    overpred_factor, loops = user_interface(recording_csv[i], prediction_csv[i], start_time[i], stop_time[i], map_path[0])
    sum_overpred_factor += overpred_factor
    total_loops += loops

print("Total Overprediction Factor: ", sum_overpred_factor / total_loops)
