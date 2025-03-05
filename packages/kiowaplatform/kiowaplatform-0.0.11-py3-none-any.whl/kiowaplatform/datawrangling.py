# datawrangling.py

def get_starlink_data_v1(payload, edge_type):
    """
    Extract Starlink data from the payload for an edge device.

    Args:
        payload (dict): The payload containing the Starlink data.
        edge_type (str): The type of edge device.
    
    Returns:
        dict: The extracted Starlink data.
    """

    # Access the data under the 'payload' key
    if 'payload' not in payload:
        return {}

    data = payload['payload']['M']  # This is where the actual Starlink data resides

    def extract_starlink_data(sensor_data):
        # Helper to extract and convert 'N' values
        def get_numeric_value(data, key):
            value = data.get(key, {}).get('N')
            if value is not None:
                try:
                # Try to convert to an integer
                    return int(float(value)) if float(value).is_integer() else float(value)
                except ValueError:
                    return None
            return None


        # Extract location data
        location = sensor_data.get('location', {}).get('M', {}).get('lla', {}).get('M', {})
        alt = get_numeric_value(location, 'alt')
        lon = get_numeric_value(location, 'lon')
        lat = get_numeric_value(location, 'lat')
        location_source = get_numeric_value(sensor_data.get('location', {}).get('M', {}), 'source')

        # Extract status data
        status = sensor_data.get('status', {}).get('M', {})
        software_update_state = get_numeric_value(status, 'software_update_state')
        eth_speed_mbps = get_numeric_value(status, 'eth_speed_mbps')
        downlink_throughput_bps = get_numeric_value(status, 'downlink_throughput_bps')
        uplink_throughput_bps = get_numeric_value(status, 'uplink_throughput_bps')
        pop_ping_latency_ms = get_numeric_value(status, 'pop_ping_latency_ms')

        # Extract initialization duration
        initialization_duration = status.get('initialization_duration_seconds', {}).get('M', {})
        initialization_duration_data = {
            'initial_network_entry': get_numeric_value(initialization_duration, 'initial_network_entry'),
            'stable_connection': get_numeric_value(initialization_duration, 'stable_connection'),
            'attitude_initialization': get_numeric_value(initialization_duration, 'attitude_initialization'),
            'first_cplane': get_numeric_value(initialization_duration, 'first_cplane'),
            'gps_valid': get_numeric_value(initialization_duration, 'gps_valid'),
            'burst_detected': get_numeric_value(initialization_duration, 'burst_detected'),
            'network_schedule': get_numeric_value(initialization_duration, 'network_schedule'),
            'first_pop_ping': get_numeric_value(initialization_duration, 'first_pop_ping'),
            'rf_ready': get_numeric_value(initialization_duration, 'rf_ready'),
            'ekf_converged': get_numeric_value(initialization_duration, 'ekf_converged')
        }

        # Extract alignment stats
        alignment_stats = status.get('alignment_stats', {}).get('M', {})
        boresight_azimuth_deg = get_numeric_value(alignment_stats, 'boresight_azimuth_deg')
        boresight_elevation_deg = get_numeric_value(alignment_stats, 'boresight_elevation_deg')
        tilt_angle_deg = get_numeric_value(alignment_stats, 'tilt_angle_deg')
        desired_boresight_azimuth_deg = get_numeric_value(alignment_stats, 'desired_boresight_azimuth_deg')
        desired_boresight_elevation_deg = get_numeric_value(alignment_stats, 'desired_boresight_elevation_deg')
        attitude_uncertainty_deg = get_numeric_value(alignment_stats, 'attitude_uncertainty_deg')

        # Extract device info
        device_info = status.get('device_info', {}).get('M', {})
        country_code = device_info.get('country_code', {}).get('S')
        device_id = device_info.get('id', {}).get('S')
        software_version = device_info.get('software_version', {}).get('S')
        hardware_version = device_info.get('hardware_version', {}).get('S')
        bootcount = get_numeric_value(device_info, 'bootcount')
        generation_number = get_numeric_value(device_info, 'generation_number')

        # Extract additional fields
        device_state = status.get('device_state', {}).get('M', {})
        uptime_s = get_numeric_value(device_state, 'uptime_s')

        software_update_stats = status.get('software_update_stats', {}).get('M', {})
        software_update_progress = get_numeric_value(software_update_stats, 'software_update_progress')

        obstruction_stats = status.get('obstruction_stats', {}).get('M', {})
        fraction_obstructed = get_numeric_value(obstruction_stats, 'fraction_obstructed')

        config = status.get('config', {}).get('M', {})
        apply_location_request_mode = config.get('apply_location_request_mode', {}).get('BOOL')

        return {
            'location': {
                'altitude': alt,
                'longitude': lon,
                'latitude': lat,
                'source': location_source
            },
            'status': {
                'software_update_state': software_update_state,
                'eth_speed_mbps': eth_speed_mbps,
                'downlink_throughput_bps': downlink_throughput_bps,
                'uplink_throughput_bps': uplink_throughput_bps,
                'pop_ping_latency_ms': pop_ping_latency_ms,
                'initialization_duration': initialization_duration_data
            },
            'alignment_stats': {
                'boresight_azimuth_deg': boresight_azimuth_deg,
                'boresight_elevation_deg': boresight_elevation_deg,
                'tilt_angle_deg': tilt_angle_deg,
                'desired_boresight_azimuth_deg': desired_boresight_azimuth_deg,
                'desired_boresight_elevation_deg': desired_boresight_elevation_deg,
                'attitude_uncertainty_deg': attitude_uncertainty_deg
            },
            'device_info': {
                'country_code': country_code,
                'id': device_id,
                'software_version': software_version,
                'hardware_version': hardware_version,
                'bootcount': bootcount,
                'generation_number': generation_number
            },
            'device_state': {
                'uptime_s': uptime_s
            },
            'software_update_stats': {
                'software_update_progress': software_update_progress
            },
            'obstruction_stats': {
                'fraction_obstructed': fraction_obstructed
            },
            'config': {
                'apply_location_request_mode': apply_location_request_mode
            }
        }

    starlink_data = {}

    # Loop through all sensor entries in the payload
    for sensor_id, sensor_data in data.items():
        starlink_data[sensor_id] = extract_starlink_data(sensor_data.get('M', {}))

    return {
        'edge_type': edge_type,
        **starlink_data  # Directly merge starlink data into the return dictionary
    }


