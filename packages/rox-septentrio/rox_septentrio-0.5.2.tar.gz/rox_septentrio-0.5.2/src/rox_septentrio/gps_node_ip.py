#!/usr/bin/env python3
"""
GPS node. Reads NMEA data from a socket, parses it and publishes to MQTT
Includes robust socket connection handling, complete type hints, and full stack traces on exceptions.

Copyright (c) 2024 ROX Automation - Jev Kuznetsov
"""

import logging
import os
import socket
import time
from typing import Dict, Type

import coloredlogs  # type: ignore
import orjson
import paho.mqtt.client as mqtt
from pynmea2 import ChecksumError
from rox_septentrio import config, nmea, __version__

# Setup logging configuration
LOG_FORMAT: str = "%(asctime)s.%(msecs)03d  %(message)s"
LOGLEVEL: str = os.environ.get("LOGLEVEL", "INFO").upper()
FEEDBACK_PERIOD: int = 5

coloredlogs.install(level=LOGLEVEL, fmt=LOG_FORMAT)

log: logging.Logger = logging.getLogger("gps_node")


def connect_socket(gps_cfg: config.GpsConfig) -> socket.socket:
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((gps_cfg.ip_host, gps_cfg.ip_port))
    log.info(f"Connected to GPS server at {gps_cfg.ip_host}:{gps_cfg.ip_port}")
    return sock


def main() -> None:
    log.info(f"Starting GPS node over IP version {__version__}")
    mqtt_cfg: config.MqttConfig = config.MqttConfig()
    gps_cfg: config.GpsConfig = config.GpsConfig()

    topic_map: Dict[Type[nmea.PositionData | nmea.HeadingData], str] = {
        nmea.PositionData: mqtt_cfg.position_topic,
        nmea.HeadingData: mqtt_cfg.direction_topic,
    }

    # Initialize MQTT client
    log.info(f"Connecting to MQTT broker at {mqtt_cfg.host}:{mqtt_cfg.port}")
    client: mqtt.Client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # type: ignore
    client.connect(mqtt_cfg.host, mqtt_cfg.port, 60)

    # Initialize counters
    successful_messages: int = 0
    failed_messages: int = 0
    last_print_time: float = time.time()

    try:
        log.info(f"Connecting to GPS server at {gps_cfg.ip_host}:{gps_cfg.ip_port}")
        with connect_socket(gps_cfg) as sock:
            sock.settimeout(10)  # Set 10-second timeout for recv
            while True:
                try:
                    data: bytes = sock.recv(1024)
                    if not data:
                        log.warning("No data received. Exiting...")
                        break

                    decoded_data: str = data.decode("utf-8")
                    for line in decoded_data.split("\n"):
                        line = line.strip()
                        if not line:
                            continue

                        log.debug(f"{line=}")
                        try:
                            msg: nmea.PositionData | nmea.HeadingData | None = (
                                nmea.parse(line)
                            )
                            if msg is not None:
                                log.debug(f"{msg=}")
                                json_data: bytes = orjson.dumps(msg.to_dict())  # pylint: disable=no-member
                                topic: str = topic_map[type(msg)]

                                result = client.publish(topic, json_data)
                                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                                    raise RuntimeError("MQTT publish failed")
                                successful_messages += 1
                            else:
                                failed_messages += 1
                        except ChecksumError as e:
                            log.warning(f"Could not parse '{line}': {e}")

                    # Print counters every 5 seconds
                    current_time = time.time()
                    if current_time - last_print_time >= FEEDBACK_PERIOD:
                        log.info(
                            f"Messages   OK:{successful_messages}, NOK: {failed_messages}"
                        )
                        successful_messages = 0
                        failed_messages = 0

                        last_print_time = current_time

                except socket.timeout:
                    log.warning("Socket timeout occurred. Exiting...")
                    raise

    except KeyboardInterrupt:
        log.info("GPS node interrupted by user")
    except Exception as e:
        log.error(f"Crashed with exception: {e}", exc_info=True)
        raise

    finally:
        client.loop_stop()
        client.disconnect()
        log.info(
            f"GPS node stopped. Final counts - Successfully processed messages: {successful_messages}, Failed messages: {failed_messages}"
        )


if __name__ == "__main__":
    main()
