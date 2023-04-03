# AAR STATS COLLECTOR

## Description

Script to collect the Cisco SDWAN BFD statististics from the devices matched on a site-id range

## Installation

Python 3.6+ is required

Use pip to install requirements file

    pip install -r requirements.txt

## Configuration

Edit the config.yaml file with your vmanage credentials

## Run

Execute the script with the following command

    python aar_stats_collector.py --range 100-200

Script uses the argument --range or short option -r to match the site-id from the devices present on the overlay and obtain the AAR STATS from them, if no devices found for the given range an error message will be displayed

Once script runs successfully the AAR BFD stats will be saved on a CSV file saved under the outputs folder

    AAR-STATS-[TIMESTAMP].csv

Script supports debug mode add the --debug keyboard and an extended output will be created with detailed messages from execution

    python aar_stats_collector.py --range 100-200 --debug

## Contact

Please use issues section on github to request new funtionality or report bugs

For any comment email the authors

    zaziz@cisco.com
    rgomezbe@cisco.com
