from mqtt_client import MQTTClient
from timer import Timer
from timeit import default_timer as timer
import yaml
import json
from devices import display_device, display_input_entity, gamer_mode_entity
from ddc import (
    get_physical_monitors, get_input_source, set_input_source,
    INPUT_SOURCE_DP, INPUT_SOURCE_HDMI,
    set_gamer_mode, get_gamer_mode,
    GAMER_MODE_OFF, GAMER_MODE_FPS, GAMER_MODE_RTS,
    GAMER_MODE_RACING, GAMER_MODE_GAMER1, GAMER_MODE_GAMER2, GAMER_MODE_GAMER3
)

class Service:
    def __init__(self):
        self.dt = 0
        
        try:
            with open("config.yml", "r") as config:
                config = yaml.safe_load(config)
        except Exception as e:
            with open("rename_to_config.yml", "r") as config:
                config = yaml.safe_load(config)
                
        self.mqtt = MQTTClient(config["mqtt"]["username"],
                            config["mqtt"]["password"],
                            config["mqtt"]["host"],
                            config["mqtt"]["port"])
        
        poll_interval = 20 if "interval" not in config else config["interval"]
        
        self.mqtt.delegate = self
        
        self.inputs = {}
        self.gamer_modes = {}
        display_data = config['display']
        
        print(display_data)

        self.inputs = {}
        self.gamer_modes = {}
        
        for display in display_data:
            display_id = display['id']
            self.inputs[display_id] = {
                "select": None,
                "inputs": display['inputs']  # Store the input sources and their codes
            }
            self.gamer_modes[display_id] = { "select": None }
            
            for input_name, input_code in display['inputs'].items():
                self.create_input_select(display_id, input_name, input_code)
            
            self.create_gamer_mode_select(display_id)
            
        self.timer = Timer(poll_interval, self)
        self.update_inputs_states()
        self.update_gamer_modes_states()
        
    def update_inputs_states(self):
        monitors = get_physical_monitors()
        for display_id in self.inputs.keys():
            if display_id < len(monitors):
                monitor_handle = monitors[display_id][0]
                input_code = get_input_source(monitor_handle)
                
                print(f"Input code is {input_code}")
                
                # Map input codes to their corresponding names
                input_map = {
                    INPUT_SOURCE_DP: "DisplayPort",
                    INPUT_SOURCE_HDMI: "HDMI"
                    # Add more mappings as needed
                }
                
                current_input_name = input_map.get(input_code, "Unknown")
                
                # Update the state in Home Assistant
                self.mqtt.client.publish(self.inputs[display_id]["select"]["topic"], current_input_name, retain=True)
                self.inputs[display_id]["select"]["state"] = current_input_name
            
    def update_gamer_modes_states(self):
        monitors = get_physical_monitors()
        for display_id in self.gamer_modes.keys():
            if display_id < len(monitors):
                monitor_handle = monitors[display_id][0]
                current_mode_code = get_gamer_mode(monitor_handle)
                
                # Debug log
                print(f"Checking Gamer Mode for display {display_id}. Current mode code: {current_mode_code}")
                
                # Map mode codes to their corresponding names
                mode_map = {
                    GAMER_MODE_OFF: "OFF",
                    GAMER_MODE_FPS: "FPS",
                    GAMER_MODE_RTS: "RTS",
                    GAMER_MODE_RACING: "Racing",
                    GAMER_MODE_GAMER1: "Gamer 1",
                    GAMER_MODE_GAMER2: "Gamer 2",
                    GAMER_MODE_GAMER3: "Gamer 3"
                }
                
                current_mode_name = mode_map.get(current_mode_code, "OFF")
                
                # Update the state in Home Assistant
                self.mqtt.client.publish(self.gamer_modes[display_id]["select"]["topic"], current_mode_name, retain=True)
                self.gamer_modes[display_id]["select"]["state"] = current_mode_name
            
    def on_message(self, topic, payload):
        """
        Handles MQTT messages for input source select and Gamer Mode select entities.
        """
        print(f"Received message on topic: {topic}, payload: {payload}")  # Debug print

        if payload == 'OFF':
            return  # Do nothing
        
        # Split the topic into parts
        parts = topic.split("/")
        
        # Ensure the topic has the correct structure
        if len(parts) < 4:
            print(f"Invalid topic structure: {topic}")
            return
        
        # Extract display_id and command type
        try:
            # Extract display_id and command_type from the 3rd part of the topic
            # Example: "display_0_gamer_mode" -> display_id = 0, command_type = "gamer_mode"
            display_part = parts[2]  # "display_0_gamer_mode"
            display_parts = display_part.split("_")  # Split into ["display", "0", "gamer", "mode"]
            
            display_id = int(display_parts[1])  # Extract display_id from "0"
            command_type = "_".join(display_parts[2:])  # Combine "gamer" and "mode" to get "gamer_mode"
        except (IndexError, ValueError) as e:
            print(f"Failed to parse display_id or command_type from topic: {topic}. Error: {e}")
            return
        
        print(f"Display ID: {display_id}, Command Type: {command_type}")  # Debug print
        
        if command_type == "input":
            # The payload contains the selected input source (e.g., "HDMI" or "DisplayPort")
            selected_input = payload.decode("utf-8")  # Get the selected input source
            self.activate_input(display_id, selected_input)
        elif command_type == "gamer_mode":
            selected_mode = payload.decode("utf-8")  # Get the selected Gamer Mode
            self.set_gamer_mode(display_id, selected_mode)
        else:
            print(f"Unknown command type: {command_type}")
    
    def activate_input_deactivate_rest(self, display_id, input_name):
        print(f"Display {display_id} name {input_name}")
        
        monitors = get_physical_monitors()
        if display_id < len(monitors):
            monitor_handle = monitors[display_id][0]
            
            # Find the input code for the selected input name
            input_code = None
            for entry in self.inputs[display_id]["select"]["options"]:
                if entry["name"] == input_name:
                    input_code = entry["code"]
                    break
            
            if input_code is not None:
                # Set the input source
                set_input_source(monitor_handle, int(input_code))
                
                # Update the state in Home Assistant
                self.mqtt.client.publish(self.inputs[display_id]["select"]["topic"], input_name, retain=True)
                self.inputs[display_id]["select"]["state"] = input_name
            else:
                print(f"Invalid input name: {input_name}")
    
    def set_gamer_mode(self, display_id, mode_name):
        """
        Sets the Gamer Mode for the specified monitor and updates the state in Home Assistant.
        """
        print(f"Setting Gamer Mode for display {display_id} to {mode_name}")
        
        monitors = get_physical_monitors()
        if display_id < len(monitors):
            monitor_handle = monitors[display_id][0]
            
            # Map mode names to their corresponding codes
            mode_map = {
                "OFF": GAMER_MODE_OFF,
                "FPS": GAMER_MODE_FPS,
                "RTS": GAMER_MODE_RTS,
                "Racing": GAMER_MODE_RACING,
                "Gamer 1": GAMER_MODE_GAMER1,
                "Gamer 2": GAMER_MODE_GAMER2,
                "Gamer 3": GAMER_MODE_GAMER3
            }
            
            if mode_name in mode_map:
                # Set the Gamer Mode
                success = set_gamer_mode(monitor_handle, mode_map[mode_name])
                if success:
                    # Update the state in Home Assistant
                    self.mqtt.client.publish(self.gamer_modes[display_id]["select"]["topic"], mode_name, retain=True)
                    self.gamer_modes[display_id]["select"]["state"] = mode_name
                else:
                    print(f"Failed to set Gamer Mode to {mode_name}")
            else:
                print(f"Invalid Gamer Mode: {mode_name}")
    
    def create_input_select(self, display_id, input_name, input_code):
        """
        Creates a dropdown (select) entity for an input source.
        """
        # Replace wildcards in the topic templates
        topic = display_input_entity["generic_select"].format(display_id=display_id)
        availability_topic = display_input_entity["generic_select_config"]["availability_topic"].format(display_id=display_id)
        state_topic = display_input_entity["generic_select_config"]["state_topic"].format(display_id=display_id)
        command_topic = display_input_entity["generic_select_config"]["command_topic"].format(display_id=display_id)

        config = display_input_entity["generic_select_config"].copy()
        config["unique_id"] = f"display_{display_id}_input"
        config["object_id"] = f"display_{display_id}_input"
        config["name"] = "Input Source"
        config["state_topic"] = state_topic
        config["availability_topic"] = availability_topic
        config["command_topic"] = command_topic

        # Add the display_device dynamically
        device = display_device.copy()
        device["name"] = device["name"].format(display_id=display_id)
        device["identifiers"] = [f"display_{display_id}"]  # Unique identifier for each monitor
        config["device"] = device

        # Publish initial state
        self.mqtt.client.publish(availability_topic, "online", retain=True)
        self.mqtt.client.publish(state_topic, "HDMI", retain=True)  # Default state
        self.mqtt.client.publish(topic, json.dumps(config), retain=True)

        # Subscribe to the command topic
        self.mqtt.client.subscribe(command_topic)

        # Store the select entity for later use
        self.inputs[display_id]["select"] = {
            "topic": state_topic,
            "config": config,
            "state": "HDMI",  # Default state
            "options": []  # Initialize the options list
        }

        # Add the input source options
        for input_name, input_code in self.inputs[display_id]["inputs"].items():
            self.inputs[display_id]["select"]["options"].append({
                "name": input_name,
                "code": input_code
            })

    def create_gamer_mode_select(self, display_id):
        """
        Creates a dropdown (select) entity for Gamer Mode.
        """
        # Replace wildcards in the topic templates
        topic = gamer_mode_entity["generic_select"].format(display_id=display_id)
        availability_topic = gamer_mode_entity["generic_select_config"]["availability_topic"].format(display_id=display_id)
        state_topic = gamer_mode_entity["generic_select_config"]["state_topic"].format(display_id=display_id)
        command_topic = gamer_mode_entity["generic_select_config"]["command_topic"].format(display_id=display_id)

        config = gamer_mode_entity["generic_select_config"].copy()
        config["unique_id"] = f"display_{display_id}_gamer_mode"
        config["object_id"] = f"display_{display_id}_gamer_mode"
        config["name"] = "Gamer Mode"
        config["state_topic"] = state_topic
        config["availability_topic"] = availability_topic
        config["command_topic"] = command_topic

        # Add the display_device dynamically
        device = display_device.copy()
        device["name"] = device["name"].format(display_id=display_id)
        device["identifiers"] = [f"display_{display_id}"]  # Unique identifier for each monitor
        config["device"] = device

        # Publish initial state
        self.mqtt.client.publish(availability_topic, "online", retain=True)
        self.mqtt.client.publish(state_topic, "OFF", retain=True)
        self.mqtt.client.publish(topic, json.dumps(config), retain=True)

        # Subscribe to the command topic
        self.mqtt.client.subscribe(command_topic)

        # Store the select entity for later use
        self.gamer_modes[display_id] = {
            "select": {
                "topic": state_topic,
                "config": config,
                "state": "OFF"
            }
        }

    def activate_input(self, display_id, input_name):
        """
        Activates the specified input source for the monitor.
        """
        print(f"Display {display_id} name {input_name}")
        
        monitors = get_physical_monitors()
        if display_id < len(monitors):
            monitor_handle = monitors[display_id][0]
            
            # Find the input code for the selected input name
            input_code = None
            for entry in self.inputs[display_id]["select"]["options"]:
                if entry["name"] == input_name:
                    input_code = entry["code"]
                    break
            
            if input_code is not None:
                # Set the input source
                set_input_source(monitor_handle, int(input_code))
                
                # Update the state in Home Assistant
                self.mqtt.client.publish(self.inputs[display_id]["select"]["topic"], input_name, retain=True)
                self.inputs[display_id]["select"]["state"] = input_name
            else:
                print(f"Invalid input name: {input_name}")
                
    def step(self, dt):
        """
        Handles the main loop of the service.
        """
        # Step the timer
        self.timer.step(dt)
        
        # Step the MQTT client
        self.mqtt.step(dt)

    def on_timer(self, timer, elapsed):
        """
        Handles periodic tasks when the timer elapses.
        """
        # Update the input source states
        self.update_inputs_states()
        
        # Update the Gamer Mode states
        self.update_gamer_modes_states()
        
        # Reset the timer
        self.timer.reset()
        self.timer.active = True

    def start(self):
        while True:
            t0 = timer()
            self.step(self.dt)
            t1 = timer()
            self.dt = t1 - t0

service = Service()
service.start()