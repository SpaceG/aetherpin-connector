"""Build AetherPin Connector for Mac, Windows, Linux.
Run: python build.py
Creates standalone app in dist/ folder."""

import PyInstaller.__main__
import platform
import sys

name = 'AetherPin Connector'
entry = 'run.py'

import platform as _p
# Mac uses --onedir for instant launch (--onefile extracts to /tmp on every
# start, takes 10-30s on Intel Macs with numpy+astropy bundled). On Win/Linux
# we keep --onefile so users get a single-file download.
_pack_mode = '--onedir' if _p.system() == 'Darwin' else '--onefile'

args = [
    entry,
    '--name', name,
    _pack_mode,
    '--clean',
    '--noconfirm',
]

# Mac: create .app bundle. Arch follows the host runner. The CI uses
# macos-13 (Intel) so the resulting binary is x86_64 and runs on both
# Intel natively and Apple Silicon via Rosetta 2. Universal2 was tried
# but watchdog ships only single-arch wheels → IncompatibleBinaryArchError.
if platform.system() == 'Darwin':
    args.append('--windowed')
    args += ['--icon', 'icon.icns']

# Hidden imports that PyInstaller misses
args += [
    '--hidden-import', 'watchdog.observers',
    '--hidden-import', 'watchdog.events',
    '--hidden-import', 'requests',
]

print(f'Building {name} for {platform.system()}...')
PyInstaller.__main__.run(args)
print(f'\nDone. Check dist/ folder.')
