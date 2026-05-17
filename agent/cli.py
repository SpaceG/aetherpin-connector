import argparse
import sys
import os

from .watcher import watch_folder
from .sender import DEFAULT_API
from . import config as cfg


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


def ask_autostart() -> bool:
    """Ask user if they want auto-start on boot (Windows only)."""
    import subprocess, platform
    if platform.system() != 'Windows':
        return False
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        ans = messagebox.askyesno('AetherPin Connector',
                                   'Start automatically when Windows boots?\n\n'
                                   '(You can change this later by running the .exe with --reconfigure)')
        root.destroy()
        return bool(ans)
    except Exception:
        return False


def first_run_setup():
    """Collect key + folder + auto-start preference, save to config."""
    api_key = ask_key()
    if not api_key.startswith('ap_'):
        print('Error: API key must start with "ap_"')
        sys.exit(1)

    watch_path = pick_folder()
    enable_autostart = ask_autostart()

    cfg.save({
        'api_key': api_key,
        'watch_path': watch_path,
        'api_url': DEFAULT_API,
        'autostart': enable_autostart,
    })

    if enable_autostart:
        exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
        ok = cfg.autostart_enable(exe)
        print(f'[setup] Auto-start on boot: {"enabled" if ok else "failed"}')

    return api_key, watch_path, DEFAULT_API


def main():
    parser = argparse.ArgumentParser(
        prog='aetherpin-connector',
        description='AetherPin Connector — send telescope data to the live sky map',
    )
    parser.add_argument('--key', default=None, help='Override saved API key')
    parser.add_argument('--watch', default=None, help='Override saved watch folder')
    parser.add_argument('--api', default=None, help='Override API endpoint URL')
    parser.add_argument('--reconfigure', action='store_true', help='Re-run setup (asks for key, folder, autostart)')
    parser.add_argument('--no-autostart', action='store_true', help='Disable auto-start on boot')
    args = parser.parse_args()

    if args.no_autostart:
        cfg.autostart_disable()
        print('[setup] Auto-start disabled.')
        sys.exit(0)

    saved = cfg.load()

    if args.reconfigure or not saved.get('api_key') or not saved.get('watch_path'):
        # First run or explicit reconfigure
        print('AetherPin Connector — Setup')
        api_key, watch_path, api_url = first_run_setup()
    else:
        api_key = saved.get('api_key')
        watch_path = saved.get('watch_path')
        api_url = saved.get('api_url') or DEFAULT_API

    # CLI flags override saved config
    if args.key: api_key = args.key
    if args.watch: watch_path = args.watch
    if args.api: api_url = args.api

    if not api_key.startswith('ap_'):
        print('Error: API key must start with "ap_"')
        sys.exit(1)

    print('AetherPin Connector v0.2.4')
    print(f'Server:  {api_url}')
    print(f'API key: {api_key[:6]}...{api_key[-4:]}')
    print(f'Folder:  {watch_path}')

    watch_folder(watch_path, api_key, api_url)


if __name__ == '__main__':
    main()
