"""main entry point for septentrio_gps."""

from rox_septentrio import __version__
from rox_septentrio import config

cfg = config.GpsConfig()
if cfg.node_type == "ip":
    print("Using IP node")
    from rox_septentrio.gps_node_ip import main as node_main
elif cfg.node_type == "serial":
    print("Using SERIAL node")
    from rox_septentrio.gps_node_serial import main as node_main
else:
    raise ValueError(f"Unknown node type: {cfg.node_type}")


def main() -> None:
    """importable entrypoint"""
    print(f"Septentro gps version: {__version__}")
    node_main()


if __name__ == "__main__":
    main()
