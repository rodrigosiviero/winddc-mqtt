from __future__ import annotations

import logging
import time

from config import AppConfig, DisplayConfig
from ddc import GAMER_MODE_CODE, INPUT_SOURCE_CODE, get_vcp_feature, physical_monitors, set_vcp_feature
from discovery import entities
from mqtt_client import MQTTClient


class Controller:
    def __init__(self, config: AppConfig):
        self.config = config
        self.mqtt = MQTTClient(config.mqtt)
        self.mqtt.on_connected = self._connected
        self.mqtt.on_message = self._command

    def start(self) -> None:
        self.mqtt.start()
        try:
            while True:
                self.poll()
                time.sleep(self.config.interval_seconds)
        finally:
            self.mqtt.stop()

    def check(self) -> list[str]:
        with physical_monitors() as monitors:
            return [description for _handle, description in monitors]

    def _connected(self) -> None:
        self.mqtt.publish("winddc-mqtt/availability", "online")
        for display in self.config.displays:
            for topic, payload in entities(display, "winddc_mqtt"):
                self.mqtt.publish(topic, __import__("json").dumps(payload))
                self.mqtt.subscribe(payload["command_topic"])
        self.poll()

    def poll(self) -> None:
        with physical_monitors() as monitors:
            for display in self.config.displays:
                if display.id >= len(monitors):
                    logging.warning("Configured display %s is unavailable", display.id)
                    continue
                handle, _description = monitors[display.id]
                self._publish_state(display, "input", get_vcp_feature(handle, INPUT_SOURCE_CODE), display.inputs)
                self._publish_state(display, "gamer_mode", get_vcp_feature(handle, GAMER_MODE_CODE), display.gamer_modes)

    def _publish_state(self, display: DisplayConfig, kind: str, value: int | None, choices: dict[str, int]) -> None:
        if value is None:
            logging.warning("DDC read failed for display %s %s", display.id, kind)
            return
        name = next((name for name, code in choices.items() if code == value), "Unknown")
        self.mqtt.publish(f"homeassistant/select/display_{display.id}_{kind}/state", name)

    def _command(self, topic: str, payload: str) -> None:
        for display in self.config.displays:
            prefix = f"homeassistant/select/display_{display.id}_"
            if not topic.startswith(prefix):
                continue
            kind = "input" if topic == prefix + "input/command" else "gamer_mode"
            choices = display.inputs if kind == "input" else display.gamer_modes
            value = choices.get(payload)
            if value is None:
                logging.warning("Rejected invalid %s command %r for display %s", kind, payload, display.id)
                return
            with physical_monitors() as monitors:
                if display.id >= len(monitors):
                    logging.warning("Configured display %s is unavailable", display.id)
                    return
                set_vcp_feature(monitors[display.id][0], INPUT_SOURCE_CODE if kind == "input" else GAMER_MODE_CODE, value)
            self.poll()
            return
