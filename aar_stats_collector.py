from modules.vmanage import vManage
from modules.parser import (
    find_apply_policy,
    find_site_lists_section,
    find_devices_range,
    save_to_csv,
    create_filename,
    load_yaml_config,
    get_range_args,
)

if __name__ == '__main__':

    ranges = get_range_args()
    server,port,username,password = load_yaml_config('config.yaml')

    session = vManage(server,port,username,password)

    apply_policy = find_apply_policy(session.policy)
    available_site_lists = [line.split(' ')[-1] for line in apply_policy if 'site-list' in line]
    system_ips = find_devices_range(session.devices,ranges)

    if system_ips:

        site_list_policy_section = find_site_lists_section(session.policy)
        system_ips = find_devices_range(session.devices,ranges)
        data = session.collect_aar_stats(system_ips)
        filename = create_filename()
        save_to_csv(data,filename)

    else:
        print(f'No devices found for range: {ranges}')
