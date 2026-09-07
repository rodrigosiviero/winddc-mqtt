from config import DisplayConfig
from discovery import entities


def test_power_switch_discovery_uses_standby_for_off() -> None:
    display = DisplayConfig(0, "Desk", {"DisplayPort": 15}, {"Off": 0}, {})

    topic, payload = next(item for item in entities(display, "winddc_mqtt") if item[0] == "homeassistant/switch/display_0_power/config")

    assert topic == "homeassistant/switch/display_0_power/config"
    assert payload["name"] == "Power"
    assert payload["payload_on"] == "ON"
    assert payload["payload_off"] == "OFF"
    assert payload["state_on"] == "ON"
    assert payload["state_off"] == "OFF"
