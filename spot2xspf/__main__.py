import configparser
from pathlib import Path

import click
import spotipy

from .spotify import fetch_playlist, parse_playlist_id
from .xspf import build_xspf


def load_credentials(client_id, client_secret, config_path=None):
    # client_id/client_secret already incorporate env vars via click's envvar= option
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
        "set SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET, or add them to "
        "~/.config/spot2xspf/config."
    )


@click.command()
@click.argument("playlist")
@click.option("--client-id", envvar="SPOTIFY_CLIENT_ID", default=None)
@click.option("--client-secret", envvar="SPOTIFY_CLIENT_SECRET", default=None)
def main(playlist, client_id, client_secret):
    client_id, client_secret = load_credentials(client_id, client_secret)
    playlist_id = parse_playlist_id(playlist)
    try:
        data = fetch_playlist(playlist_id, client_id, client_secret)
    except spotipy.exceptions.SpotifyException as e:
        raise click.ClickException(str(e)) from e
    click.echo(build_xspf(data))
