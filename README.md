# spot2xspf

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

Convert a Spotify playlist to [XSPF](https://xspf.org) (XML Shareable Playlist Format).

```
$ spot2xspf https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
<?xml version='1.0' encoding='UTF-8'?>
<playlist xmlns="http://xspf.org/ns/0/" version="1">
  <title>Today's Top Hits</title>
  ...
```

## Installation

Requires Python 3.9 or later.

```sh
git clone https://github.com/lucasgonze/spot2xspf
cd spot2xspf
pip install .
```

## Spotify credentials

spot2xspf uses the Spotify Web API with [client credentials](https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow) — no user login required. You need a free Spotify developer account.

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) and create an app.
2. Copy the **Client ID** and **Client Secret**.

When using the CLI, credentials are read from (in order of priority):

1. `--client-id` / `--client-secret` flags
2. `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` environment variables
3. `~/.config/spot2xspf/config`:

When using the Python API, pass credentials directly to `convert()` or `fetch_playlist()`.

```ini
[spotify]
client_id = YOUR_CLIENT_ID
client_secret = YOUR_CLIENT_SECRET
```

> **Note:** Client credentials cannot access private playlists. The playlist must be public.

## Usage

```
Usage: spot2xspf [OPTIONS] PLAYLIST

  Convert a Spotify playlist to XSPF format.

  PLAYLIST can be a Spotify playlist ID, URI (spotify:playlist:...), or HTTPS URL.
  Output is written to stdout unless -O is given.

Options:
  --client-id TEXT      Spotify API client ID. Falls back to SPOTIFY_CLIENT_ID
                        env var or ~/.config/spot2xspf/config.
  --client-secret TEXT  Spotify API client secret. Falls back to
                        SPOTIFY_CLIENT_SECRET env var or
                        ~/.config/spot2xspf/config.
  -O, --save            Write output to playlists/<title>.xspf instead of
                        stdout. Spaces and special characters in the title are
                        replaced with underscores. The full path is printed to
                        stderr.
  -h, --help            Show this message and exit.
```

### Examples

Print XSPF to stdout:

```sh
spot2xspf 37i9dQZF1DXcBWIGoYBM5M
spot2xspf spotify:playlist:37i9dQZF1DXcBWIGoYBM5M
spot2xspf https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
```

Save to a file in `playlists/`:

```sh
spot2xspf -O https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
# → playlists/Today_s_Top_Hits.xspf
```

Redirect stdout to a specific file:

```sh
spot2xspf 37i9dQZF1DXcBWIGoYBM5M > my_playlist.xspf
```

## Python API

The package is importable and can be used directly from Python code.

### High-level

```python
import spot2xspf

xspf = spot2xspf.convert(
    "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
)
```

`convert()` accepts a playlist ID, URI, or HTTPS URL and returns XSPF as a string.

### Lower-level

```python
from spot2xspf import fetch_playlist, parse_playlist_id, build_xspf

playlist_id = parse_playlist_id("spotify:playlist:37i9dQZF1DXcBWIGoYBM5M")
data = fetch_playlist(playlist_id, client_id, client_secret)
# data is a plain dict — inspect or modify it before serializing
xspf = build_xspf(data)
```

## Output format

The generated XSPF includes:

| XSPF element | Source |
|---|---|
| `<playlist>/<title>` | Playlist name |
| `<playlist>/<creator>` | Owner display name |
| `<playlist>/<annotation>` | Playlist description |
| `<playlist>/<identifier>` | Spotify playlist URI |
| `<playlist>/<image>` | Playlist cover art URL |
| `<track>/<title>` | Track name |
| `<track>/<creator>` | Primary artist |
| `<track>/<album>` | Album name |
| `<track>/<duration>` | Duration in milliseconds |
| `<track>/<identifier>` | Spotify track URI |
| `<track>/<image>` | Album art URL |

Tracks with no `<location>` element cannot be played directly - they need a content resolver like [Parachord](https://github.com/Parachord/parachord); the Spotify URI in `<identifier>` identifies each track for import or scripting purposes.

## Development

```sh
pip install -e ".[dev]"
pytest
```