def get_victor_vedirect_data_v1(payload, edge_type):
    """
    Extract Victor VE.Direct data from the payload for an edge device.

    Args:
        payload (dict): The payload containing the VE.Direct data.
        edge_type (str): The type of edge device.

    Returns:
        dict: The extracted VE.Direct data.
    """
    # Access the data under the 'payload' key
    if 'payload' not in payload:
        return {}

    data = payload['payload']['M']  # This is where the actual VE.Direct data resides

    def extract_vedirect_data(sensor_data):
        # Helper to extract and convert 'S' values
        def get_string_value(data, key):
            return data.get(key, {}).get('S')

        def get_int_value(data, key):
            value = get_string_value(data, key)
            return int(value) if value is not None and value.isdigit() else None

        # Extract relevant VE.Direct data fields and handle None cases safely
        battery_voltage_v = get_int_value(sensor_data, 'V')
        battery_voltage_v = battery_voltage_v / 1000 if battery_voltage_v is not None else None
        
        battery_current_a = get_int_value(sensor_data, 'I')
        battery_current_a = battery_current_a / 1000 if battery_current_a is not None else None

        load_current_a = get_int_value(sensor_data, 'IL')
        load_current_a = load_current_a / 1000 if load_current_a is not None else None

        panel_voltage_v = get_int_value(sensor_data, 'VPV')
        panel_voltage_v = panel_voltage_v / 1000 if panel_voltage_v is not None else None

        # Safely calculate load power (LoadPowerW)
        load_power_w = None
        if load_current_a is not None and battery_voltage_v is not None:
            load_power_w = load_current_a * battery_voltage_v
            load_power_w = round(load_power_w, 2)

        vedirect_data = {
            'MPPT': get_int_value(sensor_data, 'MPPT'),
            'OperationalRunningStatus': get_string_value(sensor_data, 'OR'),
            'LoadCurrentA': load_current_a,
            'LoadPowerW': load_power_w,
            'ErrorCode': get_int_value(sensor_data, 'ERR'),
            'SerialNumber': get_string_value(sensor_data, 'SER#'),
            'LoadStatus': get_string_value(sensor_data, 'LOAD'),
            'History21': get_int_value(sensor_data, 'H21'),
            'History20': get_int_value(sensor_data, 'H20'),
            'History23': get_int_value(sensor_data, 'H23'),
            'BatteryVoltageV': battery_voltage_v,
            'BatteryCurrentA': battery_current_a,
            'History22': get_int_value(sensor_data, 'H22'),
            'ProductID': get_string_value(sensor_data, 'PID'),
            'ChargingState': get_int_value(sensor_data, 'CS'),
            'FirmwareVersion': get_int_value(sensor_data, 'FW'),
            'History19': get_int_value(sensor_data, 'H19'),
            'PanelPowerW': get_int_value(sensor_data, 'PPV'),
            'HistorySolarDailyYieldWh': get_int_value(sensor_data, 'HSDS'),
            'PanelVoltageV': panel_voltage_v
        }

        return vedirect_data

    vedirect_data = {}

    # Loop through all sensor entries in the payload
    for sensor_id, sensor_data in data.items():
        vedirect_data[sensor_id] = extract_vedirect_data(sensor_data.get('M', {}))

    return {
        'edge_type': edge_type,
        **vedirect_data  # Directly merge VE.Direct data into the return dictionary
    }



