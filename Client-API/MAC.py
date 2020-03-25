import re

class MAC:
    def __init__(self, address, isRandom, fk_vendor):
        self.address = address
        self.isRandom = isRandom
        self.fk_vendor = fk_vendor
    
    def mac_to_int(self):
        res = re.match('^((?:(?:[0-9a-f]{2}):){5}[0-9a-f]{2})$', self.address.lower())
        if res is None:
            raise ValueError('invalid mac address')
        return int(res.group(0).replace(':', ''), 16)

    def int_to_mac(self, intAddress):
        if type(intAddress) != int:
            raise ValueError('invalid integer')
        return ':'.join(['{}{}'.format(a, b)
                        for a, b
                        in zip(*[iter('{:012x}'.format(intAddress))]*2)])

    def isLocallyAssigned(self):
        intAddress = self.mac_to_int()
        # set the 41th bit to one and the others to zero
        mask = 0x20000000000
        return bool(((intAddress & mask) >> 41) | 0)