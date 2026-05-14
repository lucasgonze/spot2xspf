from urllib.parse import urlparse


def parse_playlist_id(input: str) -> str:
    input = input.strip()
    if input.startswith("spotify:playlist:"):
        return input.split(":")[-1]
    if input.startswith("http"):
        return urlparse(input).path.rstrip("/").split("/")[-1]
    return input
