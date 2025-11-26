# Ransom-Halt | Sentinel

## Overview
Ransom-Halt is a lightweight Dash-based monitoring and demo "sentinel" application that simulates ransomware detection behavior and shows real-time system metrics (CPU, RAM, top processes). It is intended for testing, demonstration, and learning only — not for production security.

## Key files
- `app.py` — main Dash application and sentinel logic.
- `readme.md` — this file.
- `incident_report.html` — generated incident report (created at runtime).
- `protected_folder` — watched directory (created automatically by `app.py`).
- `quarantine_zone` — folder used by the demo virus lab (create manually).

## Features
- Real-time CPU / RAM display and gauge.
- Top processes table with simple risk labeling.
- File system watcher that flags rapid file changes as a simulated ransomware event.
- Demo "VIRUS LAB" with buttons to drop a dummy `trojan.exe` and to clean the zone.
- Generate a self-contained HTML incident report and open it locally.

## Requirements
- Python 3.9+ (tested on Windows).
- Packages:
  - `dash`
  - `dash-bootstrap-components`
  - `plotly`
  - `psutil`
  - `pandas`
  - `watchdog`

Install with:
```bash
pip install dash dash-bootstrap-components plotly psutil pandas watchdog

- (or use pip install -r requirements.txt if you add one)
