from rox_septentrio import __main__ as main


def test_main() -> None:
    assert main.__version__ is not None
