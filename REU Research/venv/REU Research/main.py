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


def import_match_data(id_list, positions_csv_list, map):
    api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NWQ4NWU1MC1jODE3LTAxM2EtYzc4Yi03OWE4NjMxM2U1MTMiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNjU0NTU1MTE5LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InB1YmctZGF0YS1wcm9jIn0.K4JaJpbDJpnkt2zPfbt9L3OASg94B7bCgGrliksa_tI"
    pubg = PUBG(api_key, "pc-na")

    for count, id in enumerate(id_list):
        # This line of code is used if you have the match id of a certain match.
        match = pubg.match(id)

        # This block of code creates a csv file for player positions given the match_id. User must manually enter file
        # location for csv in second parameter.
        telemetry = match.get_telemetry()
        pubg_csv.player_position_csv(telemetry, positions_csv_list[count].format(map), map)
        pubg_csv.fill_csv(positions_csv_list[count].format(map))


def prepare_training_data(positions_csv_list, packets_list, training, map):
    tensor_x = torch.FloatTensor()
    tensor_y = torch.FloatTensor()
    timestamps_list = []

    for i in range(len(positions_csv_list)):
        # for pos, pack in zip()
        x, y, timestamps = pubg_tensors.get_tensors(positions_csv_list[i].format(map), packets_list[i].format(map))

        # Write predictions to a csv if prepping for valuation
        if not training:
            m = model.load()
            prd = m(x)

            # Fill header with generic players
            header = ['timestamp']
            for j in range(105):
                header.append('Player{0}_x'.format(j))
                header.append('Player{0}_y'.format(j))
                header.append('Player{0}_z'.format(j))

            # Title the new predictions file with same time and maps as recording.
            write_file = open('predictions_{}{}.csv'.format(positions_csv_list[i][-17:-6], map), 'w', newline='')
            csv_writer = csv.writer(write_file)
            csv_writer.writerow(header)

            # Fill rows with timestamp, predictions
            list_prd = prd.tolist()
            for j, row in enumerate(list_prd):
                datetimestamp = datetime.datetime.fromtimestamp(float(timestamps[j]))
                write_row = [datetimestamp.astimezone(pytz.timezone('US/Pacific'))]
                for value in row:
                    write_row.append(value)
                csv_writer.writerow(write_row)

        tensor_x = torch.cat((tensor_x, x))
        tensor_y = torch.cat((tensor_y, y))
        timestamps_list.extend(timestamps)

    # This block of code either prepares the data for training the model or for evaluating the predicted coordinates
    if training:
        timestamps_list = preparedata.prepare_data_training(tensor_x, tensor_y, timestamps_list)
    else:
        preparedata.prepare_data_valuation(tensor_x, tensor_y)

    # This block of code creates a csv file for the timestamps
    csv_writer = csv.writer(open('tensor_timestamps.csv', 'w', newline=''))
    for timestamp in timestamps_list:
        csv_writer.writerow([timestamp])


# Main function
def main():
    id_list =               ['490b5eae-0667-452b-aade-32bc6ed54742']
    player_positions_list = ['PlayerPositions/player_pos_062922_1607_{}.csv']
    packets_list =          ['NetworkPackets/packets_062922_1607_{}.json']
    map = 'ergl'

    inp = input('Import match data? y / n: ')
    match inp:
        case 'y':
            import_match_data(id_list, player_positions_list, map)
        case _:
            pass

    inp = input('Prepare data? training / valuation / none: ')
    match inp:
        case 'training':
            prepare_training_data(player_positions_list, packets_list, True, map)
        case 'valuation':
            prepare_training_data(player_positions_list, packets_list, False, map)
        case _:
            pass


if __name__ == "__main__":
    main()
