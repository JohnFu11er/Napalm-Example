import napalm
import json
import time

t = time.time()

# input a list of your target routers
routers = [
    '192.168.99.126',
    '192.168.99.127'
]

# tells napalm that you are talking to cisco devices
driver = napalm.get_network_driver('ios')

final_dict = {}

for router in routers:
    device = driver(
        hostname = router,
        username = 'your username goes here',    # enter the cli username
        password = 'your password goes here'     # enter the cli password
    )
    
    # connect to device
    print(f'Opening {router}')
    device.open()

    # fetch data from the device and create a list of only the tunnel interfaces
    print('Fetching data...')
    tunnel_data = [i for i in device.get_facts()['interface_list'] if 'Tunnel' in i]

    final_dict[router] = {}

    for tunnel in tunnel_data:
        command = f'sho run interface {tunnel}'    # string to pass to cli
        data = device.cli(
            [
                command
            ]
        )

        # builds a list which contains bandwidth, mtu, and delay for each device
        tunnel_data = [i for i in data[command].split("\n") if "band" in i or "mtu" in i or "delay" in i]
        print(tunnel)

        # assigns tunnel_data items to variables
        for item in tunnel_data:
            if 'bandwidth' in item:
                bandwidth = "".join([i for i in item if i.isnumeric()])
            elif 'mtu' in item:
                mtu = "".join([i for i in item if i.isnumeric()])
            elif 'delay' in item:
                delay = "".join([i for i in item if i.isnumeric()])

        # builds final layer of final_dict dictionary
        final_dict[router][tunnel] = {
            "bandwidth" : bandwidth,
            "mtu" : mtu,
            "delay" : delay
        }

    print(f'Closing {router}')
    device.close()

print("\n******************************\n")
print(json.dumps(final_dict, indent=4))

print(f'Time taken: {time.time() - t}')
