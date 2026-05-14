import pytest
from spot2xspf.spotify import parse_playlist_id


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
