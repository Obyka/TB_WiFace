import argparse
from scapy.all import *
from mac_vendor_lookup import MacLookup

parser = argparse.ArgumentParser(description="Scan for probes request")
parser.add_argument('-i', help="interface wifi en monitor")
args = parser.parse_args()
mac = MacLookup()

def analyzePacket(packet):
    # Le paquet possede-t-il la couche 802.11
    if packet.haslayer(Dot11) or packet.haslayer(Dot11FCS):
        #print(packet.show())
        # Le paquet est-il un paquet de management et est une probe request
        if packet.type == 0 and packet.subtype == 4:
            print("Client MAC adress: ", packet.addr2)
            try:
                print("Supposed Vendor : ", mac.lookup(packet.addr2))
            except:
                print("Vendor error")
            print("SSID: ", packet.addr2)
            print("ESSID : ", packet.info.decode('utf-8'))


sniff(iface=args.i, prn=analyzePacket)
