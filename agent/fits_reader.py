import struct
import xml.etree.ElementTree as ET
from astropy.io import fits
from pathlib import Path


FITS_EXT = ('.fits', '.fit', '.fts')
XISF_EXT = ('.xisf',)
SER_EXT = ('.ser',)
SUPPORTED_EXT = FITS_EXT + XISF_EXT + SER_EXT


# Known solar system objects with approximate J2000 coords.
# For planets these shift over months, but close enough to place a pin.
# The map only needs to show roughly WHERE someone is pointing.
KNOWN_OBJECTS = {
    'sun':      {'ra': '06:00:00', 'dec': '+23:00:00'},
    'moon':     {'ra': '12:00:00', 'dec': '+05:00:00'},
    'mercury':  {'ra': '07:00:00', 'dec': '+20:00:00'},
    'venus':    {'ra': '05:00:00', 'dec': '+18:00:00'},
    'mars':     {'ra': '08:30:00', 'dec': '+20:00:00'},
    'jupiter':  {'ra': '05:45:00', 'dec': '+23:10:00'},
    'saturn':   {'ra': '23:30:00', 'dec': '-05:00:00'},
    'uranus':   {'ra': '03:20:00', 'dec': '+18:00:00'},
    'neptune':  {'ra': '23:55:00', 'dec': '-02:00:00'},
}


def is_supported_file(path: str) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_EXT


# legacy alias
is_fits_file = is_supported_file


def read_header(path: str) -> dict:
    suffix = Path(path).suffix.lower()
    if suffix in FITS_EXT:
        return _read_fits(path)
    if suffix in XISF_EXT:
        return _read_xisf(path)
    if suffix in SER_EXT:
        return _read_ser(path)
    return {'target_name': '', 'ra': '', 'dec': ''}


# legacy alias
read_fits_header = read_header


def _read_fits(path: str) -> dict:
    hdr = fits.getheader(path)
    return {
        'target_name': (hdr.get('OBJECT') or '').strip(),
        'ra': (hdr.get('RA') or hdr.get('OBJCTRA') or '').strip(),
        'dec': (hdr.get('DEC') or hdr.get('OBJCTDEC') or '').strip(),
    }


def _read_ser(path: str) -> dict:
    """Read SER 178-byte header. SER has NO RA/DEC fields,
    so we extract the target name from the filename and
    look up coordinates from known objects."""
    telescope = ''
    observer = ''

    try:
        with open(path, 'rb') as f:
            sig = f.read(14)
            if not sig.startswith(b'LUCAM-RECORDER'):
                return {'target_name': '', 'ra': '', 'dec': ''}
            f.seek(42)
            observer = f.read(40).split(b'\x00')[0].decode('ascii', errors='ignore').strip()
            instrument = f.read(40).split(b'\x00')[0].decode('ascii', errors='ignore').strip()
            telescope = f.read(40).split(b'\x00')[0].decode('ascii', errors='ignore').strip()
    except Exception:
        pass

    # SER has no OBJECT/RA/DEC — parse target from filename
    target = _target_from_filename(path)

    ra = ''
    dec = ''
    if target:
        coords = KNOWN_OBJECTS.get(target.lower())
        if coords:
            ra = coords['ra']
            dec = coords['dec']

    return {'target_name': target or telescope or 'Unknown', 'ra': ra, 'dec': dec}


def _target_from_filename(path: str) -> str:
    """Try to extract target name from filename.
    Common patterns from capture software:
      FireCapture: 2026-05-09-1830_3-Sun_Halpha.ser
      SharpCap:    Jupiter_2026-05-09T18-30-00.ser
      ASICap:      Sun_120000.ser
    """
    stem = Path(path).stem  # filename without extension

    # Check if any known object name appears in the filename
    stem_lower = stem.lower()
    for name in KNOWN_OBJECTS:
        if name in stem_lower:
            return name.capitalize()

    # Try splitting by common separators and find a non-date/non-number part
    parts = stem.replace('-', '_').replace(' ', '_').split('_')
    for part in parts:
        cleaned = part.strip()
        if cleaned and not cleaned.isdigit() and len(cleaned) > 1:
            # Skip date-like parts (2026, 0509, etc.)
            if cleaned.isdigit():
                continue
            # Skip time-like parts
            if len(cleaned) <= 2:
                continue
            # Skip common prefixes from capture software
            if cleaned.lower() in ('capture', 'cap', 'img', 'frame', 'seq', 'halpha', 'ha', 'sii', 'oiii', 'lum', 'rgb'):
                continue
            return cleaned

    return ''


def _read_xisf(path: str) -> dict:
    """Read XISF XML header block for RA/DEC/Object.
    XISF stores properties as XML before the pixel data."""
    target = ''
    ra = ''
    dec = ''

    with open(path, 'rb') as f:
        sig = f.read(8)
        if sig != b'XISF0100':
            return {'target_name': '', 'ra': '', 'dec': ''}

        f.seek(8)
        xml_len = struct.unpack('<I', f.read(4))[0]
        f.seek(16)
        xml_data = f.read(xml_len)

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        return {'target_name': '', 'ra': '', 'dec': ''}

    # Search FITSKeyword elements
    for kw in root.iter('{http://www.pixinsight.com/xisf}FITSKeyword'):
        name = kw.get('name', '')
        value = (kw.get('value') or '').strip().strip("'").strip()
        if name == 'OBJECT' and not target:
            target = value
        elif name in ('RA', 'OBJCTRA') and not ra:
            ra = value
        elif name in ('DEC', 'OBJCTDEC') and not dec:
            dec = value

    # Also check XISF Property elements
    for prop in root.iter('{http://www.pixinsight.com/xisf}Property'):
        pid = prop.get('id', '')
        val = (prop.get('value') or prop.text or '').strip()
        if pid == 'Observation:Object:Name' and not target:
            target = val
        elif pid == 'Observation:Center:RA' and not ra:
            ra = val
        elif pid == 'Observation:Center:Dec' and not dec:
            dec = val

    return {'target_name': target, 'ra': ra, 'dec': dec}
