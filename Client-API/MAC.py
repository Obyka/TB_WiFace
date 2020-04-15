import re

class MAC:
    """Simple class to represent MAC object a few utils functions
    """
    def __init__(self, address, isRandom, fk_vendor):
        self.address = address.upper()
        self.isRandom = isRandom
        self.fk_vendor = fk_vendor
    
    @staticmethod
    def mac_to_int(address):
        """Convert a string mac address to its hex representation
        
        Arguments:
            address {[string]} -- [address to convert]
        
        Raises:
            ValueError: [the address is invalid]
        
        Returns:
            [int] -- [int value for the address]
        """
        res = re.match('^((?:(?:[0-9a-f]{2}):){5}[0-9a-f]{2})$', address.lower())
        if res is None:
            raise ValueError('invalid mac address')
        return int(res.group(0).replace(':', ''), 16)

    @staticmethod
    def int_to_mac(intAddress):
        """Convert an int value to mac address string format
        
        Arguments:
            intAddress {[int]} -- [int address to convert]
        
        Raises:
            ValueError: [invalid int value]
        
        Returns:
            [string] -- [mac address]
        """
        if type(intAddress) != int:
            raise ValueError('invalid integer')
        return ':'.join(['{}{}'.format(a, b)
                        for a, b
                        in zip(*[iter('{:012x}'.format(intAddress))]*2)])

    @staticmethod
    def isLocallyAssigned(address):
        """Check the locally assigned bit. if it is set, we assume the address is random
        
        Arguments:
            address {[string]} -- [mac address to check]
        
        Returns:
            [bool] -- [is the given address random]
        """
        intAddress = MAC.mac_to_int(address)
        # set the 41th bit to one and the others to zero
        mask = 0x20000000000
        return bool(((intAddress & mask) >> 41) | 0)

    @staticmethod
    def extractVendor(address):
        """Exract the vendor's OUI
        
        Arguments:
            address {[string]} -- [mac address to check]
        
        Returns:
            [string] -- [vendor's OUI]
        """
        return address[:8]