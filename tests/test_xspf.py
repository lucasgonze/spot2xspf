import xml.etree.ElementTree as ET
from spot2xspf.xspf import build_xspf

XSPF_NS = "http://xspf.org/ns/0/"

SAMPLE_PLAYLIST = {
    "title": "My Playlist",
    "creator": "Jane Doe",
    "description": "A great playlist",
    "identifier": "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
    "image": "https://img.example.com/cover.jpg",
    "tracks": [
        {
            "title": "Track One",
            "creator": "Artist A",
            "album": "Album X",
            "duration": 210000,
            "identifier": "spotify:track:aaa",
            "image": "https://img.example.com/album.jpg",
        }
    ],
}


def parse(xml_str):
    return ET.fromstring(xml_str)


def test_output_is_valid_xml():
    root = parse(build_xspf(SAMPLE_PLAYLIST))
    assert root.tag == f"{{{XSPF_NS}}}playlist"


def test_playlist_title():
    root = parse(build_xspf(SAMPLE_PLAYLIST))
    assert root.find(f"{{{XSPF_NS}}}title").text == "My Playlist"


def test_playlist_creator():
    root = parse(build_xspf(SAMPLE_PLAYLIST))
    assert root.find(f"{{{XSPF_NS}}}creator").text == "Jane Doe"


def test_playlist_description():
    root = parse(build_xspf(SAMPLE_PLAYLIST))
    assert root.find(f"{{{XSPF_NS}}}annotation").text == "A great playlist"


def test_playlist_identifier():
    root = parse(build_xspf(SAMPLE_PLAYLIST))
    assert root.find(f"{{{XSPF_NS}}}identifier").text == "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"


def test_playlist_image():
    root = parse(build_xspf(SAMPLE_PLAYLIST))
    assert root.find(f"{{{XSPF_NS}}}image").text == "https://img.example.com/cover.jpg"


def test_track_fields():
    root = parse(build_xspf(SAMPLE_PLAYLIST))
    track = root.find(f".//{{{XSPF_NS}}}track")
    assert track.find(f"{{{XSPF_NS}}}title").text == "Track One"
    assert track.find(f"{{{XSPF_NS}}}creator").text == "Artist A"
    assert track.find(f"{{{XSPF_NS}}}album").text == "Album X"
    assert track.find(f"{{{XSPF_NS}}}duration").text == "210000"
    assert track.find(f"{{{XSPF_NS}}}identifier").text == "spotify:track:aaa"
    assert track.find(f"{{{XSPF_NS}}}image").text == "https://img.example.com/album.jpg"


def test_missing_fields_omitted():
    playlist = {
        "title": "Minimal",
        "description": None,
        "image": None,
        "tracks": [
            {
                "title": "Track",
                "creator": None,
                "album": None,
                "duration": None,
                "identifier": "spotify:track:aaa",
                "image": None,
            }
        ],
    }
    root = parse(build_xspf(playlist))
    assert root.find(f"{{{XSPF_NS}}}annotation") is None
    track = root.find(f".//{{{XSPF_NS}}}track")
    assert track.find(f"{{{XSPF_NS}}}creator") is None
    assert track.find(f"{{{XSPF_NS}}}duration") is None


def test_xml_declaration():
    result = build_xspf(SAMPLE_PLAYLIST)
    assert result.startswith("<?xml")
