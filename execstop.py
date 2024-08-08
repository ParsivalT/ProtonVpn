from api.proton import Vpn
from api.config import ConfigManager
import os 
import subprocess

VPN = Vpn()

try:
    subprocess.run(["pkill", "openvpn"])
    VPN.restart_default()
    
except Exception as err:
    print(f"Erro: {err}")
