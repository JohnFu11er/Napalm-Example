import threading
import napalm
import json
import time

t = time.time()

full_dict = {}

print(f'full_dict = {full_dict}')

class myThread (threading.Thread):
    
    def __init__(self, threadID, router):
        threading.Thread.__init__(self)
        self._threadID = threadID
        self._router = router
    def run(self):
        print(f'Starting {self.name}')
        get_interface_data(self._router)
        print(f'Exiting {self.name}')


def get_interface_data(router):

    driver = napalm.get_network_driver('ios')

    final_dict = {}

    device = driver(
        hostname = router,
        username = 'your username here',
        password = 'your password here'
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
    full_dict.update(final_dict)
    

thread1 = myThread(1, '192.168.99.126')
thread2 = myThread(2, '192.168.99.127')

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print(json.dumps(full_dict, indent=4, sort_keys=True))

print(f'Time taken: {time.time() - t}')
