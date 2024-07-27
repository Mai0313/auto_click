from src.utils.config_utils import load_hydra_config


def test_load_hydra_config() -> None:
    config = load_hydra_config()
    assert isinstance(config, dict)
