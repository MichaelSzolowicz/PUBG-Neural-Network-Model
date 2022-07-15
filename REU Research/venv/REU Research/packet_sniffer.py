import scapy.all as scapy
import model, torch
# from scapy.layers import http
import datetime
import pubg_csv
import pytz

coordinates = []
timestamp = datetime.datetime

# Port used in training: udp port 4380 or udp portrange 27000-27040
# Full PUBG ports: tcp portrange 27015-27030 or tcp portrange 27037 or udp port 4380 or udp portrange 27000-
# or udp port 27036

# Port ranges that produce output as of June 2022. Note that output is erratic.
# udp portrange 6999-8000
# udp portrange 6999-8000 or tcp portrange 27000-27040
# udp portrange 7000-7999

# This arg list also produce output as of June 2022
# count=1, filter="tcp portrange 27015-27030 or tcp portrange 27037 or udp port 4380 or "
# "udp portrange 27000-27031 or udp port 27036", timeout=10


def main():
    global coordinates
    global timestamp
    print('Packet Sniffer Sniffs')
    m = model.load()
    while True:
        packet = scapy.sniff(count=1, filter='udp portrange 7000-7999', iface='Ethernet')
        coordinates = get_predictions(m, packet)
        if coordinates is not None:
            timestamp = get_timestamp(packet).astimezone(pytz.timezone('US/Pacific'))
            print('TIMESTAMP', timestamp)
            print('COORD', coordinates)
            pubg_csv.append_predictions_csv('Predictions/predictions.csv', [coordinates], [timestamp])



def get_predictions(m, packet):
    local_ip = scapy.get_if_addr(scapy.conf.iface)
    packet.hexdump()

    if packet[0].payload.src != local_ip:
        print("You received a packet!")
        data = packet[0].payload.payload.payload.load
        if 756 > len(data) > 100:
            byte_data = []
            for bits in data:
                bit = float(bits)
                bit /= 240.0
                byte_data.append(bit)
            if len(byte_data) < 756:
                for j in range(756 - len(byte_data)):
                    byte_data.append(float(0.0))
            tensor = torch.FloatTensor(byte_data)
            prediction = m(tensor).tolist()
            coordinates = []
            for i in range(0, len(prediction), 3):
                x = prediction[i]
                y = prediction[i + 1]
                z = prediction[i + 2]
                if x > 0.0001 and y > 0.0001 and z > 0.0001:
                    coordinates.append(x)
                    coordinates.append(y)
                    coordinates.append(z)
            return coordinates
    else:
        print("You sent a packet!")


def get_timestamp(packets):
    for packet in packets:
        timestamp = datetime.datetime.fromtimestamp(packet.time)
    return timestamp


if __name__ == "__main__":
    main()
