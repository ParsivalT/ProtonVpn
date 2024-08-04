import subprocess
import psutil
from random import randint, choice
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Vpn:
    def __init__(self):
        self.current_path = os.getcwd()

    def __set_mac_address(self, interfaces: list) -> bool:
        """Configura um novo endereço MAC para cada interface fornecida."""
        for interface in interfaces:
            for _ in range(3):
                new_mac_address = ":".join(f"{randint(0, 255):02x}" for _ in range(6))
                try:
                    # Desativar a interface de rede
                    subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'down'], check=True)
                    
                    # Definir um novo endereço MAC
                    subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'address', new_mac_address], check=True)
                    
                    # Reativar a interface de rede
                    subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], check=True)
                    
                    logging.info(f"MAC address for interface {interface} set to {new_mac_address}.")
                    break  # Se a configuração foi bem-sucedida, saia do loop

                except subprocess.CalledProcessError as err:
                    logging.error(f"Error configuring network interface {interface}: {err}")
                    continue  # Continue tentando com a próxima tentativa

        return True

    def __finish_process(self, process_name: str = 'openvpn') -> None:
        """Encontra e termina todos os processos com o nome especificado."""
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == process_name:
                proc.kill()
                logging.info(f"Process {process_name} terminated.")

    def start_vpn(self, auth_file: str, config_file: str) -> None:
        """Inicia o OpenVPN após configurar os endereços MAC das interfaces de rede."""
        if not os.path.isfile(auth_file):
            raise FileNotFoundError(f"Auth file {auth_file} does not exist.")
        if not os.path.isfile(config_file):
            raise FileNotFoundError(f"Config file {config_file} does not exist.")
        
        self.__finish_process("openvpn")

        interfaces = self.get_network_interfaces()
        if not interfaces:
            raise ConnectionError("É necessário que uma interface de rede esteja ativa.")

        for interface in  interfaces:
        	self.__set_mac_address(interfaces):
        	# TODO: CorriGIR o erro ao que deleta as interfacers

        # Inicia um novo processo OpenVPN
        subprocess.Popen(["sudo", "openvpn", "--config", config_file, "--auth-user-pass", auth_file])
        logging.info("OpenVPN started.")

    @staticmethod
    def check_internet_connection() -> bool:
        """Verifica se há conexão com a Internet."""
        try:
            subprocess.run(['ping', '-c', '1', 'www.debian.org'], check=True, stdout=subprocess.DEVNULL)
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

        except Exception as e:
            logging.error(f"Error getting network interfaces: {e}")
            return []

    def choose_random_configuration(self) -> tuple:
        """
        Escolhe aleatoriamente um diretório de país e um servidor dentro dele, e constrói os caminhos para os arquivos de configuração e autenticação.
        
        Retorna:
            tuple: (config_file, auth_file) onde config_file é o caminho para o arquivo de configuração
                   e auth_file é o caminho para o arquivo de autenticação.
        """
        current_path = self.current_path

        # Lista todos os diretórios que não contêm um ponto (assumindo que são países).
        dirs_country = [i for i in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, i)) and '.' not in i]
        
        if not dirs_country:
            logging.error("Não há diretórios válidos de país.")
            raise RuntimeError("Não há diretórios válidos de país.")

        # Escolhe um país aleatoriamente.
        chosen_country = choice(dirs_country)

        # Lista todos os arquivos dentro do diretório do país escolhido (assumindo que são configurações de servidores).
        dirs_servers = [i for i in os.listdir(os.path.join(current_path, chosen_country)) if os.path.isfile(os.path.join(current_path, chosen_country, i))]
        
        if not dirs_servers:
            logging.error(f"Não há servidores listados para o país {chosen_country}.")
            raise RuntimeError(f"Não há servidores listados para o país {chosen_country}.")

        # Escolhe um servidor aleatoriamente.
        chosen_server = choice(dirs_servers)

        # Caminho completo para o arquivo de configuração do OpenVPN.
        auth_file = os.path.join(current_path, 'credential.txt')

        # Caminho completo para o arquivo de autenticação (assumindo que é um arquivo dentro do diretório do país e servidor escolhidos).
        config_file = os.path.join(current_path, chosen_country, chosen_server)

        return config_file, auth_file

if __name__ == "__main__":
    vpn = Vpn()
    config_file, auth_file = vpn.choose_random_configuration()
    print(f"Config file: {config_file}")
    print(f"Auth file: {auth_file}")

    vpn.start_vpn(auth_file, config_file)
