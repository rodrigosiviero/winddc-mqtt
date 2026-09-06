# Operations

## Runtime model

`winddc-mqtt` is a **scheduled task**, not a Windows Service.

A Windows Service runs in Session 0 (usually as `LocalSystem`). DDC/CI is exposed by DXVA2 physical-monitor handles in the logged-in desktop session; Session 0 cannot reliably enumerate or control them. The old service and boot-triggered interactive task were therefore unsupported.

`WinddcMqtt` uses:

| Setting | Value |
| --- | --- |
| Trigger | At logon for the current user |
| Principal | `InteractiveToken`, `HighestAvailable` |
| Executable | `<repo>\.venv\Scripts\pythonw.exe` |
| Argument | `"<repo>\start.py"` |
| Restart | 3 retries, 1-minute interval |
| Execution limit | Disabled |

The direct `pythonw.exe` action means Task Scheduler uses the local virtual environment without activating it, opening `cmd.exe`, or relying on PATH/profile state.

## Install or reinstall

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-user-task.ps1
```

The script validates that `.venv\Scripts\pythonw.exe` and `start.py` exist before registering the task.

```powershell
# Start now.
schtasks /run /tn "WinddcMqtt"

# Inspect state, executable and arguments.
schtasks /query /tn "WinddcMqtt" /fo LIST /v

# Remove automatic startup.
powershell -ExecutionPolicy Bypass -File .\scripts\install-user-task.ps1 -Remove
```

## Logs and verification

```powershell
# Follow runtime logs.
Get-Content .\winddc.log -Tail 100 -Wait

# Validate Python/configuration without changing monitor settings.
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m compileall -q .
.venv\Scripts\python.exe start.py --check
```

A successful task reports an action equivalent to:

```text
<repo>\.venv\Scripts\pythonw.exe "<repo>\start.py"
```

## Home Assistant and MQTT

Discovery is generated from `config.yml` and publishes retained topics such as:

```text
homeassistant/select/display_0_input/config
homeassistant/select/display_0_input/state
homeassistant/select/display_0_input/command
homeassistant/select/display_0_gamer_mode/config
winddc-mqtt/availability
```

The bridge reconnects to MQTT automatically and uses `winddc-mqtt/availability` for availability.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| Home Assistant entity is `unavailable` | Run `schtasks /query /tn "WinddcMqtt" /fo LIST /v`, then inspect `winddc.log`. |
| `--check` finds no monitor | Run it from the logged-in local desktop session. Verify monitor power and DDC/CI in the monitor OSD. Do not use a Windows Service. |
| `DDC read failed` | Restore monitor DDC/CI availability; the next polling cycle retries. |
| Task exits with `0xC000013A` | Reinstall the task. The direct `pythonw.exe` action replaces the old `cmd.exe`/batch wrapper that received `CTRL_C_EXIT`. |
| Task references an old path | Re-run `scripts\install-user-task.ps1`; it derives all paths from the repository location. |
| `WinddcMqttService` still exists | Remove it: services are unsupported for this bridge. |

## Configuration policy

`config.yml` is local and ignored because it can contain broker credentials and LAN-specific monitor mappings. Start from `config.example.yml`; never commit `config.yml`.
