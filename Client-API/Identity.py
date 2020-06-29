from dataclasses import dataclass


class Identity:
    """Simple class to represent an identity
    """

    def __init__(self, firstname, lastname, mail, uuid, id=None):
        self.firstname = firstname
        self.lastname = lastname
        self.mail = mail
        self.uuid = uuid
        if id is not None:
            self.id = id


@dataclass
class Represents:
    """Simple dataclass to represent the link between an identity and a picture
    """
    fk_identity: int
    fk_picture: int
    probability: float
