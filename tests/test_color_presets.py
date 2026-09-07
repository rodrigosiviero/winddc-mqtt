from pathlib import Path

from config import DisplayConfig, load_config
from discovery import entities


def test_color_presets_are_loaded_and_published_as_a_select(tmp_path: Path):
    path = tmp_path / "config.yml"
    path.write_text(
        """mqtt: {host: broker}
display:
  - id: 0
    inputs: {DisplayPort: 15}
    gamer_modes: {Off: 0}
    color_presets: {sRGB: 1, Warm: 5, Normal: 6, Cool: 8, User: 11}
""",
        encoding="utf-8",
    )

    display = load_config(path).displays[0]
    topic, payload = next(item for item in entities(display, "winddc_mqtt") if item[0].endswith("_color_preset/config"))

    assert display.color_presets == {"sRGB": 1, "Warm": 5, "Normal": 6, "Cool": 8, "User": 11}
    assert topic == "homeassistant/select/display_0_color_preset/config"
    assert payload["name"] == "Color Preset"
    assert payload["options"] == ["sRGB", "Warm", "Normal", "Cool", "User"]


def test_color_preset_entity_is_omitted_when_not_configured() -> None:
    display = DisplayConfig(0, "Desk", {"DisplayPort": 15}, {"Off": 0}, {})

    topics = [topic for topic, _payload in entities(display, "winddc_mqtt")]

    assert "homeassistant/select/display_0_color_preset/config" not in topics
