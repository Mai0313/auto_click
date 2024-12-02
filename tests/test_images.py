import os

import yaml
import pytest

from src.types.image_models import ImageModel

root_path = "./configs/games"
config_path = [
    f for f in os.listdir(root_path) if f.endswith(".yaml") and not f.startswith("default")
]
config_path = [os.path.join(root_path, f) for f in config_path]


def load_yaml(config_path: str) -> dict:
    with open(config_path, encoding="utf-8") as file:
        configs = yaml.safe_load(file)
    return configs


@pytest.mark.parametrize("config_path", config_path)
def test_load_image(config_path: str) -> None:
    config_dict = load_yaml(config_path=config_path)
    image_list = config_dict["image_list"]
    for image_dict in image_list:
        image_info = ImageModel(**image_dict)
        if not os.path.exists(image_info.image_path):
            raise FileNotFoundError(f"Image not found: {image_info.image_path}")


if __name__ == "__main__":
    test_load_image()
