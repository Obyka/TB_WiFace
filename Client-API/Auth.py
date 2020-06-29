from dataclasses import dataclass


@dataclass
class User:
    """Simple dataclass to represent an user
    """
    email: str
    password: str


@dataclass
class Token:
    """Simple dataclass to represent a token
    """
    access: str
    refresh: str
    timestamp: str
