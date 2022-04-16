import requests
import gzip
import xml.etree.ElementTree as ET


request_sequence = requests.get("https://planet.osm.org/replication/changesets/004/877/289.osm.gz", stream=True)

xml = ET.fromstring(gzip.decompress(request_sequence.raw.read()))

json_logs = []

for changeset in xml:
    changeset_id = int(changeset.attrib["id"])

    print(changeset_id)
    json_log = {}

    for attribute in changeset.attrib:
        if attribute in ["id", "changes_count", "comments_count", "uid"]:
            json_log["changeset." + attribute] = int(changeset.attrib[attribute])
        else :
            json_log["changeset." + attribute] = str(changeset.attrib[attribute])

    for element in changeset:
        if 'k' in element.attrib: 
            json_log["changeset." + element.attrib["k"]] = element.attrib["v"]
