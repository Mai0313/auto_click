from pathlib import Path
import tempfile

import yaml
import pandas as pd
import pytest

from src.types.image_models import ImageModel


@pytest.fixture(scope="module")
def image_model() -> ImageModel:
    config_path = "./configs/games/all_stars.yaml"
    config_obj = Path(config_path)
    config_content = config_obj.read_text(encoding="utf-8")
    config_dict = yaml.safe_load(config_content)
    image_list = config_dict["image_list"]
    image_config_dict = image_list[0]
    return ImageModel(**image_config_dict)


def get_temp_file(suffix: str, prefix: str) -> str:
    temp_folder = Path("./.cache/pytest/tempfile")
    temp_folder.mkdir(exist_ok=True, parents=True)
    _, temp_file = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=temp_folder)
    return temp_file


def test_export_json(image_model: ImageModel) -> None:
    output_path = get_temp_file(".json", "sync_")
    result = image_model.export_json(output_path)
    assert isinstance(result, dict)
    assert result == image_model.model_dump()


def test_export_yaml(image_model: ImageModel) -> None:
    output_path = get_temp_file(".yaml", "sync_")
    result = image_model.export_yaml(output_path)
    assert isinstance(result, dict)
    assert result == image_model.model_dump()


def test_export_csv(image_model: ImageModel) -> None:
    output_path = get_temp_file(".csv", "sync_")
    result = image_model.export_csv(output_path)
    assert isinstance(result, pd.DataFrame)
