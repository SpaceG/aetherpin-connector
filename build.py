"""Build AetherPin Connector for Mac, Windows, Linux.
Run: python build.py
Creates standalone app in dist/ folder."""

import PyInstaller.__main__
import platform
import sys

name = 'AetherPin Connector'
entry = 'agent/__main__.py'

args = [
    entry,
    '--name', name,
    '--onefile',
    '--clean',
    '--noconfirm',
]

# Mac: create .app bundle
if platform.system() == 'Darwin':
    args.append('--windowed')

# Hidden imports that PyInstaller misses
args += [
    '--hidden-import', 'astropy.io.fits',
    '--hidden-import', 'watchdog.observers',
    '--hidden-import', 'watchdog.events',
    '--hidden-import', 'requests',
]

print(f'Building {name} for {platform.system()}...')
PyInstaller.__main__.run(args)
print(f'\nDone. Check dist/ folder.')