def deviceg1_message_type(payload):
    """
    Garmin IPC Inbound Message Codes and descriptions.
    """
    message_codes = {
        0: {"Name": "Position Report", "Description": "Drops a breadcrumb while tracking."},
        1: {"Name": "Reserved", "Description": "Reserved for later use."},
        2: {"Name": "Locate Response", "Description": "Position for a locate request."},
        3: {"Name": "Free Text Message", "Description": "Message containing a free-text block."},
        4: {"Name": "Declare SOS", "Description": "Declares an emergency state."},
        5: {"Name": "Reserved", "Description": "Reserved for later use."},
        6: {"Name": "Confirm SOS", "Description": "Confirms an unconfirmed SOS."},
        7: {"Name": "Cancel SOS", "Description": "Stops a SOS event."},
        8: {"Name": "Reference Point", "Description": "Shares a non-GPS location."},
        10: {"Name": "Start Track", "Description": "Begins a tracking process on the server."},
        11: {"Name": "Track Interval", "Description": "Indicates changes in tracking interval."},
        12: {"Name": "Stop Track", "Description": "Ends a tracking process on the server."},
        13: {
            "Name": "Unknown Index",
            "Description": (
                "Used when the device receives a message from the server addressed to a synced "
                "contact identifier that is not on the device."
            )
        },
        14: {
            "Name": "Puck Message 1",
            "Description": "Sends the first of three inReach message button events."
        },
        15: {
            "Name": "Puck Message 2",
            "Description": "Sends the second of three inReach message button events."
        },
        16: {
            "Name": "Puck Message 3",
            "Description": "Sends the third of three inReach message button events."
        },
        17: {"Name": "Map Share", "Description": "Sends a message to the shared map."},
        20: {
            "Name": "Mail Check",
            "Description": "Sent to determine if any messages are queued for the device."
        },
        21: {
            "Name": "Am I Alive",
            "Description": (
                "Sent when the device needs to determine if it is active. This message is "
                "automatically replied to by the Garmin server to indicate the current status of "
                "the device."
            )
        },
        24: {
            "Name": "Pre-defined Message",
            "Description": "The index for a text message that is synchronized with the server."
        },
        64: {
            "Name": "Encrypted Binary",
            "Description": "An encrypted binary Earthmate message."
        },
        65: {
            "Name": "Pingback Message",
            "Description": "A pingback response message (initiated through IPCInbound)."
        },
        66: {
            "Name": "Generic Binary",
            "Description": "An uninterpreted binary message."
        },
        67: {
            "Name": "EncryptedPinpoint",
            "Description": "A fully-encrypted inReach message."
        },
        3099: {
            "Name": "Canned Message",
            "Description": "A Quicktext message, potentially edited by the user."
        }
    }

    message_code = int(payload['payload']['M']['event']['M']['messageCode']['N'])
    message_info = message_codes.get(
        message_code, {"Name": "Unknown", "Description": "Unknown message code"}
    )

    return {
        "id": message_code,
        "name": message_info["Name"],
        "description": message_info["Description"]
    }