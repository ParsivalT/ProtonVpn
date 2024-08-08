from api.proton import Vpn
from api.config import ConfigManager
import os 

VPN = Vpn()
CURRENT_PATH = os.getcwd()
config_manager = ConfigManager("/etc/resolv.conf")

try:
    config_server_file, auth_file = VPN.choose_random_configuration(CURRENT_PATH)
    VPN.start_vpn(auth_file, config_server_file)
    
except Exception as err:
    VPN.restart_default()
    print(f"Erro: {err}")
