<p align="center">
  <img src="https://aetherpin.com/assets/img/og-image.png" alt="AetherPin" width="100%">
</p>

<p align="center">
  <a href="https://aetherpin.com/connector">aetherpin.com/connector</a>
</p>

# AetherPin Connector

Link your telescope to the [AetherPin](https://aetherpin.com) live space map. The Connector watches your imaging folder for new FITS, XISF, or SER files, reads the target coordinates from the headers, and sends a live pin to the map. Everyone can see what you're imaging — in real time.

## Download

| Platform | Download |
|----------|----------|
| Windows | [AetherPin.Connector.exe](https://github.com/SpaceG/aetherpin-connector/releases/download/v0.2.0/AetherPin.Connector.exe) |
| macOS | [AetherPin.Connector.Mac.zip](https://github.com/SpaceG/aetherpin-connector/releases/download/v0.2.0/AetherPin.Connector.Mac.zip) |
| Linux | [AetherPin.Connector.Linux](https://github.com/SpaceG/aetherpin-connector/releases/download/v0.2.0/AetherPin.Connector.Linux) |

Or browse all releases: [GitHub Releases](https://github.com/SpaceG/aetherpin-connector/releases)

## Setup

1. Create an account on [aetherpin.com](https://aetherpin.com)
2. Go to [Profile](https://aetherpin.com/profile) → Remote Telescope Integration
3. Register your telescope and click **Generate API Key** — copy the key immediately (shown once)
4. Download and run the Connector
5. Paste your API key, select your image folder
6. Done — your pin appears on the [space map](https://aetherpin.com/space) within 15 seconds

## How it works

```
Telescope PC                     AetherPin Server              Browser
┌──────────────────┐             ┌──────────────────┐          ┌──────────┐
│ AetherPin        │   POST      │ /api/remote-     │   GET    │ /space   │
│ Connector        │────────────▶│ telescope/live   │◀─────────│          │
│                  │  on new file │                  │  polling │          │
└──────────────────┘             └──────────────────┘          └──────────┘
  watches folder                   stores live status            shows pin
  reads FITS/XISF/SER headers     2 min timeout = offline       on space map
```

The Connector runs in the background. When your capture software (NINA, SharpCap, FireCapture, etc.) saves a new file, the Connector picks it up, extracts the target name and coordinates, and sends a live pin to the server.

When you stop imaging or close the Connector, the pin disappears from the map after 2 minutes.

## Supported formats

| Format | Target source | Coordinate source |
|--------|--------------|-------------------|
| FITS (.fits, .fit) | `OBJECT` header | `RA` + `DEC` headers |
| XISF (.xisf) | `OBJECT` header | `RA` + `DEC` headers |
| SER (.ser) | Filename (e.g. `Sun_12_51_34.ser`) | Built-in lookup table |

## CLI flags

```
python -m agent [OPTIONS]

--key <api_key>      Override saved API key
--watch <path>       Override saved watch folder
--api <url>          Override API endpoint
--reconfigure        Re-run setup dialogs
--no-autostart       Disable Windows boot auto-start
```

## Features

- **Auto-start on Windows** — registers in startup registry, runs on boot
- **Persistent config** — saves credentials to system config directory
- **Recursive watching** — scans subfolders (SharpCap/FireCapture save per-object)
- **Native dialogs** — folder picker on Mac (osascript) and Windows (tkinter)
- **Cross-platform** — Windows .exe, macOS .app, Linux binary

## Build from source

Requires Python 3.8+.

```bash
git clone https://github.com/SpaceG/aetherpin-connector
cd aetherpin-connector
pip install astropy watchdog requests
python -m agent
```

## Build standalone binary

```bash
pip install pyinstaller
python build.py
```

Output in `dist/`. Uses PyInstaller onefile mode (~38 MB, bundles Python runtime).

## Config location

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\AetherPin\config.json` |
| macOS | `~/Library/Application Support/AetherPin/config.json` |
| Linux | `~/.config/aetherpin/config.json` |

## License

MIT
