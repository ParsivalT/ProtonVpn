import subprocess
import psutil
from random import randint, choice
import logging
import os
import time
from .config import ConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Vpn:
    def __init__(self):
        self.current_path = os.getcwd()
        self.config_manager = ConfigManager("/etc/resolv.conf")

    def __set_mac_address(self, interfaces: list, max_attempts: int = 4, wait_time: int = 5) -> bool:
        """Configura um novo endereço MAC para cada interface fornecida e verifica a conexão."""
        for interface in interfaces:
            for attempt in range(max_attempts):
                new_mac_address = ":".join(f"{randint(0, 255):02x}" for _ in range(6))
                try:
                    logging.info(f"Attempt {attempt + 1}: Setting MAC address {new_mac_address} for interface {interface}.")
                    
                    # Desativar a interface de rede
                    subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], check=True)
                    time.sleep(1)
                    # Definir um novo endereço MAC
                    subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'address', new_mac_address], check=True)
                    
                    time.sleep(1)
                    # Reativar a interface de rede
                    subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], check=True)
                    
                    time.sleep(1)
                    # Aguarde alguns segundos para garantir que a configuração seja aplicada
                    time.sleep(wait_time)
                    
                    # Verificar se há conexão com a internet
                    if self.check_internet_connection():
                        logging.info(f"Connection established with new MAC address {new_mac_address}.")
                        return True  # Se a conexão estiver ok, saia do loop
                    else:
                        logging.warning(f"No internet connection with MAC address {new_mac_address}. Trying another address.")
                
                except subprocess.CalledProcessError as err:
                    logging.error(f"Error configuring network interface {interface}: {err}")
        
        raise RuntimeError("Failed to configure a working MAC address after multiple attempts.")

    def __finish_process(self, process_name: str) -> None:
        """Encontra e termina todos os processos com o nome especificado."""
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == process_name:
                proc.kill()
                logging.info(f"Process {process_name} terminated.")

    def start_vpn(self, auth_file: str, config_file: str) -> None:
        """Inicia o OpenVPN após configurar os endereços MAC das interfaces de rede."""
        dns = "nameserver 1.1.1.1\n" 

        if not os.path.isfile(auth_file):
            raise FileNotFoundError(f"Auth file {auth_file} does not exist.")
        if not os.path.isfile(config_file):
            raise FileNotFoundError(f"Config file {config_file} does not exist.")
        
        for _ in range(3):
            try:
                self.__finish_process("openvpn")

                interfaces = self.get_network_interfaces()
                if not interfaces:
                    raise ConnectionError("No active network interfaces found.")

                # Configura os endereços MAC das interfaces
                self.__set_mac_address(interfaces)

                # Aterando o DNS para 1.1.1.1
                self.config_manager.write(dns)
                
                # Inicia o OpenVPN
                subprocess.Popen(["sudo", "openvpn", "--config", config_file, "--auth-user-pass", auth_file])

                if not self.check_internet_connection():
                    raise ConnectionError("No internet connection detected.")

                logging.info("OpenVPN started successfully.")
                print("Conexão realizada com sucesso!")
                break

            except (subprocess.CalledProcessError, ConnectionError, RuntimeError, FileNotFoundError) as err:
                logging.error(f"Error starting VPN: {err}")
                continue

        if not self.check_internet_connection():
            raise ConnectionError("No internet connection detected.")

    @staticmethod
    def check_internet_connection() -> bool:
        """Verifica se há conexão com a Internet."""
        try:
            subprocess.run(['ping', '-c', '1', '8.8.8.8'], check=True, stdout=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def get_network_interfaces() -> list:
        """Obtém uma lista de interfaces de rede ativas."""
        try:
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            output = result.stdout.strip().split('\n')
            interfaces = [line.split(':')[1].strip() for line in output if 'state UP' in line]
            return interfaces
        except subprocess.CalledProcessError as e:
            logging.error(f"Error getting network interfaces: {e}")
            return []

    def choose_random_configuration(self, path: str) -> tuple:
        """
        Escolhe aleatoriamente um diretório de país e um servidor dentro dele, e constrói os caminhos para os arquivos de configuração e autenticação.
        
        Retorna:
            tuple: (config_file, auth_file) onde config_file é o caminho para o arquivo de configuração
                   e auth_file é o caminho para o arquivo de autenticação.
        """
        dirs_country = [i for i in os.listdir(path) if os.path.isdir(os.path.join(path, i)) and '.' not in i]
        
        if not dirs_country:
            logging.error("No valid country directories found.")
            raise RuntimeError("No valid country directories found.")

        chosen_country = choice(dirs_country)
        dirs_servers = [i for i in os.listdir(os.path.join(path, chosen_country)) if os.path.isfile(os.path.join(path, chosen_country, i))]
        
        if not dirs_servers:
            logging.error(f"No servers listed for country {chosen_country}.")
            raise RuntimeError(f"No servers listed for country {chosen_country}.")

        chosen_server = choice(dirs_servers)
        auth_file = os.path.join(path, 'credential.txt')
        config_file = os.path.join(path, chosen_country, chosen_server)

        return config_file, auth_file

    def restart_default(self, dns: str = "nameserver 127.0.2.1\n") -> None:
        # Alterando o DNS padrão.
        self.config_manager.write(dns)

        try:
            # Reiniciando os serviços para garantir o funcionamento.
            subprocess.run(["systemctl", "restart", "NetworkManager"], check=True)
            time.sleep(4)
            subprocess.run(["systemctl", "restart", "dnscrypt-proxy"], check=True)
        except subprocess.CalledProcessError as err:
            print("Houve um problema: ", err)
