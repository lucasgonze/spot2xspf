import configparser
from pathlib import Path

import click


def load_credentials(client_id, client_secret, config_path=None):
    if client_id and client_secret:
        return client_id, client_secret
    if config_path is None:
        config_path = Path.home() / ".config" / "spot2xspf" / "config"
    config = configparser.ConfigParser()
    if Path(config_path).exists():
        config.read(config_path)
        file_id = config.get("spotify", "client_id", fallback=None)
        file_secret = config.get("spotify", "client_secret", fallback=None)
        if file_id and file_secret:
            return file_id, file_secret
    raise click.UsageError(
        "Spotify credentials not found. Provide --client-id/--client-secret, "
        "set SPOTIPY_CLIENT_ID/SPOTIPY_CLIENT_SECRET, or add them to "
        "~/.config/spot2xspf/config."
    )
