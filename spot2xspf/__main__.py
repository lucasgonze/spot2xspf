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
        "set SPOTIFY_CLIENT_ID/SPOTIFY_CLIENT_SECRET, or create "
        "~/.config/spot2xspf/config with contents:\n\n"
        "  [spotify]\n"
        "  client_id = YOUR_CLIENT_ID\n"
        "  client_secret = YOUR_CLIENT_SECRET\n\n"
        "Obtain credentials at https://developer.spotify.com/dashboard."
    )


def _safe_filename(title: str, fallback: str = "playlist") -> str:
    name = re.sub(r'[^\w.-]+', "_", title).strip("_")
    return name or fallback


@click.command(context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True)
@click.argument("playlist", metavar="PLAYLIST")
@click.option("--client-id", envvar="SPOTIFY_CLIENT_ID", default=None,
              help="Spotify API client ID. Falls back to SPOTIFY_CLIENT_ID env var or ~/.config/spot2xspf/config.")
@click.option("--client-secret", envvar="SPOTIFY_CLIENT_SECRET", default=None,
              help="Spotify API client secret. Falls back to SPOTIFY_CLIENT_SECRET env var or ~/.config/spot2xspf/config.")
@click.option("-O", "--save", is_flag=True, default=False,
              help="Write output to playlists/<title>.xspf instead of stdout. "
                   "Spaces and special characters in the title are replaced with underscores. "
                   "The full path is printed to stderr.")
def main(playlist, client_id, client_secret, save):
    """Convert a Spotify playlist to XSPF format.

    PLAYLIST can be a Spotify playlist ID, URI (spotify:playlist:...), or HTTPS URL.
    Output is written to stdout unless -O is given.
    """
    client_id, client_secret = load_credentials(client_id, client_secret)
    try:
        playlist_id = parse_playlist_id(playlist)
    except ValueError as e:
        raise click.UsageError(str(e)) from e
    click.echo("Fetching playlist…", err=True)
    try:
        data = fetch_playlist(playlist_id, client_id, client_secret)
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 404:
            raise click.ClickException(
                "Playlist not found. If it is private, client credentials cannot access it."
            ) from e
        raise click.ClickException(str(e)) from e
    click.echo(f"{len(data['tracks'])} tracks.", err=True)
    xspf = build_xspf(data)
    if save:
        out_dir = Path("playlists")
        out_dir.mkdir(exist_ok=True)
        filename = _safe_filename(data.get("title") or "", fallback=playlist_id) + ".xspf"
        out_path = out_dir / filename
        out_path.write_text(xspf, encoding="utf-8")
        click.echo(str(out_path.resolve()), err=True)
    else:
        click.echo(xspf)
