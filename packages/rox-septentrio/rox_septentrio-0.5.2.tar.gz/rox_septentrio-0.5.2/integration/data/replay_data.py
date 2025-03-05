#!/usr/bin/env python3
"""
Replay data from logged files

Copyright (c) 2022 Green Robotics - Jev Kuznetsov



"""

import argparse
import asyncio
import logging
import sys
import time
from collections import namedtuple
from pathlib import Path
from typing import List, Optional, Tuple, Union, Any

import click
import coloredlogs
import paho.mqtt.client as mqtt
import serial
import yaml

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
DATE_FORMAT = "%H:%M:%S"

log = logging.getLogger("main")

coloredlogs.install(
    level="INFO",
    fmt=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    milliseconds=True,
)


DEFAULT_CONFIG = """
config:
  dt: 0.1
  duration: 20
  restart: true

sources:
  - source: "sensors.txt"
    mqtt_topic: "/sensors"
    player: "mqtt"
    t_offset: 1697033983.140983
    url: "broker:1883"
  - source: "sensors.txt"
    t_offset: 1697033983.140983
    player: "print"
  # - source: "sensors.txt"
  #   t_offset: 1697033983.140983
  #   player: "serial"
  #   tty: "/tmp/tty_imu_tx"


"""

# Define the named tuple
TimeText = namedtuple("TimeText", ["time", "text"])


def split_line(line: str, idx: int = 17) -> tuple[float, str]:
    """split line into timestamp and text parts."""

    ts = float(line[:idx])  # type: ignore
    txt = (line[idx:]).strip()

    return ts, txt


def split_url(url: str) -> Tuple[str, Optional[int]]:
    """split url into host and port"""
    parts = url.split(":")
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else None
    return (host, port)


def load_data(
    data_file: Union[str, Path], t_offset: Optional[float] = None
) -> List[TimeText]:
    """load data from txt file"""

    data = []

    with open(data_file, "r", encoding="utf-8") as fid:
        lines = fid.readlines()

    if t_offset is None:
        t_offset, _ = split_line(lines[0])

    for line in lines:
        try:
            t, txt = split_line(line)
            data.append(TimeText(t - t_offset, txt))
        except ValueError:
            log.warning(f"Could not parse line {line}")

    return data


def gen_test_data(duration: float = 10, dt: float = 0.1) -> List[TimeText]:
    """test data for replay"""

    data = []

    for i in range(int(duration / dt)):
        data.append(TimeText(i * dt, f"line {i} t={i*dt:.3f}"))

    return data


class Player:
    """replay data from txt log"""

    def __init__(self, name: str = "Player") -> None:
        """Replay data from txt log to destination

        Args:
            data_file (str): log file
            t_offset (float, optional): time offset from the first entry. Defaults to None.
        """

        self._log = logging.getLogger(name)

        # self.data = load_data(data_file, t_offset)
        self.data: List[TimeText] = []

        self._data_index = 0  # current data index
        self._t_start = time.time()  # start time

    def reset(self, t_start: float) -> None:
        """reset to the beginning"""
        self._data_index = 0
        self._t_start = t_start

    def send(self, txt: str) -> None:
        """send line"""
        self._log.debug(f"Sending {txt}")

    async def play(self, duration_s: float) -> None:
        """replay data from start to  duration_s"""

        self._data_index = 0
        msg = self.data[self._data_index]

        # fast forward to t=0
        while msg.time < 0:
            self._data_index += 1
            msg = self.data[self._data_index]

        t_elapsed = 0.0
        self._log.info(f"Starting replay for {duration_s:.3f} s")

        while t_elapsed < duration_s:
            # get message
            msg = self.data[self._data_index]
            t_elapsed = time.time() - self._t_start
            t_target = self._t_start + msg.time
            delay = t_target - time.time()
            self._log.debug(
                f"idx={self._data_index} {t_elapsed=:.3f} {t_target=:.3f}, {delay=:.3f}"
            )
            await asyncio.sleep(delay)

            # send message
            self.send(msg.text)

            # get next message
            self._data_index += 1

            # check if we reached the end
            if self._data_index >= len(self.data):
                self._log.info("Reached end of data")
                break

        self._log.info(f"Finished replay at {t_elapsed=:.3f}")


