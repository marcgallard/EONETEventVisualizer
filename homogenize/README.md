## Description

Since Tableau only supports GeoJSON files that contain a single type of geometry and EONET can sometimes retrieve events of varying types of geometry, this script attempts to have all geometries be of type "Point". 

For example, currently the original EONET data my Tableau visualization was based on has Points and occasionally LineStrings, sets of Points that are already in the current dataset. This means some events are repeated twice, once as a Point and again as a coordinate in a LineString. LineStrings can be therefore be treated as duplicates, allowing us to remove them from the data without affecting the data's integrity, yielding a modified version of EONET Events data that only has Points. This can be exported back as a GeoJSON file, allowing Tableau to visualize the data without issue.

The script also takes in the JSON files for Categories and Sources that were created during the main script's run. This is done to improve the presentation of homogenized events data using Tableau since 'sources' and 'categories' info for each event can be hard on the eyes. Tableau also does not render lists; all events have their sources' type as lists. Each event therefore has two new columns, 'simpleCategory' and 'simpleSources' that attempts to rectify these issues.

## Prerequisites

- `geopandas` for importing and exporting GeoJSON files + manipulating them as data frames
- Files from pullData.py for importing

## Installation

Run
    
    pip install geopandas
    
to install geopandas.

## Running script

First ensure that `categories.json`, `events.geojson`, and `sources.json` are in the './homogenize/data' folder! It's also important that the data is named as such, otherwise the script won't run.

    py ./homogenize/homogenizeEvents.py
    
The generated output will be stored in a time-based folder within './homogenize/output/'.
