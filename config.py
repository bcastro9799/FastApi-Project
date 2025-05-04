import os
from dotenv import load_dotenv

def load_env_all_files():
    """
    Loads all environment variables from every `.env` file located in the `env_files` directory
    within the current working directory.
    """
    cwd = os.getcwd()
    env_folder = f"{cwd}/env_files"
    for file_name in os.listdir(env_folder):
        if file_name.endswith(".env"):
            env_file = os.path.join(env_folder,file_name)
            load_dotenv(env_file)