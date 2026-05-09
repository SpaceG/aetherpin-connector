# AetherPin Connector — Sphere Live Map

Remote-Teleskope automatisch auf der Sternenkarte anzeigen.

## Architektur

```
Telescope PC                    AetherPin Server              Browser
┌──────────────┐    POST       ┌──────────────────┐          ┌──────────┐
│ AetherPin    │──────────────▶│ /api/remote-      │          │ /space/  │
│ Connector    │  alle 10s     │ telescope/live    │◀─────────│ sphere     │
│ (Python)     │               │                  │  GET 10s  │          │
└──────────────┘               └──────────────────┘          └──────────┘
  liest FITS Header              speichert in DB               zeigt Pins
  sendet RA/DEC/Target           120s timeout = offline        live auf Map
```

## User Flow

1. Account erstellen auf aetherpin.com
2. Teleskop registrieren → API Key erhalten
3. AetherPin Connector herunterladen (.exe / CLI)
4. API Key eingeben, Watch-Ordner setzen
5. Connector läuft im Hintergrund → Pins erscheinen auf /space/sphere

---

## Roadmap

### Phase 1 — Server-Seite ⬅ AKTUELL
Status: **In Arbeit**

| # | Aufgabe | Datei(en) | Status |
|---|---------|-----------|--------|
| 1 | DB-Tabellen | `connector/sql/001_tables.sql` | ☑ |
| 2 | POST API (Agent → Server) | `api/remote-telescope/live.php` | ☑ |
| 3 | GET API (Map ← Server) | `api/remote-telescope/live.php` | ☑ |
| 4 | Teleskop-Settings UI | `profile.php` + `api/remote-telescope/manage.php` | ☑ |
| 5 | /space/sphere Seite | `sphere.php` | ☐ |
| 6 | JS Live-Polling + Marker | `assets/js/sphere.js` | ☐ |
| 7 | .htaccess Route | `.htaccess` | ☑ |

### Phase 2 — Connector CLI (Python)
Status: **Geplant**

| # | Aufgabe | Datei(en) | Status |
|---|---------|-----------|--------|
| 1 | FITS Header Reader | `connector/agent/fits_reader.py` | ☐ |
| 2 | Ordner-Watcher | `connector/agent/watcher.py` | ☐ |
| 3 | API Sender | `connector/agent/sender.py` | ☐ |
| 4 | CLI Entry Point | `connector/agent/main.py` | ☐ |
| 5 | Config | `connector/agent/config.ini.example` | ☐ |

### Phase 3 — Connector GUI (.exe)
Status: **Geplant**

| # | Aufgabe | Status |
|---|---------|--------|
| 1 | GUI Fenster (tkinter/PyQt) | ☐ |
| 2 | PyInstaller → .exe | ☐ |
| 3 | py2app → .app (Mac) | ☐ |
| 4 | Download-Seite auf aetherpin.com | ☐ |

### Phase 4 — Erweitert
Status: **Später**

| # | Aufgabe | Status |
|---|---------|--------|
| 1 | NINA Plugin | ☐ |
| 2 | ASIAIR Support | ☐ |
| 3 | System Tray | ☐ |
| 4 | Auto-Update | ☐ |
| 5 | Mehrere Teleskope gleichzeitig | ☐ |

---

## Dateiübersicht (alle Dateien die zu diesem Feature gehören)

```
aetherlog/
├── connector/
│   ├── README.md                      ← diese Datei
│   ├── sql/
│   │   └── 001_tables.sql            ← DB Migration
│   └── agent/                         ← Python Connector (Phase 2+3)
│       ├── main.py
│       ├── fits_reader.py
│       ├── watcher.py
│       ├── sender.py
│       └── config.ini.example
├── api/
│   └── remote-telescope/
│       └── live.php                   ← POST + GET API
├── sphere.php                           ← /space/sphere Seite
├── assets/
│   └── js/
│       └── sphere.js                    ← Live-Polling + Canvas Marker
```

---

## DB Schema

### remote_telescopes
| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | INT AUTO_INCREMENT | PK |
| user_id | INT | FK → users |
| name | VARCHAR(100) | z.B. "Starfront 14" |
| observatory | VARCHAR(100) | z.B. "Sphere", "Backyard" |
| software | VARCHAR(100) | z.B. "NINA", "SharpCap" |
| api_key_hash | VARCHAR(255) | bcrypt Hash des API Keys |
| is_active | TINYINT(1) | 1 = aktiv |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### remote_telescope_live_status
| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | INT AUTO_INCREMENT | PK |
| telescope_id | INT | FK → remote_telescopes |
| target_name | VARCHAR(100) | z.B. "M42" |
| ra | VARCHAR(20) | z.B. "05:35:17" |
| dec | VARCHAR(20) | z.B. "-05:23:28" |
| status | ENUM('live','idle','offline') | |
| last_seen | DATETIME | für 120s Timeout |
| created_at | DATETIME | |
| updated_at | DATETIME | |

---

## API Spec

### POST /api/remote-telescope/live
Agent sendet Teleskop-Status.

**Header:** `Authorization: Bearer <API_KEY>`

**Body:**
```json
{
  "target_name": "M42",
  "ra": "05:35:17",
  "dec": "-05:23:28",
  "status": "live"
}
```

**Response:** `200 OK`
```json
{ "success": true }
```

**Rate Limit:** max 1 Request pro 5 Sekunden pro Teleskop.

### GET /api/remote-telescope/live
Map holt aktive Teleskope.

**Parameter:** `?observatory=sphere` (optional)

**Response:**
```json
[
  {
    "telescope_id": 1,
    "name": "Starfront 14",
    "observatory": "Sphere",
    "software": "NINA",
    "target_name": "M42",
    "ra": "05:35:17",
    "dec": "-05:23:28",
    "status": "live",
    "last_seen": "2026-05-06T22:15:30Z",
    "username": "lucas"
  }
]
```

Nur Einträge mit `last_seen` < 120 Sekunden.
