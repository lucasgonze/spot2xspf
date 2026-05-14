import configparser
import pytest
from pathlib import Path
from click import UsageError
from spot2xspf.__main__ import load_credentials


def test_returns_explicit_credentials():
    assert load_credentials("id1", "secret1") == ("id1", "secret1")


def test_reads_from_config_file(tmp_path):
    config_path = tmp_path / "config"
    config = configparser.ConfigParser()
    config["spotify"] = {"client_id": "file_id", "client_secret": "file_secret"}
    with open(config_path, "w") as f:
        config.write(f)
    assert load_credentials(None, None, config_path=config_path) == ("file_id", "file_secret")


def test_raises_when_no_credentials(tmp_path):
    missing = tmp_path / "nonexistent"
    with pytest.raises(UsageError, match="credentials"):
        load_credentials(None, None, config_path=missing)


def test_explicit_takes_priority_over_config(tmp_path):
    config_path = tmp_path / "config"
    config = configparser.ConfigParser()
    config["spotify"] = {"client_id": "file_id", "client_secret": "file_secret"}
    with open(config_path, "w") as f:
        config.write(f)
    assert load_credentials("cli_id", "cli_secret", config_path=config_path) == ("cli_id", "cli_secret")
