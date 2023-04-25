<h3 align="center">EONET Event Visualizer</h3>

<div align="center">

![Version](https://img.shields.io/badge/version-0.1-blue.svg?cacheSeconds=2592000)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](https://www.apache.org/licenses/LICENSE-2.0)
[![python](https://img.shields.io/badge/python-3.10.4-blue.svg?logo=python&labelColor=yellow)](https://www.python.org/downloads/)
[![platform](https://img.shields.io/badge/platform-osx%2Flinux%2Fwindows-green.svg)](https://github.com/marcgallard/EONETEventVisualizer)

</div>

<p align="center">
The EONET Event Visualizer visualizes natural events and disasters on a global level using Tableau
</p>

## About EONET Event Visualizer

EONET's geospatial data is first pulled using the EONET API, after which the data is written into json and geojson files using Python. Tableau is then used to visualize the data for an interactive dashboard experience. Note that the GeoJSON data is static once parsed; one possible improvement is for the Tableau viz to have a live connection to a server it can pull updated data from (such as having a server Tableau can connect to that has a local DB Tableau can pull from).

The script requests EONET data up to 3 times, 3 second delay between each request by default. If the first request is successful then the other two won't be attempted. Also note that the EONET API has a strict rate-limit; more info can be found on NASA's [API documentation](https://api.nasa.gov/) website.

One limitation of this project is that Tableau currently does not support MixedGeometry. If the EONET data contains a mix of different geometries (Point and LineString as one example), an additional script called "homogenizeEvents.py" will attempt to make all events of type "Point"; further details can be found in the script's README found in folder "./homogenize".

## Visualization

Please check out my Tableau Public visualization! Here's the link: [https://public.tableau.com/app/profile/marco.gallardo/viz/4-24-23_EONET_Data_Visualized/Dashboard1](https://public.tableau.com/app/profile/marco.gallardo/viz/4-24-23_EONET_Data_Visualized/Dashboard1)

## Prerequisites

- `pip 23.1` to make installation of argparse and jsonschema easy
- `Python 3.10.4` (version used for this project)
- `requests` for making API calls to EONET
- (if running on own) Tableau account to create an interactive dashboard (a public visualization will also be available on my personal profile)

## Installation

Clone the repo: `git clone https://github.com/marcgallard/EONETEventVisualizer.git`

Install pip to help install requests (I recommend following [this guide](https://packaging.python.org/en/latest/tutorials/installing-packages/#ensure-you-can-run-pip-from-the-command-line))

Then run
    
    pip install requests
    
to install requests.

## Running main script
    
    py pullData.py
    
Output is stored in a time-based folder within the folder './output'. If data needs to be homogenized to Point geometry only then run `homogenizeEvents.py` under the 'homogenize' folder (limitations apply).

## Copyright and license

Code and documentation copyright 2023 under [me](https://github.com/marcgallard). Code released under the [Apache 2.0 License](https://github.com/marcgallard/EONETEventVisualizer/blob/main/LICENSE). Documentation released under [Apache](https://www.apache.org/licenses/LICENSE-2.0).
