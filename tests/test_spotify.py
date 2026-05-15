import pytest
from unittest.mock import patch
from spot2xspf.spotify import parse_playlist_id, fetch_playlist


def test_bare_id():
    assert parse_playlist_id("37i9dQZF1DXcBWIGoYBM5M") == "37i9dQZF1DXcBWIGoYBM5M"


def test_https_url():
    assert parse_playlist_id(
        "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=abc"
    ) == "37i9dQZF1DXcBWIGoYBM5M"


def test_spotify_uri():
    assert parse_playlist_id("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M") == "37i9dQZF1DXcBWIGoYBM5M"


def test_strips_whitespace():
    assert parse_playlist_id("  37i9dQZF1DXcBWIGoYBM5M  ") == "37i9dQZF1DXcBWIGoYBM5M"


def test_invalid_uri_raises():
    with pytest.raises(ValueError, match="Invalid Spotify playlist URI"):
        parse_playlist_id("spotify:playlist:")


def test_invalid_url_raises():
    with pytest.raises(ValueError, match="Could not extract a playlist ID from URL"):
        parse_playlist_id("https://open.spotify.com/")


def test_url_with_trailing_slash():
    assert parse_playlist_id(
        "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M/"
    ) == "37i9dQZF1DXcBWIGoYBM5M"


MOCK_PLAYLIST = {
    "name": "Test Playlist",
    "description": "A test playlist",
    "uri": "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
    "owner": {"display_name": "Jane Doe", "id": "janedoe"},
    "images": [{"url": "https://img.example.com/cover.jpg", "height": 640}],
}

MOCK_PAGE = {
    "items": [
        {
            "track": {
                "name": "Track One",
                "artists": [{"name": "Artist A"}],
                "album": {
                    "name": "Album X",
                    "images": [{"url": "https://img.example.com/album.jpg", "height": 300}],
                },
                "duration_ms": 210000,
                "uri": "spotify:track:aaa",
            }
        }
    ],
    "next": None,
}


def test_fetch_playlist_returns_expected_shape():
    with patch("spot2xspf.spotify.spotipy.Spotify") as MockSpotify:
        sp = MockSpotify.return_value
        sp.playlist.return_value = MOCK_PLAYLIST
        sp.playlist_items.return_value = MOCK_PAGE

        result = fetch_playlist("37i9dQZF1DXcBWIGoYBM5M", "client_id", "client_secret")

    assert result["title"] == "Test Playlist"
    assert result["creator"] == "Jane Doe"
    assert result["description"] == "A test playlist"
    assert result["identifier"] == "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"
    assert result["image"] == "https://img.example.com/cover.jpg"
    assert len(result["tracks"]) == 1
    track = result["tracks"][0]
    assert track["title"] == "Track One"
    assert track["creator"] == "Artist A"
    assert track["album"] == "Album X"
    assert track["duration"] == 210000
    assert track["identifier"] == "spotify:track:aaa"
    assert track["image"] == "https://img.example.com/album.jpg"


def test_fetch_playlist_paginates():
    page_1 = {
        "items": [
            {
                "track": {
                    "name": "Track One",
                    "artists": [{"name": "Artist A"}],
                    "album": {"name": "Album X", "images": []},
                    "duration_ms": 180000,
                    "uri": "spotify:track:aaa",
                }
            }
        ],
        "next": "https://api.spotify.com/v1/playlists/.../tracks?offset=1",
    }
    page_2 = {
        "items": [
            {
                "track": {
                    "name": "Track Two",
                    "artists": [{"name": "Artist B"}],
                    "album": {"name": "Album Y", "images": []},
                    "duration_ms": 200000,
                    "uri": "spotify:track:bbb",
                }
            }
        ],
        "next": None,
    }
    with patch("spot2xspf.spotify.spotipy.Spotify") as MockSpotify:
        sp = MockSpotify.return_value
        sp.playlist.return_value = MOCK_PLAYLIST
        sp.playlist_items.side_effect = [page_1, page_2]

        result = fetch_playlist("37i9dQZF1DXcBWIGoYBM5M", "client_id", "client_secret")

    assert len(result["tracks"]) == 2


def test_fetch_playlist_skips_null_tracks():
    page = {
        "items": [
            {"track": None},
            {
                "track": {
                    "name": "Real Track",
                    "artists": [{"name": "Artist"}],
                    "album": {"name": "Album", "images": []},
                    "duration_ms": 180000,
                    "uri": "spotify:track:ccc",
                }
            },
        ],
        "next": None,
    }
    with patch("spot2xspf.spotify.spotipy.Spotify") as MockSpotify:
        sp = MockSpotify.return_value
        sp.playlist.return_value = MOCK_PLAYLIST
        sp.playlist_items.return_value = page

        result = fetch_playlist("37i9dQZF1DXcBWIGoYBM5M", "client_id", "client_secret")

    assert len(result["tracks"]) == 1
    assert result["tracks"][0]["title"] == "Real Track"
