from os import environ

def get_env(key: str, default):
    val = environ.get(key, default)
    if val == "":
        return default
    return val
