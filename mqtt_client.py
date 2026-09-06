from __future__ import annotations

import logging
from typing import Callable

import paho.mqtt.client as mqtt

from config import MqttConfig


class MQTTClient:
    def __init__(self, config: MqttConfig, client_id: str = "winddc-mqtt"):
        self.config = config
        self.on_connected: Callable[[], None] | None = None
        self.on_message: Callable[[str, str], None] | None = None
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        if config.username:
            self.client.username_pw_set(config.username, config.password)
        self.client.will_set("winddc-mqtt/availability", "offline", qos=1, retain=True)
        self.client.on_connect = self._connected
        self.client.on_message = self._message
        self.client.on_disconnect = self._disconnected

    def start(self) -> None:
        self.client.reconnect_delay_set(min_delay=1, max_delay=60)
        self.client.connect_async(self.config.host, self.config.port, 60)
        self.client.loop_start()

    def stop(self) -> None:
        self.client.publish("winddc-mqtt/availability", "offline", qos=1, retain=True)
        self.client.disconnect()
        self.client.loop_stop()

    def publish(self, topic: str, payload: str, retain: bool = True) -> None:
        self.client.publish(topic, payload, qos=1, retain=retain)

    def subscribe(self, topic: str) -> None:
        self.client.subscribe(topic, qos=1)

    def _connected(self, _client, _userdata, _flags, reason_code, _properties) -> None:
        if reason_code.is_failure:
            logging.error("MQTT connection refused: %s", reason_code)
            return
        logging.info("Connected to MQTT broker %s:%s", self.config.host, self.config.port)
        if self.on_connected:
            self.on_connected()

    def _message(self, _client, _userdata, message) -> None:
        if self.on_message:
            self.on_message(message.topic, message.payload.decode("utf-8", errors="replace"))

    def _disconnected(self, _client, _userdata, _flags, reason_code, _properties) -> None:
        logging.warning("MQTT disconnected: %s", reason_code)
