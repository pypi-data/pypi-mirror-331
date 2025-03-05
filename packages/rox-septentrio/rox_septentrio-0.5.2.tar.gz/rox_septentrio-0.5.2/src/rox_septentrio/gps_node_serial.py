#!/usr/bin/env python3
"""
GPS node. Reads NMEA data from serial, parses it and publishes to MQTT

Copyright (c) 2024 ROX Automation - Jev Kuznetsov
"""

import os
import logging
import coloredlogs  # type: ignore
import serial  # type: ignore
import paho.mqtt.client as mqtt
from rox_septentrio import config
from rox_septentrio import nmea
import orjson

# Setup logging configuration
LOG_FORMAT = "%(asctime)s.%(msecs)03d  %(message)s"
LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()

coloredlogs.install(level=LOGLEVEL, fmt=LOG_FORMAT)

log = logging.getLogger("gps_node")


def main() -> None:
    log.info("Starting GPS node over SERIAL")
    mqtt_cfg = config.MqttConfig()
    gps_cfg = config.GpsConfig()

    # topic map from type to topic
    topic_map = {
        nmea.PositionData: mqtt_cfg.position_topic,
        nmea.HeadingData: mqtt_cfg.direction_topic,
    }

    # Initialize MQTT client
    # migration guide: https://eclipse.dev/paho/files/paho.mqtt.python/html/migrations.html
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # type: ignore
    log.info(f"Connecting to MQTT broker at {mqtt_cfg.host}:{mqtt_cfg.port}")
    client.connect(mqtt_cfg.host, mqtt_cfg.port, 60)

    # Using context manager to handle serial connection
    log.info(
        f"Connecting to serial port {gps_cfg.serial_port} at {gps_cfg.serial_baud} baud"
    )
    with serial.Serial(gps_cfg.serial_port, gps_cfg.serial_baud, timeout=1.0) as tty:
        tty.reset_input_buffer()  # flush previous messages
        try:
            msg = None
            while True:
                line = tty.readline()
                if not line:
                    print(".", end="", flush=True)
                    continue
                log.debug(f"{line=}")
                try:
                    msg = nmea.parse(line.decode("utf-8").strip())

                except Exception as e:
                    log.warning(f"Could not parse '{line}': {e}")

                if msg is None:
                    continue

                log.debug(f"{msg=}")
                # Publish parsed data
                data = orjson.dumps(msg.to_dict())  # pylint: disable=no-member

                topic = topic_map[type(msg)]

                client.publish(topic, data)

        except KeyboardInterrupt:
            log.info("GPS node interrupted by user")
            client.loop_stop()


if __name__ == "__main__":
    main()
