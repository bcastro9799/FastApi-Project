from os import environ

from config import load_env_all_files

load_env_all_files()

SERVER_IP = str(environ.get("SERVER_IP","127.0.0.1"))
SERVER_PORT = str(environ.get("SERVER_PORT","8000"))

