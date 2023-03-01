import os
import csv
from datetime import datetime
import yaml
from argparse import ArgumentParser


def get_range_args():

    parser = ArgumentParser(description='Arguments for AAR Stats Collector')
    parser.add_argument('--range', '-r', required=True, type=str, help='Site ID range to catch devices for SDWAN overlay')
    arguments = parser.parse_args()

    ranges = [arguments.range]

    return ranges


def load_yaml_config(config_file):

    with open(config_file, 'r') as f:
        variables = yaml.safe_load(f)

    for key in variables.keys():
        if not variables[key]:
            variables[key] = input(f'{key}: ')

    server = variables['VMANAGE']
    port = variables['PORT']
    username = variables['USERNAME']
    password = variables['PASSWORD']

    return server,port,username,password
        

def find_apply_policy(lines):

    parent_pattern = 'apply-policy'

    for i,line in enumerate(lines):
        if parent_pattern in line:
            start_index = i

    apply_policy = lines[start_index:]
    
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
                    
    return devices_in_range


def save_to_csv(data,filename):

    with open(filename,'w') as f:

        writer_csv = csv.writer(f,delimiter=',')
        for line in data:
            writer_csv.writerow(line)

    print(f'File saved as: {filename}')


def create_filename():

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    modules = os.path.dirname(__file__)
    outputs = os.path.join(os.path.dirname(modules), "outputs")
    filename = os.path.join(outputs, f'AAR-STATS-{timestamp}.csv')
    
    return filename
