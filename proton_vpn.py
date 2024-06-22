import subprocess
from random import choice 
from time import sleep
import os

class TerminalColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m' 
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


current_path = os.getcwd()

# List all directories that do not contain a dot (assuming they are countries).
dirs_country = [i for i in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, i)) and '.' not in i]

if not dirs_country:
    print("there are no valid parent directories")
    exit()

# Choose a country at random. 
choice_country = choice(dirs_country)

# List all files within the country directory (assuming they are server configurations).
dirs_servers = os.listdir(os.path.join(current_path, choice_country))
if not dirs_servers:
    print(f"There are no servers listed for the country {choice_country}.")
    exit()

# Choose a server at random.
choice_server = choice(dirs_servers)

# Full path to the OpenVpn configurations file.
config_file = os.path.join(current_path, 'config.txt')

# Full path to the username and password file (assuming it is a file within the chosen country and server directory)
auth_file = os.path.join(current_path, choice_country, choice_server)

os.system('clear')
print("--"*25)
print(TerminalColors.OKGREEN + "Starting tunneling..." + TerminalColors.ENDC)
sleep(1)
print(TerminalColors.WARNING + f"Server Country: {choice_country}" + TerminalColors.ENDC)

try:
    # subprocess.run command to run OpenVPN
    result = subprocess.run(['sudo','openvpn', '--config', auth_file, '--auth-user-pass', config_file],
                   text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print(TerminalColors.GREEN + "Vpn Status: Online" + TerminalColors.ENDC)

    else:
        raise Exception(f"{result.stderr}")
        exit()

except KeyboardInterrupt:
    print("Shutdonw Vpn")

except Exception as err:
    print("There was problem starting tunneling: " + err)


