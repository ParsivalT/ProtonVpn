import subprocess

class ConfigManager:
    def __init__(self, path: str):
        self.path = path

    def is_blocked(self) -> bool:
        try:
            result = subprocess.run(["lsattr", self.path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                raise Exception(f"Erro ao executar o lsattr: {result.stderr}")
            return "i" in result.stdout
        except Exception as err:
            print(f"Houve um problema: {err}")
            return False

    def block(self) -> bool:
        try:
            result = subprocess.run(["chattr", "+i", self.path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                raise Exception(f"Erro ao executar o chattr: {result.stderr}")
            return True
        except Exception as err:
            print(f"Houve um problema: {err}")
            return False

    def unblock(self) -> bool:
        try:
            result = subprocess.run(["chattr", "-i", self.path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                raise Exception(f"Erro ao executar o chattr: {result.stderr}")
            return True
        except Exception as err:
            print(f"Houve um problema: {err}")
            return False

    def write(self, value: str) -> bool:
        try:
            # Check if file is blocked
            if self.is_blocked():
                self.unblock()
            with open(self.path, "w") as file:
                file.write(value)
            self.block()
            return True
        except Exception as err:
            print(f"Houve um problema {err}")
            return False
