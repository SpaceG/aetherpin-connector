"""Build AetherPin Connector for Mac, Windows, Linux.
Run: python build.py
Creates standalone app in dist/ folder."""

import PyInstaller.__main__
import platform
import sys

name = 'AetherPin Connector'
entry = 'run.py'

args = [
    entry,
    '--name', name,
    '--onefile',
    '--clean',
    '--noconfirm',
]

# Mac: create .app bundle as a universal2 binary (arm64 + x86_64).
# Without --target-arch, a build on macos-latest (arm64) produces an
# arm64-only .app that crashes on Intel Macs with "Bad CPU type".
if platform.system() == 'Darwin':
    args.append('--windowed')
    args += ['--target-arch', 'universal2']

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
