import csv
import datetime
import pytz
import os


# Creates or updates a record of predicted positions.
def record_prediction_csv(file_name, timestamp, predictions):
    # Create a csv file and fill with generic headers if csv file path does not yet exist.
    header = ['timestamp']
    count = 0
    if not os.path.exists(file_name):
        while count < 100:
            header.append('Player{0}_x'.format(count))
            header.append('Player{0}_y'.format(count))
            count += 1
        write_file = open(file_name, 'w', newline='')
        csv_writer = csv.DictWriter(write_file, fieldnames=header, restval="")
        csv_writer.writeheader()
        write_file.close()
    # Else append a new timestamp and associated predictions to existing csv file.
    else:
        new_file = open(file_name, 'a', newline='')
        csv_writer = csv.writer(new_file)
        print('TIMESTAMP', timestamp)
        timestamps = [timestamp.astimezone(pytz.timezone('US/Pacific'))]
        for prediction in predictions:
            timestamps.append(prediction[0])
            timestamps.append(prediction[1])
        csv_writer.writerow(timestamps)


# Creates a csv file of player positions given telemetry object
def player_position_csv(telemetry, csv_file_name):
    csv_header = ['timestamp']

    """
    From the chicken_dinner source for filter_by("log_player_positions"):
        Returns a dict of players positions up to death with keys being player
        names and values being a list of tuples. Each tuple has four elements
        being (t, x, y, z) coordinates where t is taken from the event
        timestamps.
    """
    player_positions = telemetry.filter_by("log_player_position")
    characters = []
    timestamps = []
    timestamps_GMT = []
    for players in player_positions:
        current_character_name = players.character.name
        if current_character_name not in characters:
            characters.append(current_character_name)
            csv_header.append('{0}_x'.format(current_character_name))
            csv_header.append('{0}_y'.format(current_character_name))
            csv_header.append('{0}_z'.format(current_character_name))
        timestamp = players.timestamp
        year = int(timestamp[:4])
        month = int(timestamp[5:7])
        day = int(timestamp[8:10])
        hr = int(timestamp[11:13])
        mins = int(timestamp[14:16])
        sec = int(timestamp[17:19])
        mill = int(timestamp[20:23])
        dt = datetime.datetime(year, month, day, hr, mins, sec, mill, tzinfo=pytz.UTC)
        dt_pdt = dt.astimezone(pytz.timezone('US/Pacific'))
        if dt_pdt not in timestamps:
            timestamps.append(dt_pdt)
            timestamps_GMT.append(timestamp)

    new_file = open(csv_file_name, 'w', newline='')
    csv_writer = csv.DictWriter(new_file, fieldnames=csv_header, restval="")
    csv_writer.writeheader()

    for timestamp in timestamps:
        csv_writer.writerow({'timestamp': timestamp})

    new_file.close()
    csv_reader = csv.reader(open(csv_file_name))
    csv_list = list(csv_reader)

    # Moves character positions from player_positions dictionary to csv_list in order to prepare for writing.
    for timestamp in timestamps_GMT:
        for players in player_positions:
            if players.timestamp == timestamp:
                character_index = characters.index(players.character.name)
                start_index = (character_index * 2) + (character_index + 1)
                csv_list[timestamps_GMT.index(timestamp) + 1][start_index] = players.character.location.x
                csv_list[timestamps_GMT.index(timestamp) + 1][start_index + 1] = players.character.location.y
                csv_list[timestamps_GMT.index(timestamp) + 1][start_index + 2] = players.character.location.z

    csv_writer = csv.writer(open(csv_file_name, 'w', newline=''))
    csv_writer.writerows(csv_list)
    return csv_file_name


# Updates csv file so that the csv file has previous known player positions
def fill_csv(file_name):
    csv_reader = csv.reader(open(file_name))
    csv_list = list(csv_reader)

    for rows in range(2, len(csv_list)):
        for columns in range(len(csv_list[rows])):
            if csv_list[rows][columns] == '' and csv_list[rows - 1][columns] != '':
                csv_list[rows][columns] = csv_list[rows - 1][columns]

    csv_writer = csv.writer(open(file_name, 'w', newline=''))
    csv_writer.writerows(csv_list)
