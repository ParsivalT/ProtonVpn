#!/usr/bin/env python
import subprocess
import psutil
import os
from random import choice, randint


def check_internet_connection():
    try:
        subprocess.run(['ping', '-c', '1', 'www.google.com'], check=True, stdout=subprocess.DEVNULL)
        return True
        
    except subprocess.CalledProcessError:
        return False
    

def setmac(interface:str) -> None:
    while True:
        
        new_mac_address = ':'.join(f'{randint(0, 255):02x}' for _ in range(6))
        print(new_mac_address)
        
        
        try:
            # Disable Networking interface.
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], check=True)
        
            # Changing MAC address.
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'address', new_mac_address])
                    
            # Enable Networking interface.
            subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'])
                
        except subprocess.CalledProcessError as err:
            print(f"Error for configurate Networking interface {interface}: {err}")

        if check_internet_connection():
            print('The Computer is Online!')
            break

            
def finish_process(process_name:str) -> None:
    # Finds and terminates all running OpenVPN processes
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            proc.kill()
            print(f"Process {process_name} finish.")


def restart_openvpn(auth_file:str, config_file:str):
    finish_process("openvpn")
    # Init a new process OpenVpn
    subprocess.Popen(["openvpn", "--config", auth_file, "--auth-user-pass", config_file])


def main() -> None:
    current_path = os.getcwd()
    # List all directories that do not contain a dot (assuming they are countries).
    dirs_country = [i for i in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, i)) and '.' not in i]
    
    if not dirs_country:
        print("there are no valid parent directories")
        exit()
    # Choose a country at random. 
    chosen_country = choice(dirs_country)
    # List all files within the country directory (assuming they are server configurations).
    dirs_servers = os.listdir(os.path.join(current_path, chosen_country))
    if not dirs_servers:
        print(f"There are no servers listed for the country {chosen_country}.")
        exit()
    
    # Choose a server at random.
    choice_server = choice(dirs_servers)
    
    # Full path to the OpenVpn configurations file.
    config_file = os.path.join(current_path, 'config.txt')
    
    # Full path to the username and password file (assuming it is a file within the chosen country and server directory)
    auth_file = os.path.join(current_path, chosen_country, choice_server)
    
    # Ends the existing OpenVPN process and starts a new one
    restart_openvpn(auth_file, config_file)
    print(f"Starting OpenVpn for the country {chosen_country}...")

if __name__ == "__main__":
   # main()
   setmac('enp9s0')
