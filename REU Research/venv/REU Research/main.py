from chicken_dinner.pubgapi import PUBG
import packet_sniffer
import pubg_info
import pubg_csv
import pubg_plots
import pubg_tensors
import preparedata
import csv
import torch
import datetime
import pytz
import model
import torch


def import_match_data(id, positions_csv, map):
    """
    Import Match Data
        Uses chicken_dinner library to retrieve coordinate replay for match id.
    Args:
        id: Match ID
        positions_csv: Path to write predictions to
        map: Map the match was played on, used for normalization
    """
    api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NWQ4NWU1MC1jODE3LTAxM2EtYzc4Yi03OWE4NjMxM2U1MTMiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNjU0NTU1MTE5LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InB1YmctZGF0YS1wcm9jIn0.K4JaJpbDJpnkt2zPfbt9L3OASg94B7bCgGrliksa_tI"
    pubg = PUBG(api_key, "pc-na")

    # This line of code is used if you have the match id of a certain match.
    match = pubg.match(id)

    # This block of code creates a csv file for player positions given the match_id. User must manually enter file
    # location for csv in second parameter.
    telemetry = match.get_telemetry()
    pubg_csv.player_position_csv(telemetry, positions_csv.format(map), map)
    pubg_csv.fill_csv(positions_csv.format(map))


def prepare_training_data(positions_csv, packets, map):
    """
    Prepare Training Data
        Creates tensors with random permutations from position_csv, packets
    Args:
        positions_csv:
        packets:
        map: Map the match was played on, used for normalization
    Returns:
        x: Packet data tensor
        y: Player pos tensor
        timestamps:
    """
    # Get tensors for each file in list, concat results before writing tensors to external file.
    # for pos, pack in zip()
    x, y, timestamps = pubg_tensors.get_tensors(positions_csv.format(map), packets.format(map))
    return x, y, timestamps


def prepare_valuation_data(positions_csv, packets, map):
    """
    Prepare Valuation Data
        Creates tensors from positions_csv, packets.
        Saves predictions for tensors to a csv.
    Args:
        positions_csv:
        packets:
        map: Map the match was played on, used for normalization
    Returns:
        x: Packet data tensor
        y: Player pos tensor
        timestamps:
    """
    # Get tensors for each file in list, concat results before writing tensors to external file.
    x, y, timestamps = pubg_tensors.get_tensors(positions_csv.format(map), packets.format(map))

    # Convert timestamps to date time-timezone format
    timestamps = [datetime.datetime.fromtimestamp(float(timestamp)).astimezone(pytz.timezone('US/Pacific'))
                  for timestamp in timestamps]

    # Create a csv record of the predictions for the given packet
    m = model.load()
    prd = m(x)
    list_prd = prd.tolist()

    write_file = open('predictions_{}{}.csv'.format(positions_csv[-18:-6], map), 'w', newline='')   # New file
    csv_writer = csv.writer(write_file)

    header = pubg_csv.generic_header(105)
    csv_writer.writerow(header)
    pubg_csv.fill_predictions_csv(csv_writer, list_prd, timestamps)
    write_file.close()

    return x, y, timestamps


# Main function
def main():
    id_list =               ['b8419a2f-e824-4d1a-9296-8132c8aa7ba0', '70b2d647-eaf0-492e-a5cc-d6e66192e733', '5295efa3-8032-4071-b0aa-c4c0e5133988', '7d96d03f-7121-477f-b962-54c127509561']
    player_positions_list = ['PlayerPositions/player_pos_071122_1359_{}.csv']
    packets_list =          ['NetworkPackets/packets_071122_1359_{}.json']
    map = 'mrmr'

    inp = input('Import match data? y / n: ')
    if inp == 'y':
        for i, id in enumerate(id_list):
            import_match_data(id, player_positions_list[i], map)
    else:
        pass

    tensor_x = torch.FloatTensor()      # Append tensors & timestamps from each file to these variables
    tensor_y = torch.FloatTensor()
    timestamps_list = []

    inp = input('Prepare data? training / valuation / none: ')
    if inp == 'training':
        for i, file in enumerate(player_positions_list):
            x, y, timestamps = prepare_training_data(file, packets_list[i], map)

            tensor_x = torch.cat((tensor_x, x))
            tensor_y = torch.cat((tensor_y, y))
            timestamps_list.extend(timestamps)
            print(tensor_x.size())

        # Perform final preparation and save tensors to separate file.
        timestamps_list = preparedata.prepare_data_training(tensor_x, tensor_y, timestamps_list)

        # Creates a csv file for the timestamps,
        csv_writer = csv.writer(open('tensor_timestamps.csv', 'w', newline=''))
        for timestamp in timestamps_list:
            datetimestamp = datetime.datetime.fromtimestamp(float(timestamp))
            csv_writer.writerow([datetimestamp.astimezone(pytz.timezone('US/Pacific'))])
    elif inp == 'valuation':
        for i, file in enumerate(player_positions_list):
            x, y, timestamps = prepare_valuation_data(file, packets_list[i], map)

            tensor_x = torch.cat((tensor_x, x))
            tensor_y = torch.cat((tensor_y, y))
            timestamps_list.extend(timestamps)

        # Perform final preparation and save tensors to separate file.
        preparedata.prepare_data_valuation(tensor_x, tensor_y)
    else:
        pass


if __name__ == "__main__":
    main()
