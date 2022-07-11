from chicken_dinner.pubgapi import PUBG
import packet_sniffer
import pubg_info
import pubg_csv
import pubg_plots
import pubg_tensors
import preparedata
import csv
import torch


def import_match_data(id_list, positions_csv_list):
    api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NWQ4NWU1MC1jODE3LTAxM2EtYzc4Yi03OWE4NjMxM2U1MTMiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNjU0NTU1MTE5LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InB1YmctZGF0YS1wcm9jIn0.K4JaJpbDJpnkt2zPfbt9L3OASg94B7bCgGrliksa_tI"
    pubg = PUBG(api_key, "pc-na")

    for count, id in enumerate(id_list):
        # This line of code is used if you have the match id of a certain match.
        match = pubg.match(id)

        # This block of code creates a csv file for player positions given the match_id. User must manually enter file
        # location for csv in second parameter.
        telemetry = match.get_telemetry()
        pubg_csv.player_position_csv(telemetry, positions_csv_list[count])
        pubg_csv.fill_csv(positions_csv_list[count])


def prepare_training_data(positions_csv_list, packets_list, training):
    tensor_x = torch.FloatTensor()
    tensor_y = torch.FloatTensor()
    timestamps_list = []

    for i in range(len(positions_csv_list)):
       # for pos, pack in zip()
        x, y, timestamps = pubg_tensors.get_tensors(positions_csv_list[i], packets_list[i])
        tensor_x = torch.cat((tensor_x, x))
        tensor_y = torch.cat((tensor_y, y))
        timestamps_list.extend(timestamps)

    # This block of code either prepares the data for training the model or for evaluating the predicted coordinates
    if training:
        timestamps_list = preparedata.prepare_data_training(tensor_x, tensor_y, timestamps_list)
    else:
        preparedata.prepare_data_valuation(x, y)

    # This block of code creates a csv file for the timestamps
    csv_writer = csv.writer(open('tensor_timestamps.csv', 'w', newline=''))
    for timestamp in timestamps_list:
        csv_writer.writerow([timestamp])


# Main function
def main():
    id_list = ['490b5eae-0667-452b-aade-32bc6ed54742', 'bbba3d1c-3d9e-457e-9c3d-59f80b330e3c']
    player_positions_list = ['PlayerPositions/player_pos_6_29_22_1607.csv', 'PlayerPositions/player_pos_6_29_22_1626.csv']
    packets_list = ['NetworkPackets/packets_6_29_22_1607.json', 'NetworkPackets/packets_6_29_22_1626.json']

    inp = input('Import match data? y / n: ')
    match inp:
        case 'y':
            import_match_data(id_list, player_positions_list)
        case _:
            pass

    inp = input('Prepare data? training / valuation / none: ')
    match inp:
        case 'training':
            prepare_training_data(player_positions_list, packets_list, True)
        case 'valuation':
            prepare_training_data(player_positions_list, packets_list, False)
        case _:
            pass


if __name__ == "__main__":
    main()
