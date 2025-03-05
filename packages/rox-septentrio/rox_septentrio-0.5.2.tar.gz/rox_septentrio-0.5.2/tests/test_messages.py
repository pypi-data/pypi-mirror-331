import rox_septentrio.gps_node_serial as node
import orjson


def test_messages() -> None:
    line = b"$GPGGA,142701.307,5126.86304,N,00605.28449,E,4,20,0.7,23.1169,M,47.3944,M,3.2,0000*48\r\n"

    msg = node.nmea.parse(line.decode("utf-8").strip())

    # show types of message fields
    for field in msg._fields:  # type: ignore
        print(f"{field}: {type(getattr(msg, field))}")

    assert isinstance(msg, node.nmea.PositionData)

    orjson.dumps(msg.to_dict())


def test_empty_message() -> None:
    line = b"$GPGGA,,,,,,0,00,,,M,,M,,*66"

    msg = node.nmea.parse(line.decode("utf-8").strip())
    assert msg is None
