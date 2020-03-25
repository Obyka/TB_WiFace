import argparse
from scapy.all import *
import json
from json import JSONEncoder
import requests
import datetime

parser = argparse.ArgumentParser(description="Scan for probes request")
parser.add_argument('-i', help="interface wifi en monitor")
args = parser.parse_args()

#api consts
headers = {'Content-Type': 'application/json'}
api_url_base = 'http://localhost:5000/api/'

def postProbeRequest(probe):
    api_url = '{0}probes'.format(api_url_base)
    probe_json = {'fk_mac':probe.fk_mac, 'fk_place':probe.fk_place, 'ssid':probe.ssid}
    probe_date = DateTimeEncoder().encode(probe_json)
    print(probe_date)
    response = requests.post(api_url, headers=headers, json=probe_json)
    print(response)

def analyzePacket(packet):
    # Le paquet possede-t-il la couche 802.11
    if packet.haslayer(Dot11) or packet.haslayer(Dot11FCS):
        #print(packet.show())
        # Le paquet est-il un paquet de management et est une probe request
        if packet.type == 0 and packet.subtype == 4:
            probe = Probe(packet.info.decode('utf-8'), 1, 1)
            postProbeRequest(probe)
            print("SSID: ", packet.addr2)
            print("ESSID : ", packet.info.decode('utf-8'))


class Probe:
  def __init__(self, ssid, fk_place, fk_mac):
    self.ssid = ssid
    self.fk_place = fk_place
    self.fk_mac = fk_mac

class MAC:
  def __init__(self, address, isRandom, fk_vendor):
    self.address = address
    self.isRandom = isRandom
    self.fk_vendor = fk_vendor

class Place:
  def __init__(self, name, longitude, latitude):
    self.name = name
    self.longitude = longitude
    self.latitude = latitude

# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()

#sniff(iface=args.i, prn=analyzePacket)

probe = Probe("Coucou", 1, "FF:FF:AB:FF:FF:FF")
postProbeRequest(probe)

