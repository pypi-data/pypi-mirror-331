from rox_septentrio.converters import GpsConverter


def test_ref() -> None:
    # unset GPS_REF environment variable

    gc = GpsConverter(gps_ref=(50.0, 6.0))
    assert gc.gps_ref == (50.0, 6.0)
