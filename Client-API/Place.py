from dataclasses import dataclass


@dataclass
class Place:
    """Simple dataclass to represent a place
    """
    name: str
    longitude: float
    latitude: float
