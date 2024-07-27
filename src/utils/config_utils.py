import sys

from hydra import compose, initialize
from omegaconf import OmegaConf


def load_hydra_config() -> dict:
    args = sys.argv[1:]
    with initialize(config_path="../../configs", version_base="1.3"):
        cfg = compose(config_name="configs", overrides=args, return_hydra_config=True)
        config_dict = OmegaConf.to_container(cfg, resolve=False)
    return config_dict


if __name__ == "__main__":
    print(load_hydra_config())
