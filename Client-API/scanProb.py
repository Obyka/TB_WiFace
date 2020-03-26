import argparse
from scapy.all import *
import json
from json import JSONEncoder
import requests
import datetime
from MAC import MAC
from Place import Place
from Probe import Probe
from APIException import *


parser = argparse.ArgumentParser(description="Scan for probes request")
parser.add_argument('-i', help="interface wifi en monitor")
args = parser.parse_args()

#api consts
headers = {'Content-Type': 'application/json'}
api_url_base = 'http://localhost:5000/api/'

def postMAC(mac):
    api_url = '{0}macs'.format(api_url_base)
    mac_json = {'address':mac.address, 'isRandom':mac.isRandom, 'fk_vendor':mac.fk_vendor}
    response = requests.post(api_url, headers=headers, json=mac_json)
    if response.status_code != 201:
        raise APIError(response.status_code)

    return response.text

def getMACByAddress(address):
    api_url = '{0}macs/{1}'.format(api_url_base, address)
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        if response.status_code != 404:
            raise APIError(response.status_code)
        else:
            raise APIErrorNotFound(response.status_code)

    return response.text

def postProbeRequest(probe):
    api_url = '{0}probes'.format(api_url_base)
    probe_json = {'fk_mac':probe.fk_mac, 'fk_place':probe.fk_place, 'ssid':probe.ssid}
    response = requests.post(api_url, headers=headers, json=probe_json)
    print(response)

def analyzePacket(packet):
    # Le paquet possede-t-il la couche 802.11
    if packet.haslayer(Dot11) or packet.haslayer(Dot11FCS):
        #print(packet.show())
        # Le paquet est-il un paquet de management et est une probe request
        if packet.type == 0 and packet.subtype == 4:
            try:
                address = packet.info.decode('utf-8')
                mac = getMACByAddress(address)
            except APIErrorNotFound:
                try:
                    mac = MAC(address, MAC.isLocallyAssigned(address), MAC.extractVendor(address))
                    mac = postMAC(mac)
                except:
                    return
            except APIError:
                return
            probe = Probe(mac, 1, 1)
            postProbeRequest(probe)
            print("SSID: ", packet.addr2)
            print("ESSID : ", packet.info.decode('utf-8'))





#sniff(iface=args.i, prn=analyzePacket)

probe = Probe("Coucou", 1, "FF:FF:AB:FF:FF:FF")
mac = MAC("FF:FF:AB:FF:FF:FJ", True, "F8-4D-33")
mac2 = MAC("FF:FF:AB:FF:FF:FA", True, "F8-4D-33")
print(postMAC(mac))



