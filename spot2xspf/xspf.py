import io
import xml.etree.ElementTree as ET

XSPF_NS = "http://xspf.org/ns/0/"


def build_xspf(playlist: dict) -> str:
    ET.register_namespace("", XSPF_NS)
    root = ET.Element(f"{{{XSPF_NS}}}playlist", version="1")
    _add_text(root, "title", playlist.get("title"))
    _add_text(root, "creator", playlist.get("creator"))
    _add_text(root, "annotation", playlist.get("description"))
    _add_text(root, "identifier", playlist.get("identifier"))
    _add_text(root, "image", playlist.get("image"))
    track_list = ET.SubElement(root, f"{{{XSPF_NS}}}trackList")
    for track in playlist.get("tracks", []):
        track_el = ET.SubElement(track_list, f"{{{XSPF_NS}}}track")
        _add_text(track_el, "title", track.get("title"))
        _add_text(track_el, "creator", track.get("creator"))
        _add_text(track_el, "album", track.get("album"))
        if track.get("duration") is not None:
            _add_text(track_el, "duration", str(track["duration"]))
        _add_text(track_el, "identifier", track.get("identifier"))
        _add_text(track_el, "image", track.get("image"))
    ET.indent(root)
    buf = io.BytesIO()
    ET.ElementTree(root).write(buf, xml_declaration=True, encoding="UTF-8")
    return buf.getvalue().decode("utf-8")


def _add_text(parent: ET.Element, tag: str, text) -> None:
    if text is not None and text != "":
        el = ET.SubElement(parent, f"{{{XSPF_NS}}}{tag}")
        el.text = text
