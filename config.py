from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class MqttConfig:
    host: str
    port: int = 1883
    username: str | None = None
    password: str | None = None


@dataclass(frozen=True)
class DisplayConfig:
    id: int
    name: str
    inputs: dict[str, int]
    gamer_modes: dict[str, int]
    color_presets: dict[str, int]


@dataclass(frozen=True)
class AppConfig:
    mqtt: MqttConfig
    displays: tuple[DisplayConfig, ...]
    interval_seconds: int = 20


def load_config(path: Path) -> AppConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    mqtt_raw = raw.get("mqtt") or {}
    host = str(mqtt_raw.get("host", "")).strip()
    if not host:
        raise ValueError("mqtt.host is required")

    displays = tuple(
        DisplayConfig(
            id=int(item["id"]),
            name=str(item.get("name") or f"Display {item['id']}"),
            inputs={str(name): int(code) for name, code in (item.get("inputs") or {}).items()},
            gamer_modes={_yaml_label(name): int(code) for name, code in (item.get("gamer_modes") or {}).items()},
            color_presets={str(name): int(code) for name, code in (item.get("color_presets") or {}).items()},
        )
        for item in raw.get("display") or ()
    )
    if not displays:
        raise ValueError("at least one display is required")
    ids = [display.id for display in displays]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate display id")
    if any(not display.inputs for display in displays):
        raise ValueError("each display needs at least one input")

    return AppConfig(
        mqtt=MqttConfig(
            host=host,
            port=int(mqtt_raw.get("port", 1883)),
            username=_optional(mqtt_raw.get("username")),
            password=_optional(mqtt_raw.get("password")),
        ),
        displays=displays,
        interval_seconds=int(raw.get("interval", 20)),
    )


def _yaml_label(value: object) -> str:
    if value is False:
        return "Off"
    if value is True:
        return "On"
    return str(value)


def _optional(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None
