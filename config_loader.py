import os

def load_config():
    config = {}
    if os.path.exists("config.env"):
        with open("config.env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    config[key] = value
    return config

# Load once when imported
CONF = load_config()