import argparse
import sys

from .watcher import watch_folder
from .sender import DEFAULT_API


def pick_folder():
    """Open a native folder picker dialog (Mac/Linux/Windows)."""
    import subprocess, platform

    if platform.system() == 'Darwin':
        result = subprocess.run(
            ['osascript', '-e', 'POSIX path of (choose folder with prompt "Select your FITS image folder")'],
            capture_output=True, text=True
        )
        folder = result.stdout.strip()
    else:
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            folder = filedialog.askdirectory(title='Select your FITS image folder')
            root.destroy()
        except ImportError:
            folder = input('Enter path to FITS image folder: ').strip()

    if not folder:
        print('No folder selected. Exiting.')
        sys.exit(0)
    return folder


def ask_key():
    """Ask for the API key via dialog or terminal."""
    import subprocess, platform

    if platform.system() == 'Darwin':
        result = subprocess.run(
            ['osascript', '-e',
             'text returned of (display dialog "Paste your AetherPin API key:" default answer "ap_" with title "AetherPin Connector")'],
            capture_output=True, text=True
        )
        key = result.stdout.strip()
    else:
        try:
            import tkinter as tk
            from tkinter import simpledialog
            root = tk.Tk()
            root.withdraw()
            key = simpledialog.askstring('AetherPin Connector', 'Paste your API key:')
            root.destroy()
        except ImportError:
            key = input('Enter your API key: ').strip()

    if not key:
        print('No API key entered. Exiting.')
        sys.exit(0)
    return key.strip()


def ask_api(default: str):
    """Ask for the API endpoint URL."""
    import subprocess, platform

    prompt = 'Server URL (leave default for AetherPin.com):'
    if platform.system() == 'Darwin':
        script = (f'text returned of (display dialog "{prompt}" '
                  f'default answer "{default}" with title "AetherPin Connector")')
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        url = result.stdout.strip()
    else:
        try:
            import tkinter as tk
            from tkinter import simpledialog
            root = tk.Tk()
            root.withdraw()
            url = simpledialog.askstring('AetherPin Connector', prompt, initialvalue=default)
            root.destroy()
        except ImportError:
            url = input(f'API URL [{default}]: ').strip() or default

    return (url or default).strip()


def main():
    parser = argparse.ArgumentParser(
        prog='aetherpin-connector',
        description='AetherPin Connector — send telescope data to the live sky map',
    )
    parser.add_argument('--key', default=None, help='Your AetherPin API key (ap_...)')
    parser.add_argument('--watch', default=None, help='Path to FITS image folder')
    parser.add_argument('--api', default=DEFAULT_API, help='API endpoint URL')
    args = parser.parse_args()

    # If no API URL provided via CLI, ask via dialog (with default)
    api_url = args.api if args.api != DEFAULT_API else ask_api(DEFAULT_API)

    # If no key provided, open dialog
    api_key = args.key or ask_key()

    if not api_key.startswith('ap_'):
        print('Error: API key must start with "ap_"')
        sys.exit(1)

    # If no folder provided, open folder picker
    watch_path = args.watch or pick_folder()

    print('AetherPin Connector v0.1.0')
    print(f'Server:  {api_url}')
    print(f'API key: {api_key[:6]}...{api_key[-4:]}')
    print(f'Folder:  {watch_path}')

    watch_folder(watch_path, api_key, api_url)


if __name__ == '__main__':
    main()
