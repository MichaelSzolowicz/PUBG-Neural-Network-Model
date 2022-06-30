from chicken_dinner.pubgapi import PUBG
import packet_sniffer
import pubg_info
import pubg_csv
import pubg_plots
import pubg_tensors
import preparedata
import csv


# Main function
def main():
    api_key = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NWQ4NWU1MC1jODE3LTAxM2EtYzc4Yi03OWE4NjMxM2U1MTMiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNjU0NTU1MTE5LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InB1YmctZGF0YS1wcm9jIn0.K4JaJpbDJpnkt2zPfbt9L3OASg94B7bCgGrliksa_tI"
    match_id = '7139785b-5b4d-46a8-ae39-32563083d4c2'
    player_positions = 'PlayerPositions/player_pos_6_28_22_1358.csv'
    packets = 'NetworkPackets/packets_6_28_22_1358.json'
    pubg = PUBG(api_key, "pc-na")

    # This block of code gets players as well as current season, used to get match id of latest game played by player

    players = pubg.players_from_names(["Mszolo"])
    Mszolo = players[0]
    current_season = pubg.current_season()
    # match_id = pubg_info.get_season_duo_match_ids(Mszolo, current_season)

    # This line of code is used if you have the match id of a certain match.
    match_id = pubg.match(match_id)

    # This block of code creates a csv file for player positions given the match_id. User must manually enter file
    # location for csv in second parameter.
    telemetry = match_id.get_telemetry()
    pubg_csv.player_position_csv(telemetry, player_positions)
    pubg_csv.fill_csv(player_positions)

    # This line of code creates tensors for player positions: x for byte data and y for player positions. It also
    # returns a list of timestamps that match the packet received and player positions at that timestamp
    x, y, timestamps = pubg_tensors.get_tensors(player_positions, packets)

    # This block of code either prepares the data for training the model or for evaluating the predicted coordinates
    # User most comment one out for whatever they are trying to do.
    # timestamps = preparedata.prepare_data_training(x, y, timestamps)
    preparedata.prepare_data_valuation(x, y)

    # This block of code creates a csv file for the timestamps
    csv_writer = csv.writer(open('tensor_timestamps.csv', 'w', newline=''))
    for timestamp in timestamps:
        csv_writer.writerow([timestamp])


if __name__ == "__main__":
    main()
