#!/usr/bin/env python3
"""
Mock GPS server that reads NMEA messages from a file and serves them over a socket.
Simulates a real GPS device for testing purposes.

Copyright (c) 2024 ROX Automation
"""

import argparse
import logging
import socket
import time
from pathlib import Path
from typing import List

import coloredlogs

LOG_FORMAT: str = "%(asctime)s.%(msecs)03d  %(message)s"
DEFAULT_PORT: int = 28000
DEFAULT_HOST: str = "localhost"
DEFAULT_DELAY: float = 1.0  # seconds between messages


DATA_FILE = Path(__file__).parent / "data" / "nmea.txt"
assert DATA_FILE.exists(), f"File not found: {DATA_FILE}"

log: logging.Logger = logging.getLogger("mock_gps")
coloredlogs.install(level="INFO", fmt=LOG_FORMAT)


def split_line(line: str, idx: int = 17) -> tuple[float, str]:
    """split line into timestamp and text parts."""

    ts = float(line[:idx])  # type: ignore
    txt = (line[idx:]).strip()

    return ts, txt


def read_nmea_file(file_path: Path) -> List[str]:
    """Read NMEA messages from file, removing empty lines and whitespace."""
    with open(file_path, "r", encoding="utf8") as f:
        return [split_line(line)[1] for line in f if line.strip()]


def serve_gps_data(host: str, port: int, messages: List[str], delay: float) -> None:
    """Serve GPS data over a socket connection."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(1)
        log.info(f"Mock GPS server listening on {host}:{port}")

        while True:
            try:
                client_socket, addr = server_socket.accept()
                log.info(f"Client connected from {addr}")

                with client_socket:
                    while True:
                        for message in messages:
                            client_socket.send(f"{message}\n".encode())
                            log.debug(f"Sent: {message}")
                            time.sleep(delay)
            except (BrokenPipeError, ConnectionResetError):
                log.warning("Client disconnected")
            except KeyboardInterrupt:
                log.info("Server stopped by user")
                break


def main() -> None:
    parser = argparse.ArgumentParser(description="Mock GPS server for testing")
    parser.add_argument(
        "--file", type=Path, help="File containing NMEA messages", default=DATA_FILE
    )
    parser.add_argument(
        "--host", type=str, default=DEFAULT_HOST, help="Host to bind to"
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help="Port to listen on"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help="Delay between messages in seconds",
    )

    args = parser.parse_args()

    if not args.file.exists():
        log.error(f"File not found: {args.file}")
        return

    messages = read_nmea_file(args.file)
    log.info(f"Loaded {len(messages)} NMEA messages from {args.file}")

    serve_gps_data(args.host, args.port, messages, args.delay)


if __name__ == "__main__":
    main()
