# Windows DDC/CI to MQTT

Controls Windows-connected DDC/CI monitors through Home Assistant MQTT Discovery.

## Setup

```bat
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe start.py --check
```

`--check` only enumerates monitors; it does not change input or gamer mode.

## Configuration

`config.yml` defines broker settings and the exact DDC codes offered in Home Assistant. Keep credentials out of Git: use a local untracked config if authentication is later enabled.

## Automatic startup

DDC/CI must run in the interactive user session, not as a Windows Service. Install the logon task after validating `--check`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-user-task.ps1
```

Remove it with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-user-task.ps1 -Remove
```

Logs are written to `winddc.log`. The old `WinddcMqttService` and `\DDC` boot task are obsolete and should stay disabled/removed.
