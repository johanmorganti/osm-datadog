import requests
import xml.etree.ElementTree as ET
from os import path
import pickle
import json
from io import StringIO

from dateutil.parser import parse as dateutil_parser
from datadog_api_client.v2 import ApiClient, ApiException, Configuration
from datadog_api_client.v2.api import logs_api
from datadog_api_client.v2.models import *
from pprint import pprint

FILENAME = 'previous_max_changeset.pk'

# Defining the host is optional and defaults to https://api.datadoghq.com
# DD_SITE, DD_API_KEY, DD_APP_KEY are supported by default :
# https://github.com/DataDog/datadog-api-client-python/blob/master/src/datadog_api_client/v2/configuration.py
dd_configuration = Configuration()

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
latest_changeset = int(xml[0].attrib['id'])
last_run_changeset = 0

# load the last changeset from the last run
if path.exists(FILENAME):
    with open(FILENAME, 'rb') as fi:
        last_run_changeset = pickle.load(fi)

print("Number of changesets to load : " + str(latest_changeset - last_run_changeset))

# dump lastest changeset for next runs
with open(FILENAME, 'wb') as fi:
    pickle.dump(latest_changeset, fi)
    
# Enter a context with an instance of the API client
with ApiClient(dd_configuration) as api_client:
    # Create an instance of the API class
    api_instance = logs_api.LogsApi(api_client)

    list_logs = []

    for changeset in xml:
        if int(changeset.attrib['id']) <= last_run_changeset:
            # print("Already processed. Skipping " + changeset.attrib["id"])
            continue
        
        json_log = {}
        for attribute in changeset.attrib:
            if attribute in ["id", "changes_count", "comments_count", "uid"]:
                json_log["changeset." + attribute] = int(changeset.attrib[attribute])
            else :
                json_log["changeset." + attribute] = str(changeset.attrib[attribute])

        for tag in changeset:
            json_log["changeset." + tag.attrib["k"]] = tag.attrib["v"]

        new_log_item = HTTPLogItem(
                ddsource="python",
                ddtags="env:staging",
                hostname="test-osm",
                service="osm-to-datadog",
                message= json.dumps(json_log),
            )
        
        list_logs.append(new_log_item)
    
    body = HTTPLog(list_logs)

    try:
        # Send logs
        api_response = api_instance.submit_log(list_logs)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling LogsApi->submit_log: %s\n" % e)




