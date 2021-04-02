import napalm
import json
import time
from getpass import getpass

t = time.time()

my_password = getpass()

routers = [
    '192.168.99.126',
    '192.168.99.127'
]

def get_interface_data(router):

    driver = napalm.get_network_driver('ios')

    final_dict = {}

    device = driver(
        hostname = router,
        username = 'your username goes here',   # enter your username for the cli
        password = my_password
    )

    print(f'Opening {router}')
    device.open()

    print('Fetching data...')
    tunnel_data = [i for i in device.get_facts()['interface_list'] if 'Tunnel' in i]

    final_dict[router] = {}

    for tunnel in tunnel_data:
        command = f'sho run interface {tunnel}'
        data = device.cli(
            [
                command
            ]
        )

        tunnel_data = [i for i in data[command].split("\n") if "band" in i or "mtu" in i or "delay" in i]
        print(tunnel)

        for item in tunnel_data:
            if 'bandwidth' in item:
                bandwidth = "".join([i for i in item if i.isnumeric()])
            elif 'mtu' in item:
                mtu = "".join([i for i in item if i.isnumeric()])
            elif 'delay' in item:
                delay = "".join([i for i in item if i.isnumeric()])

        final_dict[router][tunnel] = {
            "bandwidth" : bandwidth,
            "mtu" : mtu,
            "delay" : delay
        }

    print(f'Closing {router}')
    device.close()
    return final_dict
    

full_dict = {}
for router in routers:
    full_dict.update(get_interface_data(router))

print(json.dumps(full_dict, indent=4))

print(f'Time taken: {time.time() - t}')
