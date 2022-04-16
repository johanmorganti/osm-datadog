import os
import reverse_geocoder

from datadog_api_client.v2 import ApiClient, ApiException, Configuration
from datadog_api_client.v2.api import logs_api
from datadog_api_client.v2.models import *

def get_more_info_from_coordinates(min_lat, min_lon, max_lat, max_lon):
    # For now, let's only take the center of the rectangle
    
    avg_lat = (float(min_lat) + float(max_lat)) / 2 
    avg_lon = (float(min_lon) + float(max_lon)) / 2
    
    return reverse_geocoder.search([(avg_lat,avg_lon)],mode=1)[0]

def json_from_xml_changeset(changeset):
    json_log = {}

    for attribute in changeset.attrib:
        if attribute in ["id", "changes_count", "comments_count", "uid"]:
            json_log["changeset." + attribute] = int(changeset.attrib[attribute])
        else :
            json_log["changeset." + attribute] = str(changeset.attrib[attribute])
                
    for element in changeset:
        if 'k' in element.attrib: 
            json_log["changeset." + element.attrib["k"]] = element.attrib["v"]

    if "min_lat" in changeset.attrib:
        json_log["geo"] = get_more_info_from_coordinates(
            changeset.attrib["min_lat"], 
            changeset.attrib["min_lon"], 
            changeset.attrib["max_lat"], 
            changeset.attrib["max_lon"])

    return json_log

def create_log(message, source="python",list_tags=os.environ.get("DD_TAGS"),hostmame="test-osm",service="osm-to-datadog"):
    return HTTPLogItem(
            ddsource=source,
            ddtags=list_tags,
            hostname=hostmame,
            service=service,
            message=message,
        )

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
            api_instance.submit_log(list_logs)
        except ApiException as e:
            print("Exception when calling LogsApi->submit_log: %s\n" % e)