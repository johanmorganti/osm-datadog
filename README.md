# osm-datadog
Monitoring OpenStreetMap with Datadog

## Setup

This script relies on those env variable : 
- DD_SITE (defaults to "datadoghq.com")
- DD_API_KEY 
- DD_APP_KEY

## TODO

[x] Send the 100 most recents changesets to Datadog
[x] Prevent sending duplicates
[ ] log API calls are not optimized : for now doing one API call per changeset
[ ] Need to leverage `<tag />` within the changeset
[ ] Add option to scope to a particular part of the word
[ ] Parse box to extract countries values to be able to use the [Geomap Widget](https://docs.datadoghq.com/dashboards/widgets/geomap/#configuration)
[ ] Use case :  need to be alerted when a bad changeset occurs (vandalism). Definition of a bad changeset : having a lot of deletion

