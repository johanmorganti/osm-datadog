# osm-datadog
Monitoring OpenStreetMap with Datadog

## Setup

This script relies on those env variables : 
- DD_API_KEY (mandatory)
- DD_TAGS (recommended), should a string of comma separated values (ex : `"env:staging,version:5.1"`)
- DD_SITE (optional, defaults to "datadoghq.com")

## TODO

- [x] Send the 100 most recents changesets to Datadog
- [x] Prevent sending duplicates
- [x] log API calls are not optimized : for now doing one API call per changeset
- [x] Need to leverage `<tag />` within the changeset
- [x] Parse box to extract countries values to be able to use the [Geomap Widget](https://docs.datadoghq.com/dashboards/widgets/geomap/#configuration). Idea : https://pypi.org/project/reverse_geocoder/
- [ ] Use case :  need to be alerted when a bad changeset occurs (vandalism). Definition of a bad changeset : having a lot of deletion
