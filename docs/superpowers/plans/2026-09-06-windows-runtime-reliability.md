# Windows Runtime Reliability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make DDC-to-MQTT reliable on Windows without running in Session 0 or leaking monitor handles.

**Architecture:** Run a user-session Python process launched at logon. Keep configuration/discovery as pure Python, manage every DXVA2 handle with a context manager, and let one MQTT client own reconnect, LWT, discovery, subscriptions, and availability.

**Tech Stack:** Python 3.12, PyYAML, paho-mqtt 2.x, Windows DXVA2, Home Assistant MQTT Discovery.

**Spec:** User goals from session: Windows DDC input/gamer-mode control; HA discovery; reliable automatic user-session startup; no device-changing test without authorization.

## Global Constraints

- Run from `C:\Users\rodri\hermes\MonitorMQTT\winddc-mqtt`.
- Do not use a Windows Service for DDC/CI.
- Do not change monitor input or gamer mode during verification.
- Keep MQTT authentication optional.
- Medium+ changes remain on `fix/windows-runtime-reliability`.

---

### Task 1: Add testable configuration and discovery

**Files:** Create `config.py`, `discovery.py`, `tests/test_config.py`, `tests/test_discovery.py`.

- [ ] Write failing tests for YAML validation and discovery options generated from configured inputs/modes.
- [ ] Implement minimal dataclasses and discovery payload builders.
- [ ] Run `pytest tests/test_config.py tests/test_discovery.py -q`.

### Task 2: Make DXVA2 handle ownership explicit

**Files:** Modify `ddc.py`; create `tests/test_ddc.py`.

- [ ] Write failing test proving every supplied physical monitor handle is closed after a polling operation.
- [ ] Implement a context-managed monitor collection and update read/write helpers to use it.
- [ ] Run `pytest tests/test_ddc.py -q`.

### Task 3: Replace lifecycle and MQTT recovery

**Files:** Replace `mqtt_client.py`, `start.py`; create `service.py`, `tests/test_service.py`.

- [ ] Write failing tests for command dispatch, offline availability, config-driven options, and no-op polling on unavailable monitors.
- [ ] Implement reconnect-safe paho client, LWT, re-subscription, structured logs, and guarded entry point.
- [ ] Run `pytest tests/test_service.py -q`.

### Task 4: Add Windows user-session launch and operating docs

**Files:** Create `scripts/install-user-task.ps1`, modify `run_winddc.bat`, `README.md`, `.gitignore`, `requirements.txt`.

- [ ] Add an idempotent interactive logon-task installer; do not execute it during this change.
- [ ] Document `--check`, user-task installation, logs, and removal of stale service/task.
- [ ] Create a local virtualenv and install dependencies.

### Task 5: Verify and commit

**Files:** all touched files.

- [ ] Run full `pytest -q`, compile, configuration check, and read-only `--check` against MQTT/DDC.
- [ ] Inspect branch diff and review changes.
- [ ] Commit the implementation on the feature branch.
