class Picture:
    """Simple class to represent a picture object
    """

    def __init__(self, timestamp, picPath, fk_place, id=None):
        self.timestamp = timestamp
        self.picPath = picPath
        self.fk_place = fk_place
        if id is not None:
            self.id = id
