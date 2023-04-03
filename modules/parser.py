import os
import csv
from datetime import datetime
import yaml
from argparse import ArgumentParser
import sys
import logging
logger = logging.getLogger('PARSER')


def get_args():

    logger.debug('Getting arguments from terminal')
    parser = ArgumentParser(description='Arguments for AAR Stats Collector')
    parser.add_argument('--range', '-r', required=True, type=str, help='Site ID range to catch devices for SDWAN overlay')
    parser.add_argument('--debug', '-d', action='store_true', help='Use this flag to enable debug mode')
    arguments = parser.parse_args()
    
    ranges = [arguments.range]
    debug = arguments.debug
    logger.debug(f'Range: {ranges}')
    logger.debug(f'Debug: {debug}')

    return ranges,debug


def load_yaml_config(config_file):

    logger.debug('Getting variables from YAML file')
    with open(config_file, 'r') as f:
        variables = yaml.safe_load(f)

    for key in variables.keys():
        if not variables[key]:
            variables[key] = input(f'{key}: ')

    server = variables['VMANAGE']
    port = variables['PORT']
    username = variables['USERNAME']
    password = variables['PASSWORD']
    logger.debug(f'Variables: {variables}')

    return server,port,username,password
        

def find_apply_policy(lines):

    logger.debug('obtaining apply policy section')
    parent_pattern = 'apply-policy'

    for i,line in enumerate(lines):
        if parent_pattern in line:
            start_index = i

    apply_policy = lines[start_index:]
    logger.debug(f'apply policy: {apply_policy}')

    return apply_policy


def find_site_lists_section(lines):

    write_flag = False
    lists_line_found = False
    site_list_line_found = False
    site_list_section = []

    for line in lines:

        if 'lists' in line:
            lists_line_found = True

        elif ('site-list') in line and lists_line_found and not site_list_line_found:
            write_flag = True
            site_list_line_found = True
            site_list_section.append(line)

        elif ('-list ') in line and not ('site-list') in line and site_list_line_found:
            write_flag = False
            site_list_line_found = False
        
        elif 'apply-policy' in line:
            break
        
        else:
            if write_flag:
                site_list_section.append(line)
            pass
    
    logger.debug(f'site-list policy: {site_list_section}')

    return site_list_section


def find_devices_range(devices,ranges_list):

    devices_in_range = []

    if devices:

        for item in ranges_list:

            if '-' in item:
                list_range = item.split('-')
                start = int(list_range[0])
                end = int(list_range[1]) + 1

            else:
                start = int(item)
                end = int(item) + 1

            for device in devices:
                if int(device[2]) in range(start,end):
                    devices_in_range.append(device[1])

        if not devices_in_range:
            logger.warning(f'No devices found for range: {ranges_list}')
            sys.exit(1)
    
    logger.debug(f'Devices in range {devices_in_range}')
                    
    return devices_in_range


def save_to_csv(data,filename):

    with open(filename,'w') as f:

        writer_csv = csv.writer(f,delimiter=',')
        for line in data:
            writer_csv.writerow(line)

    logger.info(f'File saved as: {filename}')


def create_filename():

    logger.debug('Creating CSV filename')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    modules = os.path.dirname(__file__)
    outputs = os.path.join(os.path.dirname(modules), "outputs")
    filename = os.path.join(outputs, f'AAR-STATS-{timestamp}.csv')
    logger.debug(f'Filename: {filename}')

    return filename
