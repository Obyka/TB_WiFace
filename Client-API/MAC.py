import re

class MAC:
    def __init__(self, address, isRandom, fk_vendor):
        self.address = address
        self.isRandom = isRandom
        self.fk_vendor = fk_vendor
    
    @staticmethod
    def mac_to_int(address):
        res = re.match('^((?:(?:[0-9a-f]{2}):){5}[0-9a-f]{2})$', address.lower())
        if res is None:
            raise ValueError('invalid mac address')
        return int(res.group(0).replace(':', ''), 16)

    @staticmethod
    def int_to_mac(intAddress):
        if type(intAddress) != int:
            raise ValueError('invalid integer')
        return ':'.join(['{}{}'.format(a, b)
                        for a, b
                        in zip(*[iter('{:012x}'.format(intAddress))]*2)])

    @staticmethod
    def isLocallyAssigned(address):
        intAddress = MAC.mac_to_int(address)
        # set the 41th bit to one and the others to zero
        mask = 0x20000000000
        return bool(((intAddress & mask) >> 41) | 0)

    @staticmethod
    def extractVendor(address):
        return address[:8]