# source : https://stackoverflow.com/questions/30970905/python-conditional-exception-messages

class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)

class APIErrorNotFound(APIError):
    pass