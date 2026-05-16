from __future__ import annotations

import re
from html import unescape
from urllib.parse import urlparse

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def fetch_playlist(playlist_id: str, client_id: str, client_secret: str) -> dict:
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret,
            cache_handler=spotipy.cache_handler.MemoryCacheHandler(),
        ),
        requests_timeout=15,
    )
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
                "identifier": track.get("uri"),
                "image": _largest_image(track.get("album", {}).get("images", [])),
            })
        if not page.get("next"):
            break
        offset += 100
    owner = data.get("owner") or {}
    return {
        "title": data.get("name"),
        "creator": owner.get("display_name") or owner.get("id"),
        "description": unescape(desc) if (desc := data.get("description")) else None,
        "identifier": data.get("uri"),
        "image": _largest_image(data.get("images", [])),
        "tracks": tracks,
    }


def _largest_image(images: list) -> str | None:
    if not images:
        return None
    return max(images, key=lambda i: i.get("height") or 0)["url"]


_SPOTIFY_ID_RE = re.compile(r'^[A-Za-z0-9]+$')


def parse_playlist_id(input: str) -> str:
    input = input.strip()
    if input.startswith("spotify:playlist:"):
        parts = input.split(":")
        if len(parts) != 3 or not _SPOTIFY_ID_RE.match(parts[2]):
            raise ValueError(f"Invalid Spotify playlist URI: {input!r}")
        return parts[2]
    if input.startswith("http"):
        candidate = urlparse(input).path.rstrip("/").split("/")[-1]
        if not candidate or not _SPOTIFY_ID_RE.match(candidate):
            raise ValueError(f"Could not extract a playlist ID from URL: {input!r}")
        return candidate
    return input
