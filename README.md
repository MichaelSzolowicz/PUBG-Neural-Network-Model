# Neural Network Model to Predict Player Positions in PUBG
This is a research project that was originally conducted with the REU in Big Data and Cybersecurity in Cal Poly Pomona. The goal of this project is to train a neural network model to predict player positions using network packets.

The current high level workflow looks like this:

- To train the model, collect network packets using wireshark and export jsons from the records.
- Use [main.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/main.py) to retrieve match recordings and create tensors from the packets.
- Use [trainmodel.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/trainmodel.py) to train the model.
- [pubg_heatmaps.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/pubg_heatmaps.py) is designed to help validate the results with more detail.
- PyGame ( [pubg_pygame_app.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/pubg_pygame_app.py)) and Scapy ([packet_sniffer.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/packet_sniffer.py))
  are used to display predictions during a match in real time.

This project uses the Chicken Dinner library from Python and is written entirely in Python.
Information on the chicken-dinner library can be found here:  [ReadTheDocs.io](https://chicken-dinner.readthedocs.io/en/latest/#) & [Github Source Code](https://github.com/crflynn/chicken-dinner/blob/master/docs/index.rst)

## Github File Structure
All important scripts are found in the REU_Project/REU Research/venv/[REU Research](https://github.com/Jorge626/REU_Project/tree/main/REU%20Research/venv/REU%20Research) directory.
- [main.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/main.py) is where the player position and network packets are turned into tensors to be used in training/evaluating the model (may need your own API key to run some code)
- [model.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/model.py) is the neural network model
- [packet_sniffer.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/packet_sniffer.py) is used in the PyGame tool to continuously sniff packets
- [preparedata.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/preparedata.py) creates random permutations from tensors and saves them for later training.
- [pubg_csv.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/pubg_csv.py) is what is used to create CSV files for player positions
- [pubg_heatmaps.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/pubg_heatmaps.py) Generate heatmaps comparing actual game coordinates to records of predicted coordinates.
- [pubg_info.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/pubg_info.py) is only used for getting information from chicken-dinner library
- [pubg_hormalization.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/pubg_normalization.py) Stores upper limits for a variety of pubg maps, useful when normalizing.
- [pubg_plots.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/pubg_plots.py) plots the player positions on a line graph (used for visualization)
- [pubg_pygame_app.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/pubg_pygame_app.py) is the PyGame application currently in development to predict player positions using the neural network model
- [pubg_tensors.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/pubg_tensors.py) is used to create tensors from player position CSV files and JSON network packet files from WireShark
- [trainmodel.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/trainmodel.py)  is used to train, evaluate, and plot the model

## Collecting Data
Data can be collected using wireshark. After recording net traffic during a match, you can save the wireshark
file then use File->Export Packet Dissections to save the packets as a json file.

## Parsing Replay Files
Replay files can be extracted in [main.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/main.py). Go to the top of main(), Enter the match IDs, 
paths where you would like to save the  replays, and maps the matches were played on, 
then enter 'y' when the program prompts you import match data.

Player positions are saved into a CSV file which are then used to create tensors to train/evaluate the model.

The map name is important because it is used to normalize the recorded coordinates. The program uses 4 letter
abbreviations of each full name, which are as follows:
- 'Miramar' -> 'mrmr'
- 'Erangel' -> 'ergl'
- 'Vikendi' -> 'vknd'
- 'Sanhok'  -> 'snhk'
- 'Karakin' -> 'krkn'

## Training Model
[main.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/main.py) is also used to create tensors for traning the model. Enter the player position csv files and corresponding 
network json files at the top of main(). Additionally enter the map the matches were played on. 

After running [main.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/main.py), you will be prompted to either prepare training or valuation data, or none at all.

- Note that when you prepare valuation data, the program will also produce a csv of predicted locations using
the current model. This can be used after training the model to generate prediction files for heatmap evaluation.
- Note that the map name you enter will be used to construct the name of any generated csv file when evaluating.
 
## Heatmap Validation
[pubg_heatmaps.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/pubg_heatmaps.py) works similar to [main.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/main.py). You enter the recording csv and corresponding prediction csv you would
like to graph at the top of main(). Additionally, start_time and stop_time can be used to list the first and last
timestamps you would like to graph from each recording & prediction file. map_path lists the maps you would
like to draw the resulting heatmaps over.

## PyGame
The PyGame app makes real time predictions based on packets collected by Scapy. 
- [packet_sniffer.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/packet_sniffer.py) collects the packets.
- [pubg_plots.py](https://github.com/MichaelSzolowicz/PUBG-Neural-Network-Model/blob/main/REU%20Research/venv/REU%20Research/pubg_plots.py) takes the packets and draws the model's predictions over an image of the game map.
