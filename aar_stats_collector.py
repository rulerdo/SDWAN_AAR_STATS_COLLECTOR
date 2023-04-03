import logging
from modules.vmanage import vManage
from modules.parser import (
    find_apply_policy,
    find_site_lists_section,
    find_devices_range,
    save_to_csv,
    create_filename,
    load_yaml_config,
    get_args,
)


if __name__ == '__main__':
    
    ranges,debug = get_args()
    log_level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(format='%(name)s - %(levelname)s : %(message)s', level=log_level)
    logger = logging.getLogger('MAIN')
    
    logger.info('Obtaining credentials from config.yaml')
    server,port,username,password = load_yaml_config('config.yaml')

    logger.info(f'Connecting to vmanage: {server}')
    session = vManage(server,port,username,password)

    logger.info('Obtaining apply policy section from centralized policy')
    apply_policy = find_apply_policy(session.policy)

    available_site_lists = [line.split(' ')[-1] for line in apply_policy if 'site-list' in line]
    
    logger.info(f'Obtaining devices in range: {ranges}')
    system_ips = find_devices_range(session.devices,ranges)

    logger.info('Obtaining site lists from centralized policy')
    site_list_policy_section = find_site_lists_section(session.policy)
    
    logger.info('Saving data on CSV file')
    data = session.collect_aar_stats(system_ips)
    filename = create_filename()
    save_to_csv(data,filename)
