from dataclasses import dataclass


@dataclass
class Probe:
    """Simple class to represent a probe request
    """
    ssid: str
    fk_place: int
    fk_mac: int
