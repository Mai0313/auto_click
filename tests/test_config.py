import os
from pathlib import Path

import yaml

from src.utils.config import ConfigModel

config_path = Path("./configs/games").rglob("*.yaml")
config_contents = [f.read_text(encoding="utf-8") for f in config_path]
config_dicts = [yaml.safe_load(content) for content in config_contents]


def test_load_config() -> None:
    for config_dict in config_dicts:
        config = ConfigModel(**config_dict)
        assert config.target is not None, "Target should not be None"
        assert isinstance(config.image_list, list), "Image list should be a list"


def test_image_config() -> None:
    for config_dict in config_dicts:
        config = ConfigModel(**config_dict)
        for image in config.image_list:
            if not os.path.exists(image.image_path):
                raise FileNotFoundError(f"Image not found: {image.image_path}")
