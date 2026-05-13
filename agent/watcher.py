import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .fits_reader import read_fits_header, is_fits_file
from .sender import send_status, send_offline


class FitsHandler(FileSystemEventHandler):
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
        self.current_target = None

    def on_created(self, event):
        if event.is_directory:
            return
        self._process(event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        self._process(event.src_path)

    def _process(self, path: str):
        if not is_fits_file(path):
            return

        try:
            data = read_fits_header(path)
        except Exception as e:
            print(f'[fits] Error reading {Path(path).name}: {e}')
            return

        if not data['target_name'] or not data['ra'] or not data['dec']:
            print(f'[fits] Incomplete header in {Path(path).name}, skipping')
            return

        # Only send if target changed
        if data['target_name'] == self.current_target:
            return

        self.current_target = data['target_name']

        try:
            send_status(self.api_key, data, self.api_url)
            print(f'[pin] {data["target_name"]} @ RA {data["ra"]} DEC {data["dec"]}')
        except Exception as e:
            print(f'[api] Send failed: {e}')


def watch_folder(folder: str, api_key: str, api_url: str):
    path = Path(folder)
    if not path.is_dir():
        raise FileNotFoundError(f'Watch folder not found: {folder}')

    handler = FitsHandler(api_key, api_url)

    # Recursively scan all existing files first (sorted by mtime, newest last)
    print(f'[scan] Checking existing files in {path} (recursive)...')
    files = [f for f in path.rglob('*') if f.is_file()]
    files.sort(key=lambda x: x.stat().st_mtime)
    for f in files:
        handler._process(str(f))

    observer = Observer()
    observer.schedule(handler, str(path), recursive=True)
    observer.start()

    print(f'[watch] Watching {path} (and all subfolders) for new files...')
    print(f'[watch] Pin will be set on first image, updated on target change')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n[watch] Session ended, removing pin...')
        try:
            send_offline(api_key, api_url)
            print('[watch] Pin removed.')
        except Exception:
            pass
        observer.stop()
    observer.join()
