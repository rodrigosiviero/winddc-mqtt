gamer_mode_entity = {
    "generic_select": "homeassistant/select/display_{display_id}_gamer_mode/config",
    "generic_select_config": {
        "availability_topic": "homeassistant/select/display_{display_id}_gamer_mode/availability",
        "state_topic": "homeassistant/select/display_{display_id}_gamer_mode/state",
        "command_topic": "homeassistant/select/display_{display_id}_gamer_mode/command",
        "options": ["OFF", "FPS", "RTS", "Racing", "Gamer 1", "Gamer 2", "Gamer 3"],
        "payload_available": "online",
        "payload_not_available": "offline",
        "unique_id": "display_{display_id}_gamer_mode",
        "object_id": "display_{display_id}_gamer_mode",
        "name": "Gamer Mode",
        "device": {}
    }
}

display_device = {
    "name": "Display {display_id}",
    "manufacturer": "Aoc",
    "model": "Monitor",
    "identifiers": ["display_{display_id}"],
    "via_device": "ddc_mqtt"
}

display_input_entity = {
    "generic_select": "homeassistant/select/display_{display_id}_input/config",
    "generic_select_config": {
        "availability_topic": "homeassistant/select/display_{display_id}_input/availability",
        "state_topic": "homeassistant/select/display_{display_id}_input/state",
        "command_topic": "homeassistant/select/display_{display_id}_input/command",
        "options": ["HDMI", "DisplayPort"],  # Add all available input sources here
        "payload_available": "online",
        "payload_not_available": "offline",
        "unique_id": "display_{display_id}_input",
        "object_id": "display_{display_id}_input",
        "name": "Input Source",
        "device": display_device
    }
}