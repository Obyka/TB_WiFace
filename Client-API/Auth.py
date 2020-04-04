class User:
  def __init__(self, email, password):
    self.email = email
    self.password = password

class Token:
  def __init__(self, access, refresh, timestamp):
      self.access = access
      self.refresh = refresh
      self.timestamp = timestamp
      
