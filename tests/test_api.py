from unittest.mock import patch
import spot2xspf
from spot2xspf import convert, fetch_playlist, parse_playlist_id, build_xspf

MOCK_PLAYLIST = {
    "name": "Test Playlist",
    "description": "A test playlist",
    "uri": "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
    "owner": {"display_name": "Jane Doe", "id": "janedoe"},
    "images": [],
}

MOCK_PAGE = {
    "items": [
        {
            "track": {
                "name": "Track One",
                "artists": [{"name": "Artist A"}],
                "album": {"name": "Album X", "images": []},
                "duration_ms": 210000,
                "uri": "spotify:track:aaa",
            }
        }
    ],
    "next": None,
}


def test_public_symbols():
    assert callable(convert)
    assert callable(fetch_playlist)
    assert callable(parse_playlist_id)
    assert callable(build_xspf)


def test_convert_returns_xspf():
    with patch("spot2xspf.spotify.spotipy.Spotify") as MockSpotify:
        sp = MockSpotify.return_value
        sp.playlist.return_value = MOCK_PLAYLIST
        sp.playlist_items.return_value = MOCK_PAGE
        result = convert("37i9dQZF1DXcBWIGoYBM5M", "client_id", "client_secret")
    assert result.startswith("<?xml")
    assert "Test Playlist" in result
    assert "Track One" in result
