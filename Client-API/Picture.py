class Picture:
  def __init__(self, timestamp, picPath, fk_place, id=None):
    self.timestamp = timestamp
    self.picPath = picPath
    self.fk_place = fk_place
    if id is not None:
      self.id = id

class Represents:
  def __init__(self, fk_identity, fk_picture, probability):
    self.fk_identity = fk_identity
    self.fk_picture = fk_picture
    self.probability = probability