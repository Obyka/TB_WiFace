import requests
from Auth import Token
from datetime import datetime, timedelta
from Identity import Identity
from Picture import Picture
import json

class API:

    def __init__(self, creds):
        self.creds = creds
        self.api_url_base = 'http://192.168.0.17:5000/api/'
        self.__APIToken = None
    
    def set_APIToken(self, token):
        self.__APIToken = token

    def get_APIToken(self):
        if self.__APIToken is None or (datetime.utcnow() - self.__APIToken.timestamp) / timedelta(seconds=1) > 600:
            res = self.getTokens(self.creds)
            loaded_json = json.loads(res)
            self.__APIToken = Token(loaded_json.get('access_token'), loaded_json.get('refresh_token'), datetime.utcnow())
        return self.__APIToken
                

    def getTokens(self,creds):
        headers = {'Content-Type': 'application/json'}
        api_url = '{0}login'.format(self.api_url_base)
        login_json = {'email':creds.email, 'password':creds.password}
        response = requests.post(api_url, headers=headers, json=login_json)
        if response.status_code == 401:
            raise APIErrorBadAuth(response.status_code)
        return response.text

    def getIdentityByUUID(self, uuid):
        headers = {'Content-Type': 'application/json', 'Authorization':'Bearer '+self.get_APIToken().access}
        api_url = '{0}identities/uuid/{1}'.format(self.api_url_base, uuid)
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            if response.status_code != 404:
                raise APIError(response.status_code)
            else:
                raise APIErrorNotFound(response.status_code)
        loaded_json = json.loads(response.text)
        foundIdentity = Identity(loaded_json.get('firstname'), loaded_json.get('lastname'), loaded_json.get('mail'), loaded_json.get('uuid'), loaded_json.get('id'))
        return foundIdentity

    def postIdentity(self, identity):
        headers = {'Content-Type': 'application/json', 'Authorization':'Bearer '+self.get_APIToken().access}
        api_url = '{0}identities'.format(self.api_url_base)
        identity_json = {'firstname':identity.firstname, 'lastname':identity.lastname, 'mail':identity.mail, 'uuid':identity.uuid}
        response = requests.post(api_url, headers=headers, json=identity_json)
        if response.status_code != 201:
            raise APIError(response.status_code)

        return response.text

    def postRepresent(self, represent):
        headers = {'Content-Type': 'application/json', 'Authorization':'Bearer '+self.get_APIToken().access}
        api_url = '{0}represents'.format(self.api_url_base)
        represents_json = {'fk_picture':represent.fk_picture, 'fk_identity':represent.fk_identity, 'probability':represent.probability}
        response = requests.post(api_url, headers=headers, json=represents_json)
        if response.status_code != 201:
            raise APIError(response.status_code)

        return response.text

    def postMAC(self, mac):
        headers = {'Content-Type': 'application/json', 'Authorization':'Bearer '+self.get_APIToken().access}
        api_url = '{0}macs'.format(self.api_url_base)
        mac_json = {'address':mac.address, 'isRandom':mac.isRandom, 'fk_vendor':mac.fk_vendor}
        response = requests.post(api_url, headers=headers, json=mac_json)
        if response.status_code != 201:
            raise APIError(response.status_code)

        return response.text

    def getMACByAddress(self, address):
        headers = {'Content-Type': 'application/json', 'Authorization':'Bearer '+self.get_APIToken().access}
        address = address.upper()
        api_url = '{0}macs/{1}'.format(self.api_url_base, address)
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            if response.status_code != 404:
                raise APIError(response.status_code)
            else:
                raise APIErrorNotFound(response.status_code)

        return response.text

    def postProbeRequest(self, probe):
        headers = {'Content-Type': 'application/json', 'Authorization':'Bearer '+self.get_APIToken().access}
        api_url = '{0}probes'.format(self.api_url_base)
        probe_json = {'fk_mac':probe.fk_mac, 'fk_place':probe.fk_place, 'ssid':probe.ssid}
        response = requests.post(api_url, headers=headers, json=probe_json)
        print(response)

    def postPicture(self, picture):
        headers = {'Content-Type': 'application/json', 'Authorization':'Bearer '+self.get_APIToken().access}
        api_url = '{0}pictures'.format(self.api_url_base)
        picture_json = {'timestamp':picture.timestamp, 'picPath':picture.picPath, "fk_place":picture.fk_place}
        response = requests.post(api_url, headers=headers, json=picture_json)
        
        loaded_json = json.loads(response.text)
        pic = Picture(loaded_json.get('timestamp'),loaded_json.get('picPath'),loaded_json.get('fk_place'),loaded_json.get('id'))
        return pic



# source : https://stackoverflow.com/questions/30970905/python-conditional-exception-messages

class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)

class APIErrorNotFound(APIError):
    pass

class APIErrorBadAuth(APIError):
    pass