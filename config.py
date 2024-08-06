import subprocess

# Verifica se o arquivo está bloqueado.
def isblock(path:str) -> bool:
    try:

        result = subprocess.run(["lsattr", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise Exception(f"Erro ao executar o lsattr: {result.stderr}")

        return "i" in result.stdout

    except Exception as err:
        print(f"Houve um problema: {err}")
        return False
        

# Bloqueia o arquivo para evitar a modificação.
def block(path:str) -> bool:
    try:
        result = subprocess.run(["chattr", "+i", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise Exception(f"Erro ao executar o chattr: {result.stderr}")
        
        return True

    except Exception as err:
        print(f"Houve um problema: {err}")
        return False

# Desbloqueia o arquivo.
def unblock(path:str) -> bool:
    try:
        result = subprocess.run(["chattr", "-i", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise Exception(f"Erro ao executar o chattr: {result.stderr}")

        return True

    except Exception as err:
        print(f"Houve um problema: {err}")
        return False


def write(path:str, value) -> bool:
    try:
        # Check if file is blocked
        if isblock(path):
            unblock(path)

        with open(path, "w") as file:
            file.write(value)
            
        block(path)

        return True

    except Exception as err:
        print(f"Houve um problema {err}")

