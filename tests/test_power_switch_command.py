from contextlib import contextmanager

from config import AppConfig, DisplayConfig, MqttConfig
from service import Controller


def test_power_switch_commands_write_standby_and_on(monkeypatch) -> None:
    config = AppConfig(MqttConfig(host="broker"), (DisplayConfig(0, "Desk", {"DisplayPort": 15}, {"Off": 0}, {}),))
    controller = Controller(config)
    writes = []
    delays = []

    @contextmanager
    def monitors():
        yield [("monitor", "Desk")]

    monkeypatch.setattr("service.physical_monitors", monitors)
    monkeypatch.setattr("service.set_vcp_feature", lambda handle, code, value: writes.append((handle, code, value)) or True)
    monkeypatch.setattr("service.time.sleep", lambda seconds: delays.append(seconds))
    monkeypatch.setattr(controller, "poll", lambda: None)

    controller._command("homeassistant/switch/display_0_power/command", "OFF")
    controller._command("homeassistant/switch/display_0_power/command", "ON")

    assert writes == [("monitor", 0xD6, 2), ("monitor", 0xD6, 1)]
    assert delays == [2, 2]


def test_failed_power_write_does_not_publish_a_stale_state(monkeypatch) -> None:
    config = AppConfig(MqttConfig(host="broker"), (DisplayConfig(0, "Desk", {"DisplayPort": 15}, {"Off": 0}, {}),))
    controller = Controller(config)
    polls = []

    @contextmanager
    def monitors():
        yield [("monitor", "Desk")]

    monkeypatch.setattr("service.physical_monitors", monitors)
    monkeypatch.setattr("service.set_vcp_feature", lambda *_args: False)
    monkeypatch.setattr(controller, "poll", lambda: polls.append(True))

    controller._command("homeassistant/switch/display_0_power/command", "OFF")

    assert polls == []
