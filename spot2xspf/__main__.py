import configparser
import re
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


def _safe_filename(title: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "", title).strip()
    return name or "playlist"


@click.command()
@click.argument("playlist")
@click.option("--client-id", envvar="SPOTIFY_CLIENT_ID", default=None)
@click.option("--client-secret", envvar="SPOTIFY_CLIENT_SECRET", default=None)
@click.option("-O", "--remote-name", is_flag=True, default=False,
              help="Write output to a file named after the playlist title.")
def main(playlist, client_id, client_secret, remote_name):
    client_id, client_secret = load_credentials(client_id, client_secret)
    playlist_id = parse_playlist_id(playlist)
    try:
        data = fetch_playlist(playlist_id, client_id, client_secret)
    except spotipy.exceptions.SpotifyException as e:
        raise click.ClickException(str(e)) from e
    xspf = build_xspf(data)
    if remote_name:
        filename = _safe_filename(data.get("title") or playlist_id) + ".xspf"
        Path(filename).write_text(xspf)
        click.echo(filename, err=True)
    else:
        click.echo(xspf)
