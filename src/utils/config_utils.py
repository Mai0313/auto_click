import yaml


def load_config(path: str) -> dict:
    with open(path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config
