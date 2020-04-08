class Identity:
  def __init__(self, firstname, lastname, mail):
    self.firstname = firstname
    self.lastname = lastname
    self.mail = mail

class Represents:
  def __init__(self, fk_identity, fk_picture, probability):
    self.fk_identity = fk_identity
    self.fk_picture = fk_picture
    self.probability = probability