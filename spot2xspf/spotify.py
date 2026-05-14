from urllib.parse import urlparse

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def fetch_playlist(playlist_id: str, client_id: str, client_secret: str) -> dict:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret,
    ))
    data = sp.playlist(playlist_id)
    tracks = []
    offset = 0
    while True:
        page = sp.playlist_items(playlist_id, offset=offset, limit=100)
        for item in page["items"]:
            track = item.get("track")
            if not track:
                continue
            tracks.append({
                "title": track.get("name"),
                "creator": track["artists"][0]["name"] if track.get("artists") else None,
                "album": track.get("album", {}).get("name"),
                "duration": track.get("duration_ms"),
                "location": track.get("uri"),
                "image": _largest_image(track.get("album", {}).get("images", [])),
            })
        if not page.get("next"):
            break
        offset += 100
    return {
        "title": data.get("name"),
        "description": data.get("description"),
        "image": _largest_image(data.get("images", [])),
        "tracks": tracks,
    }


def _largest_image(images: list) -> str | None:
    if not images:
        return None
    return max(images, key=lambda i: i.get("height") or 0)["url"]


def parse_playlist_id(input: str) -> str:
    input = input.strip()
    if input.startswith("spotify:playlist:"):
        return input.split(":")[-1]
    if input.startswith("http"):
        return urlparse(input).path.rstrip("/").split("/")[-1]
    return input
