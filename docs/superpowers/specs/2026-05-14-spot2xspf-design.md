# spot2xspf Design

## Overview

A Python CLI tool that accepts a Spotify playlist (URL, URI, or bare ID) and writes XSPF to stdout. Targets public playlists only using the Spotify Client Credentials auth flow.

## Structure

```
spot2xspf/
  __init__.py
  __main__.py      # entry point: arg parsing, credential loading, orchestration
  spotify.py       # spotipy wrapper: fetch playlist metadata and all tracks
  xspf.py          # build XSPF XML from playlist data
pyproject.toml
```

## Credentials

Priority order: CLI flags > environment variables > config file.

- **CLI flags**: `--client-id`, `--client-secret`
- **Environment variables**: `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET` (read natively by spotipy)
- **Config file**: `~/.config/spot2xspf/config` in INI format:
  ```ini
  [spotify]
  client_id = ...
  client_secret = ...
  ```

Fail fast with a clear error to stderr if credentials are missing from all sources.

## Input Parsing

Accept any of the following and extract the bare playlist ID:

- `https://open.spotify.com/playlist/<id>?si=...`
- `spotify:playlist:<id>`
- `<id>` (bare ID)

## Data Flow

1. Resolve credentials (flags > env > config file)
2. Parse playlist ID from the positional argument
3. Authenticate with Spotify using Client Credentials flow via spotipy
4. Fetch playlist metadata: title, description, image URL
5. Fetch all tracks (paginate using spotipy's `playlist_items`)
6. Build XSPF XML using `xml.etree.ElementTree`
7. Print to stdout

## XSPF Output

Namespace: `http://xspf.org/ns/0/`, version 1.

Playlist-level elements:
- `<title>` — playlist name
- `<annotation>` — playlist description
- `<image>` — playlist cover art URL

Per-track elements:
- `<title>` — track name
- `<creator>` — first artist name
- `<album>` — album name
- `<duration>` — duration in milliseconds
- `<location>` — Spotify track URI (e.g. `spotify:track:...`)
- `<image>` — album art URL (largest available image)

Fields are omitted (not written as empty tags) when the Spotify API returns no value.

## Error Handling

All errors write a human-readable message to stderr and exit with a non-zero code:

- Missing credentials → explain which are missing and how to provide them
- Invalid playlist ID → report the bad value
- Private playlist → tell user only public playlists are supported
- Network / API errors → surface the spotipy exception message

## Dependencies

- `spotipy` — Spotify Web API client
- `click` — CLI argument and option parsing

## Packaging

`pyproject.toml` with a `[project.scripts]` entry point:

```toml
[project.scripts]
spot2xspf = "spot2xspf.__main__:main"
```

Install with `pip install .` or `pipx install .`.
