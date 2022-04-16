from osmUtils import *

import requests
import xml.etree.ElementTree as ET
from os import path
import pickle
import json
import os

from datadog_api_client.v2.models import *

FILENAME = "previous_max_changeset.pk"

def get_last_changesets():
    ## Based on the latest version of OSM API : https://wiki.openstreetmap.org/wiki/API_v0.6
    url = "https://api.openstreetmap.org/api/0.6/changesets"

    response = requests.get(url)

    xml = ET.fromstring(response.text)

    # Get the latest changeset IDs
    # XML is in the form of 
    """ 
    <osm>
    <changeset id="113928427" created_at="2021-11-18T06:17:42Z" open="false" comments_count="0" changes_count="6" closed_at="2021-11-18T06:17:44Z" min_lat="15.3384649" min_lon="-91.8697209" max_lat="15.3386183" max_lon="-91.8694203" uid="12026398" user="<redacted>">
    <tag k="changesets_count" v="73"/>
    [...] # More k,v tags
    </changeset>
    <changeset id="113928426" created_at="2021-11-18T06:17:42Z" open="false" comments_count="0" changes_count="11" closed_at="2021-11-18T06:17:43Z" min_lat="-23.6402734" min_lon="47.3068178" max_lat="-23.6387451" max_lon="47.3096663" uid="13571396" user="<redated>">
    <tag k="changesets_count" v="2200"/>
    [...] # More k,v tags
    </changeset>
    [...] # more changesets
    </osm>
    """
    return xml

def main():
    xml_last_cs = get_last_changesets()

    latest_changeset = int(xml_last_cs[0].attrib['id'])
    last_run_cs_number = 0
    # load the last changeset from the last run
    if path.exists(FILENAME):
        with open(FILENAME, 'rb') as fi:
            last_run_cs_number = pickle.load(fi)

    list_logs = []
    list_changeset_processed = []
    list_changeset_skipped = []
    
    intro_message = "Number of changesets to load : " + str(latest_changeset - last_run_cs_number) + ". From " + str(last_run_cs_number) + " to " + str(latest_changeset) 
    list_logs.append(create_log(intro_message, service="osm-to-datadog-debug"))

    for changeset in xml_last_cs:
        changeset_id = int(changeset.attrib["id"])
        if changeset_id <= last_run_cs_number:
            list_changeset_skipped.append(changeset_id)
            continue

        json_changeset = json_from_xml_changeset(changeset)
        
        list_logs.append(create_log(json.dumps(json_changeset)))
        list_changeset_processed.append(changeset_id)
    
    outro_message = "Successfully sent " + str(len(list_changeset_processed)) + " changesets.\n"
    outro_message = outro_message + "List of skipped changeset : " + str(list_changeset_skipped) + " .\n"
    outro_message = outro_message + "List of processed changset : " + str(list_changeset_processed) + " ."

    list_logs.append(create_log(outro_message,service="osm-to-datadog-debug"))

    send_logs(list_logs)
        
    # dump lastest changeset for next runs
    with open(FILENAME, 'wb') as fi:
        pickle.dump(latest_changeset, fi)

    print(outro_message)

if __name__ == '__main__':
    main()
