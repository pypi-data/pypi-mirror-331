#!/usr/bin/env python3
"""
global configuration

Copyright (c) 2024 ROX Automation - Jev Kuznetsov
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class MqttConfig(BaseSettings):
    """MQTT related settings"""

    model_config = SettingsConfigDict(env_prefix="mqtt_")

    host: str = "localhost"
    port: int = 1883

    position_topic: str = "/gps/position"
    direction_topic: str = "/gps/direction"


class GpsConfig(BaseSettings):
    """gps config"""

    model_config = SettingsConfigDict(env_prefix="gps_")

    # node type can be 'serial' or 'ip'
    node_type: str = "ip"

    # serial configuration
    serial_port: str = "/dev/gps_nmea"
    serial_baud: int = 115_200

    # ip configuration
    ip_host: str = "localhost"
    ip_port: int = 28000


class PrecisionConfig(BaseSettings):
    """precision settings"""

    model_config = SettingsConfigDict(env_prefix="digits_")

    position: int = 3
    latlon: int = 8
    angle: int = 4
