from __future__ import annotations

from config import DisplayConfig


def entities(display: DisplayConfig, node_id: str) -> list[tuple[str, dict]]:
    base = f"homeassistant/select/display_{display.id}"
    device = {
        "identifiers": [f"{node_id}_display_{display.id}"],
        "name": display.name,
        "manufacturer": "AOC",
        "model": "DDC/CI monitor",
    }
    result = [
        _entity(base + "_input", "Input Source", list(display.inputs), device),
        _entity(base + "_gamer_mode", "Gamer Mode", list(display.gamer_modes), device),
    ]
    if display.color_presets:
        result.append(_entity(base + "_color_preset", "Color Preset", list(display.color_presets), device))
    return result


def _entity(base: str, name: str, options: list[str], device: dict) -> tuple[str, dict]:
    return base + "/config", {
        "name": name,
        "unique_id": base.replace("homeassistant/select/", ""),
        "object_id": base.rsplit("/", 1)[-1],
        "command_topic": base + "/command",
        "state_topic": base + "/state",
        "availability_topic": "winddc-mqtt/availability",
        "payload_available": "online",
        "payload_not_available": "offline",
        "options": options,
        "device": device,
    }
