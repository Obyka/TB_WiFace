import argparse
from scapy.all import *
import json
from json import JSONEncoder
import datetime
from MAC import MAC
from Place import Place
from Probe import Probe
from Auth import User
from API import *
import time

parser = argparse.ArgumentParser(description="Scan for probes request")
parser.add_argument('-i', help="interface wifi en monitor")
args = parser.parse_args()

creds = User("Obyka","pass")
MyAPI = API(creds, "http://92.222.64.114:5555/api/")
mac_dic = dict()

def analyzePacket(packet):
    # Le paquet possede-t-il la couche 802.11
    if packet.haslayer(Dot11) or packet.haslayer(Dot11FCS):
        #print(packet.show())
        # Le paquet est-il un paquet de management et est une probe request
        if packet.type == 0 and packet.subtype == 4:
            print("Probe!")
            address = packet.addr2
            if address not in mac_dic or (datetime.utcnow() - mac_dic[address]) / timedelta(seconds=1) > 60:
                mac_dic[address] = datetime.utcnow()
            else:
                return
            try:
                ret_mac = MyAPI.getMACByAddress(address)
            except APIErrorNotFound:
                try:
                    vendor = MAC.extractVendor(address.upper())
                    vendor = vendor if MyAPI.getVendorByOUI(vendor) else "UNDEF"
                    mac = MAC(address.upper(), MAC.isRandomFunc(address), vendor)
                    ret_mac = MyAPI.postMAC(mac)
                except Exception as e:
                    print(e)
                    return
            except APIError:
                return
            
            probe = Probe(packet.info.decode('utf-8'), 1, ret_mac.address)
            MyAPI.postProbeRequest(probe)
            print("SSID: ", packet.addr2)
            print("ESSID : ", packet.info.decode('utf-8'))

sniff(iface=args.i, prn=analyzePacket)




