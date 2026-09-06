# winddc-mqtt

Control Windows-connected DDC/CI monitors from Home Assistant through MQTT Discovery.

[Architecture diagram](docs/runtime-architecture.html) · [Operations and troubleshooting](docs/OPERATIONS.md)

## Quick start

Open **PowerShell as Administrator** in the repository:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item config.example.yml config.yml
# Edit config.yml: broker address and monitor VCP values.
.venv\Scripts\python.exe start.py --check
```

`--check` must list the expected monitors before continuing. It only reads monitor identities; it never changes input or gamer mode.

## Start automatically at logon

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-user-task.ps1
```

This creates the `WinddcMqtt` scheduled task. It runs in your **interactive desktop session** using this repository's `.venv\Scripts\pythonw.exe`—not as a Windows Service. That distinction is required because DDC/CI monitor handles are unavailable to Session 0 services.

Start it immediately instead of waiting for the next logon:

```powershell
schtasks /run /tn "WinddcMqtt"
schtasks /query /tn "WinddcMqtt" /fo LIST /v
```

## Manual run

```bat
run_winddc.bat
```

## Home Assistant entities

Each configured display creates two MQTT Discovery `select` entities:

- `select.display_<id>_input`
- `select.display_<id>_gamer_mode`

`config.yml` is intentionally ignored by Git. Keep broker credentials and local monitor VCP mappings there; commit changes to `config.example.yml` only.
