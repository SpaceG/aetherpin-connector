# Windows Build — Schritt für Schritt

Wenn du an einem Windows-PC sitzt:

1. **Python installieren**
   https://www.python.org/downloads/
   Wichtig: Beim Installer **"Add Python to PATH"** anhaken.

2. **Diesen `_connector` Ordner auf den Windows-PC kopieren**
   USB-Stick, Dropbox, Git — egal wie.

3. **Eingabeaufforderung (CMD) öffnen**
   Windows-Taste → `cmd` tippen → Enter.

4. **In den Ordner wechseln**
   ```
   cd C:\Pfad\zum\_connector
   ```

5. **Dependencies installieren**
   ```
   pip install astropy watchdog requests pyinstaller
   ```

6. **Build starten**
   ```
   python build.py
   ```

7. **Fertig**
   Im Ordner `dist\` liegt **AetherPin Connector.exe**.
   Doppelklick → läuft.

## Für den End-User

Der User lädt nur die `.exe` runter. Doppelklick → Key eingeben → Ordner wählen → fertig. Keine Python-Installation, kein Setup.
