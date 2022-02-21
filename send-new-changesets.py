from itertools import count
import requests
import xml.etree.ElementTree as ET
from os import path
import pickle
import json
import os

from dateutil.parser import parse as dateutil_parser
from datadog_api_client.v2 import ApiClient, ApiException, Configuration
from datadog_api_client.v2.api import logs_api
from datadog_api_client.v2.models import *
from pprint import pprint

import reverse_geocoder

FILENAME = "previous_max_changeset.pk"
list_tags = os.environ.get("DD_TAGS")

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

def send_logs(list_logs):
    # Defining the host is optional and defaults to https://api.datadoghq.com
    # DD_SITE, DD_API_KEY, DD_APP_KEY are supported by default :
    # https://github.com/DataDog/datadog-api-client-python/blob/master/src/datadog_api_client/v2/configuration.py
    dd_configuration = Configuration()

    # Enter a context with an instance of the API client
    with ApiClient(dd_configuration) as api_client:
        # Create an instance of the API class
        api_instance = logs_api.LogsApi(api_client)

        try:
            # Send logs
            api_response = api_instance.submit_log(list_logs)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling LogsApi->submit_log: %s\n" % e)

def get_more_info_from_coordinates(min_lat, min_lon, max_lat, max_lon):
    # For now, let's only take the center of the rectangle
    
    avg_lat = (float(min_lat) + float(max_lat)) / 2 
    avg_lon = (float(min_lon) + float(max_lon)) / 2
    
    return reverse_geocoder.search([(avg_lat,avg_lon)],mode=1)[0]

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
    log_intro_message = HTTPLogItem(
                ddsource="python",
                ddtags=list_tags,
                hostname="test-osm",
                service="osm-to-datadog-debug",
                message= intro_message,
            )
    list_logs.append(log_intro_message)
    print(intro_message)

    for changeset in xml_last_cs:
        changeset_id = int(changeset.attrib["id"])
        if changeset_id <= last_run_cs_number:
            list_changeset_skipped.append(changeset_id)
            continue

        json_log = {}
        for attribute in changeset.attrib:
            if attribute in ["id", "changes_count", "comments_count", "uid"]:
                json_log["changeset." + attribute] = int(changeset.attrib[attribute])
            else :
                json_log["changeset." + attribute] = str(changeset.attrib[attribute])

        for tag in changeset:
            json_log["changeset." + tag.attrib["k"]] = tag.attrib["v"]


        if "min_lat" in changeset.attrib:
            json_log["geo"] = get_more_info_from_coordinates(
                changeset.attrib["min_lat"], 
                changeset.attrib["min_lon"], 
                changeset.attrib["max_lat"], 
                changeset.attrib["max_lon"])

        
        new_log_item = HTTPLogItem(
                ddsource="python",
                ddtags=list_tags,
                hostname="test-osm",
                service="osm-to-datadog",
                message= json.dumps(json_log),
            )
        
        list_logs.append(new_log_item)
        list_changeset_processed.append(changeset_id)
    
    outro_message = "Successfully sent " + str(len(list_changeset_processed)) + " changesets.\n"
    outro_message = outro_message + "List of skipped changeset : " + str(list_changeset_skipped) + " .\n"
    outro_message = outro_message + "List of processed changset : " + str(list_changeset_processed) + " ."
    log_outro_message = HTTPLogItem(
                ddsource="python",
                ddtags=list_tags,
                hostname="test-osm",
                service="osm-to-datadog-debug",
                message=outro_message,
            )
    list_logs.append(log_outro_message)

    send_logs(list_logs)
        
    # dump lastest changeset for next runs
    with open(FILENAME, 'wb') as fi:
        pickle.dump(latest_changeset, fi)

    print(outro_message)

if __name__ == '__main__':
    main()
