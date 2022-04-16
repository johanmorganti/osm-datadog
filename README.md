# osm-datadog
Monitoring OpenStreetMap with Datadog

[The work in progress can be seen as this URL](https://p.datadoghq.com/sb/14e968020-4993928572d9d3e0dcdbe9a12a42499a)

![Main Dashboard](./screenshots/main_dashboard.jpeg)

## Setup

This script relies on those env variables : 
- DD_API_KEY (mandatory)
- DD_TAGS (recommended), should a string of comma separated values (ex : `"env:staging,version:5.1"`)
- DD_SITE (optional, defaults to "datadoghq.com")

Run this script every 15 to 30 seconds.

## TODO

- [x] Send the 100 most recents changesets to Datadog
- [x] Prevent sending duplicates
- [x] log API calls are not optimized : for now doing one API call per changeset
- [x] Need to leverage `<tag />` within the changeset
- [x] Parse box to extract countries values to be able to use the [Geomap Widget](https://docs.datadoghq.com/dashboards/widgets/geomap/#configuration). Idea : https://pypi.org/project/reverse_geocoder/
- [x] Clean editors (solution done on Datadog side, "editor family" created)
- [x] add log creation to the utilities
- [x] Clean imageries
- [ ] Share Datadog pipelines
- [ ] Use case :  need to be alerted when a bad changeset occurs (vandalism). First need definition of a bad changeset : having a lot of deletion?
- [ ] How to prevent counting some changeset multiple times?
        - Some changeset have a discussion, so they might be pushed to the replica at each discussion update : example with changeset `118161820` in `https://planet.osm.org/replication/changesets/004/878/999.osm.gz`
