# The _SRC_ directory


## Overview

This directory contains Python scripts used for preprocessing data and generating plots 
based on observations. Each script is designed to handle specific tasks 
like cleaning up datasets, creating summary plots, and analyzing files.

## Scripts in this Directory
### 1. cleanup_data.py

This script is responsible for removing irrelevant data from a dataset. 
When executed, you can select a directory containing the data, and the 
script will output a cleaned version of the files in the same directory.
The cleaned directory will have "_cleaned" appended to its name.

#### 2. generate_overview.py
This script generates an overview of the data. 

The script provides two main plotting options:
- **Plot Data Distribution:** Displays a summary of how much data has been recorded over time for each device type.
- **Plot Data Directly from JSON Files:** Processes all available JSON files and generates detailed visualizations comparing device states (e.g., active energy levels and relay states).

#### 3. plot_active_energy_relay_one_device.py
This script is designed to visualize the active energy consumption and relay states for a single device. 
It loads data from one JSON file, normalizes the active energy values, and plots them alongside the relay states. 
The output plot is saved as a PNG file in the `plots/` folder.


#### 4. read_and_analyze_files.py
This script reads multiple JSON files, analyzes their contents, and generates plots using Plotly. 
It also calculates the number of data points per day for each device type, which is useful for identifying gaps in data collection.


You can either use those files as basis to start with your analysis or develop your own scripts to interprete the data.
