from pathlib import Path

import pytest

from config import load_config


def test_load_config_uses_configured_inputs_and_gamer_modes(tmp_path: Path):
    path = tmp_path / "config.yml"
    path.write_text(
        """mqtt:
  host: broker
  port: 1883
interval: 30
display:
  - id: 0
    name: Desk
    inputs: {HDMI 1: 17, DisplayPort: 15}
    gamer_modes: {Off: 0, FPS: 11}
""",
        encoding="utf-8",
    )

    config = load_config(path)

    assert config.interval_seconds == 30
    assert config.displays[0].name == "Desk"
    assert config.displays[0].inputs == {"HDMI 1": 17, "DisplayPort": 15}
    assert config.displays[0].gamer_modes == {"Off": 0, "FPS": 11}


def test_load_config_rejects_duplicate_display_ids(tmp_path: Path):
    path = tmp_path / "config.yml"
    path.write_text(
        """mqtt: {host: broker}
display:
  - {id: 0, inputs: {HDMI: 17}, gamer_modes: {Off: 0}}
  - {id: 0, inputs: {HDMI: 17}, gamer_modes: {Off: 0}}
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate display id"):
        load_config(path)
