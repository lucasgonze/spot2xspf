import configparser
import pytest
from pathlib import Path
from click import UsageError
from spot2xspf.__main__ import load_credentials

import click
from unittest.mock import patch
from click.testing import CliRunner
from spot2xspf.__main__ import main

MOCK_PLAYLIST_DATA = {
    "title": "My Playlist",
    "description": "Great songs",
    "image": "https://img.example.com/cover.jpg",
    "tracks": [
        {
            "title": "Track One",
            "creator": "Artist A",
            "album": "Album X",
            "duration": 180000,
            "location": "spotify:track:aaa",
            "image": "https://img.example.com/album.jpg",
        }
    ],
}


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


def test_cli_outputs_xspf():
    runner = CliRunner()
    with patch("spot2xspf.__main__.fetch_playlist", return_value=MOCK_PLAYLIST_DATA):
        result = runner.invoke(
            main,
            ["37i9dQZF1DXcBWIGoYBM5M", "--client-id", "test_id", "--client-secret", "test_secret"],
        )
    assert result.exit_code == 0
    assert "<?xml" in result.output
    assert "My Playlist" in result.output
    assert "Track One" in result.output


def test_cli_missing_credentials_exits_nonzero():
    runner = CliRunner()
    with patch("spot2xspf.__main__.load_credentials") as mock_creds:
        mock_creds.side_effect = click.UsageError("Spotify credentials not found.")
        result = runner.invoke(main, ["37i9dQZF1DXcBWIGoYBM5M"])
    assert result.exit_code != 0
