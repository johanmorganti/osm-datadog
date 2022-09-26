from os import path
import pickle
from time import sleep
import requests
import gzip
import xml.etree.ElementTree as ET
import yaml
import json

from osmUtils import *

FILENAME = "previous_sequence.pk"
SLEEP_SECONDS = 15

def process_sequence(sequence_number):
    sequence_number_adjusted = str(sequence_number).rjust(9, "0")
    sequence_url = "https://planet.osm.org/replication/changesets/" + sequence_number_adjusted[0:3] + "/" + sequence_number_adjusted[3:6] + "/" + sequence_number_adjusted[6:9] + ".osm.gz"
    try:
        request_sequence = requests.get(sequence_url, stream=True)
    except:
        print("Error trying to fetch sequence : " + sequence_url)
    xml_sequence = ET.fromstring(gzip.decompress(request_sequence.raw.read()))

    list_changesets = []

    for changeset in xml_sequence:
        list_changesets.append(json_from_xml_changeset(changeset))

    return list_changesets

def main():
    print("Starting")

    # Get last sequence available
    request_state = requests.get("https://planet.osm.org/replication/changesets/state.yaml", stream=True)
    planet_state = yaml.load(request_state.raw.read(),Loader=yaml.FullLoader)

    last_sequence_available = planet_state["sequence"]

    # load the last sequence from the last run
    if path.exists(FILENAME):
        with open(FILENAME, 'rb') as fi:
            last_sequence_processed = pickle.load(fi)
    else:
        # For the first run, send only the last sequence available
        last_sequence_processed = last_sequence_available

    list_logs = []
    number_sequences = 0

    for sequence_number in range(last_sequence_processed, last_sequence_available):
        number_changesets = 0
        for changeset in process_sequence(sequence_number):
            list_logs.append(create_log(json.dumps(changeset)))
            number_changesets = number_changesets +1

        list_logs.append(create_log(str(number_changesets) + " changesets in sequence " + str(sequence_number),service="osm-to-datadog-debug"))
        number_sequences = number_sequences +1

    list_logs.append(create_log("Processed " + str(number_sequences) + " sequences.",service="osm-to-datadog-debug"))

    send_logs(list_logs)

    # dump lastest sequence for next runs
    with open(FILENAME, 'wb') as fi:
        pickle.dump(last_sequence_available, fi)

    print("Done, processsed {} sequences.\n".format(number_sequences))

if __name__ == '__main__':
    while(True):
        try:
            main()
            sleep(SLEEP_SECONDS)
        except Exception as e:
            print("Error trying to process Sequence: ", e)