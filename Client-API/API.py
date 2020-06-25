import requests
from Auth import Token
from datetime import datetime, timedelta
from Identity import Identity, Represents
from Picture import Picture
from Probe import Probe
from MAC import MAC
import json


class API:
    """This class implements the client-side interaction with the Wiface API
    
    Raises:
        APIErrorBadAuth: The token or login infos are invalid
        APIError: Generic error
        APIErrorNotFound: Ressource not found
    """
    def __init__(self, creds, api_url):
        """Set basic info to connect to the Wiface API
        
        Arguments:
            creds {[object]} -- [must contain email and password]
            api_url {[string]} -- [the remote or local url to the wiface API]
        """
        self.creds = creds
        self.api_url_base = api_url
        self.session = requests.session()
        # It's the most repeated value, so it's set as default
        self.session.headers = {'Content-Type': 'application/json'}
        self.session.verify = False
        self.getTokens()

    def getTokens(self):
        """API request to get a new token given some creds
        
        Arguments:
            creds {[object]} -- [must contain the fields email and password]
        
        Raises:
            APIErrorBadAuth: Invalid login
        """
        api_url = '{0}login'.format(self.api_url_base)
        login_json = {'email':self.creds.email, 'password':self.creds.password}
        response = self.session.post(api_url, json=login_json)
        if response.status_code == 401:
            raise APIErrorBadAuth(response.status_code)

    def getIdentityByUUID(self, uuid):
        """API request to get an identity based on its uuid
        
        Arguments:
            uuid {[string]} -- [unique identifier for an identity, associated with Amazon Rekognition]
        
        Returns:
            [Identity] -- [The identity labeled with the given uuid]
        """
        api_url = '{0}identities/uuid/{1}'.format(self.api_url_base, uuid)
        response = self.session.get(api_url)
        if response.status_code != 200:
            if response.status_code != 404:
                raise APIError(response.status_code)
            else:
                raise APIErrorNotFound(response.status_code)
        loaded_json = json.loads(response.text)
        foundIdentity = Identity(loaded_json.get('firstname'), loaded_json.get('lastname'), loaded_json.get('mail'), loaded_json.get('uuid'), loaded_json.get('id'))
        return foundIdentity

    def postFile(self, picture):
        """API request to upload a file on the API

        Arguments:
            picture {[file]} -- File to send
        """
        headers = {'Content-Type': None}
        api_url = '{0}upload'.format(self.api_url_base)
        print(picture)
        files = {'file': open(picture, 'rb')}
        #print("FIIIIILE "+str(len(files['file'])))
        response = self.session.post(api_url, files=files, headers=headers)
        print(response.request.headers)
        print(response.text)
        return response.text


    def postIdentity(self, identity):
        """API request to post a new Identity on the WiFace API
        
        Arguments:
            identity {[Identity]} -- [identity to post]
        
        Raises:
            APIError: [request error]
        
        Returns:
            [Identity] -- [Identity created on the server]
        """
        api_url = '{0}identities'.format(self.api_url_base)
        identity_json = {'firstname':identity.firstname, 'lastname':identity.lastname, 'mail':identity.mail, 'uuid':identity.uuid}
        response = self.session.post(api_url, json=identity_json)
        if response.status_code != 201:
            raise APIError(response.status_code)
        loaded_json = json.loads(response.text)
        identity = Identity(loaded_json.get('firstname'), loaded_json.get('lastname'), loaded_json.get('mail'), loaded_json.get('uuid'), loaded_json.get('id'))
        return identity

    def postRepresent(self, represent):
        """API request to post a new Represent object on the WiFace API
        
        Arguments:
            identity {[Represent]} -- [Represent to post]
        
        Raises:
            APIError: [request error]
        
        Returns:
            [Represent] -- [Represent created on the server]
        """
        api_url = '{0}represents'.format(self.api_url_base)
        represents_json = {'fk_picture':represent.fk_picture, 'fk_identity':represent.fk_identity, 'probability':represent.probability}
        response = self.session.post(api_url, json=represents_json)
        if response.status_code != 201:
            raise APIError(response.status_code)
        loaded_json = json.loads(response.text)
        represent = Represents(loaded_json.get('fk_identity'), loaded_json.get('fk_picture'), loaded_json.get('probability'))
        return represent

    def postMAC(self, mac):
        """API request to post a new MAC object on the WiFace API
        
        Arguments:
            mac {[MAC]} -- [MAC to post]
        
        Raises:
            APIError: [request error]
        
        Returns:
            [MAC] -- [MAC created on the server]
        """
        api_url = '{0}macs'.format(self.api_url_base)
        mac_json = {'address':mac.address, 'isRandom':mac.isRandom, 'fk_vendor':mac.fk_vendor}
        response = self.session.post(api_url, json=mac_json)
        if response.status_code != 201:
            raise APIError(response.status_code)
        loaded_json = json.loads(response.text)
        mac = MAC(loaded_json.get('address'),loaded_json.get('isRandom'), loaded_json.get('fk_vendor'))
        return mac

    def getMACByAddress(self, address):
        """API request to get a MAC by its address
        
        Arguments:
            address {[string]} -- [MAC address of the MAC object]
        
        Returns:
            [MAC] -- [MAC created on the server]
        """
        address = address.upper()
        api_url = '{0}macs/{1}'.format(self.api_url_base, address)
        response = self.session.get(api_url)
        if response.status_code != 200:
            if response.status_code != 404:
                raise APIError(response.status_code)
            else:
                raise APIErrorNotFound(response.status_code)
        loaded_json = json.loads(response.text)
        mac = MAC(loaded_json.get('address'),loaded_json.get('isRandom'), loaded_json.get('fk_vendor'))
        return mac

    def postProbeRequest(self, probe):
        """API request to post a new Probe object on the WiFace API
        
        Arguments:
            probe {[Probe]} -- [Probe to post]
        
        Raises:
            APIError: [request error]
        
        Returns:
            [Probe] -- [Probe created on the server]
        """
        api_url = '{0}probes'.format(self.api_url_base)
        probe_json = {'fk_mac':probe.fk_mac, 'fk_place':probe.fk_place, 'ssid':probe.ssid}
        response = self.session.post(api_url, json=probe_json)
        loaded_json = json.loads(response.text)
        probe = Probe(loaded_json.get("ssid"), loaded_json.get("fk_place"), loaded_json.get("fk_mac"))
        return probe

    def postPicture(self, picture):
        """API request to post a new Picture object on the Wiface API
        
        Arguments:
            picture {[Picture]} -- [Picture to post]
        
        Returns:
            [Picture] -- [Picture created on the server]
        """
        api_url = '{0}pictures'.format(self.api_url_base)
        picture_json = {'timestamp':picture.timestamp, 'picPath':picture.picPath, "fk_place":picture.fk_place}
        response = self.session.post(api_url, json=picture_json)
        
        loaded_json = json.loads(response.text)
        pic = Picture(loaded_json.get('timestamp'),loaded_json.get('picPath'),loaded_json.get('fk_place'),loaded_json.get('id'))
        return pic

    def getVendorByOUI(self, OUI):
        """API request to get a vendor from its OUI

        Arguments:
            OUI {[String]} -- [Prefix for the vendor]

        Returns:
            [Vendor] -- [vendor details]
        """
        api_url = '{0}vendors/{1}'.format(self.api_url_base, OUI)
        response = self.session.get(api_url)
        return response.status_code == 200



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