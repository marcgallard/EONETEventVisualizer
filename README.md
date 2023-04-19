<h3 align="center">EONET Event Visualizer</h3>

![Version](https://img.shields.io/badge/version-0.1-blue.svg?cacheSeconds=2592000)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](https://www.apache.org/licenses/LICENSE-2.0)
[![python](https://img.shields.io/badge/python-3.10.4-blue.svg?logo=python&labelColor=yellow)](https://www.python.org/downloads/)
[![platform](https://img.shields.io/badge/platform-osx%2Flinux%2Fwindows-green.svg)](https://github.com/marcgallard/EONETEventVisualizer)

<p align="center">
The EONET Event Visualizer visualizes natural events and disasters on a global level using Tableau
</p>

## About EONET Event Visualizer

EONET's geospatial data is first pulled using the EONET API, after which the data is parsed into a GeoJSON format using Python. Tableau is then used to visualize the data for an interactive dashboard experience. Note that the GeoJSON data is static once parsed; one possible improvement is for the Tableau viz to have a live connection to a server it can pull updated data from (such as having a server Tableau can connect to that updates a local DB after running the Python script on a scheduled basis).

## Prerequisites

- `geojson` for parsing JSON data into a format Tableau accepts
- `json` for parsing data from the API call
- `pip` to make installation of argparse and jsonschema easy
- `Python 3.10.4` (version used for this project)
- `requests` for making API calls to EONET
- (if running on own) Tableau account to create an interactive dashboard (a public visualization will also be available on my personal profile)

## Installation

Clone the repo: `git clone https://github.com/marcgallard/EONETEventVisualizer.git`

Install pip to help install geojson and requests (I recommend following [this guide](https://packaging.python.org/en/latest/tutorials/installing-packages/#ensure-you-can-run-pip-from-the-command-line))

Then run

    pip install geojson    
    
to install geojson, and
    
    pip install requests
    
to install requests.

## Running main script

TO-DO

## Copyright and license

Code and documentation copyright 2023 under [me](https://github.com/marcgallard). Code released under the [Apache 2.0 License](https://github.com/marcgallard/EONETEventVisualizer/blob/main/LICENSE). Documentation released under [Apache](https://www.apache.org/licenses/LICENSE-2.0).
