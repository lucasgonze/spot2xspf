from .spotify import fetch_playlist, parse_playlist_id
from .xspf import build_xspf


def convert(playlist: str, client_id: str, client_secret: str) -> str:
    """Fetch a Spotify playlist and return it as an XSPF string.

    playlist: playlist ID, URI (spotify:playlist:...), or HTTPS URL.
    """
    playlist_id = parse_playlist_id(playlist)
    data = fetch_playlist(playlist_id, client_id, client_secret)
    return build_xspf(data)


__all__ = ["convert", "fetch_playlist", "parse_playlist_id", "build_xspf"]
