"""Persistent config: API key, watch folder, server URL.
Stored in OS-appropriate location."""
import json
import os
from pathlib import Path
import platform


def config_path() -> Path:
    if platform.system() == 'Windows':
        base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
    elif platform.system() == 'Darwin':
        base = Path.home() / 'Library' / 'Application Support'
    else:
        base = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))

    folder = base / 'AetherPin'
    folder.mkdir(parents=True, exist_ok=True)
    return folder / 'config.json'


def load() -> dict:
    p = config_path()
    if not p.exists():
        return {}
    try:
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save(data: dict) -> None:
    p = config_path()
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def autostart_enable(exe_path: str) -> bool:
    """Add the connector to Windows startup (registry Run key).
    On Mac/Linux, returns False (use launchctl/systemd manually)."""
    if platform.system() != 'Windows':
        return False
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Run',
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, 'AetherPinConnector', 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f'[config] autostart failed: {e}')
        return False


def autostart_disable() -> bool:
    if platform.system() != 'Windows':
        return False
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Run',
                             0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, 'AetherPinConnector')
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False
