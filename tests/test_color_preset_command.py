from contextlib import contextmanager

from config import AppConfig, DisplayConfig, MqttConfig
from service import Controller


def test_color_preset_command_writes_color_temperature_vcp(monkeypatch) -> None:
    config = AppConfig(
        mqtt=MqttConfig(host="broker"),
        displays=(DisplayConfig(0, "Desk", {"DisplayPort": 15}, {"Off": 0}, {"Normal": 6}),),
    )
    controller = Controller(config)
    writes = []

    @contextmanager
    def monitors():
        yield [("monitor", "Desk")]

    monkeypatch.setattr("service.physical_monitors", monitors)
    monkeypatch.setattr("service.set_vcp_feature", lambda handle, code, value: writes.append((handle, code, value)) or True)
    monkeypatch.setattr(controller, "poll", lambda: None)

    controller._command("homeassistant/select/display_0_color_preset/command", "Normal")

    assert writes == [("monitor", 0x14, 6)]