class SerialPlayer(Player):
    def __init__(self, tty: str):
        super().__init__(self.__class__.__name__)
        self._serial = serial.Serial(tty, 115200)
        self._log.info(f"Class {self.__class__.__name__} is logging to {tty}")

    def send(self, txt: str) -> None:
        """send line to serial"""
        self._serial.write((txt + "\r\n").encode())


class MqttPlayer(Player):
    def __init__(
        self,
        url: str,
        mqtt_topic: str,
    ):
        super().__init__(self.__class__.__name__)

        self._log.info(f"Replaying to {url}")

        self._mqtt_client = mqtt.Client()
        self._mqtt_topic = mqtt_topic

        broker, port = split_url(url)

        self._log.info(f"Connecting to {broker}:{port}")
        assert port is not None
        self._mqtt_client.connect(broker, port)
        self._mqtt_client.loop_start()

    def send(self, txt: str) -> None:
        """Send line to MQTT topic"""
        self._log.debug(f"Sending {txt}")

        self._mqtt_client.publish(self._mqtt_topic, txt)

    def close(self) -> None:
        """Cleanly close the MQTT connection"""
        self._mqtt_client.loop_stop()
        self._mqtt_client.disconnect()

    # You can call this to cleanup the MQTT connection if needed
    def __del__(self) -> None:
        self.close()


def make_parser() -> argparse.ArgumentParser:
    """create cmd line parser"""
    p = argparse.ArgumentParser(description="replay serial data")
    p.add_argument("--config", type=str, help="config file.", default="replay.yaml")
    p.add_argument("--debug", help="debug mode", action="store_true")

    return p


async def replay(cfg: dict) -> None:
    print(cfg)

    duration = cfg["config"]["duration"]

    players: List[Player] = []

    for source in cfg["sources"]:
        log.info(f"loading {source}")

        # load data
        data = load_data(source["source"], source["t_offset"])

        if source["player"] == "mqtt":
            players.append(
                MqttPlayer(
                    source["url"],
                    source["mqtt_topic"],
                )
            )
        elif source["player"] == "print":
            players.append(Player())
        elif source["player"] == "serial":
            players.append(SerialPlayer(source["tty"]))

        players[-1].data = data

    while True:
        log.info("Starting replay")
        t_start = time.time()

        for player in players:
            player.reset(t_start)

        await asyncio.gather(*[player.play(duration) for player in players])

        if not cfg["config"]["restart"]:
            break


async def replay_demo(_: Any) -> None:
    """replay demo data"""

    player = Player("demo")
    player.data = gen_test_data(duration=5)
    await player.play(10)


def main() -> None:
    parser = make_parser()

    args = parser.parse_args()
    print(f"{args=}")

    # set loglevel
    if args.debug:
        print("Running in debug mode.")
        coloredlogs.set_level("DEBUG")
    else:
        coloredlogs.set_level("INFO")

    # check for existing config
    cfg_file = Path(args.config)

    # exit if config is provided but not found
    if (args.config != "replay.yaml") and (not cfg_file.exists()):
        print(f"Config file {args.config} not found.")
        sys.exit(-1)

    # create file if default config does not exist
    if not cfg_file.exists():
        if click.confirm(f"No {cfg_file.name} found. Create it?"):
            with cfg_file.open("w", encoding="utf-8") as fid:
                fid.write(DEFAULT_CONFIG)
        sys.exit(0)

    # load config
    print(f"Loading config from {cfg_file}")
    cfg = yaml.safe_load(cfg_file.open("r", encoding="utf-8"))

    try:
        asyncio.run(replay(cfg))
    except KeyboardInterrupt:
        print("interrupted.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("interrupted.")
