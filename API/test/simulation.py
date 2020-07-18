from dataclasses import dataclass
from typing import List
from datetime import datetime, timedelta, timezone
import random
from uuid import uuid4
import timeline
import re

@dataclass
class MAC:
    address: str

@dataclass
class Picture:
    timestamp: datetime
    def __str__(self):
        return self.timestamp.strftime("%H:%M:%S") + "\nPicture take"
@dataclass
class Probe:
    ssid: str
    fk_mac: MAC
    timestamp: datetime

    def __str__(self):
        return self.timestamp.strftime("%H:%M:%S") + "\nSSID: "+self.ssid+"\nMAC: "+self.fk_mac.address

@dataclass
class Device:
    mac: MAC
    probes: List[Probe]
    def emit_probe_request(self, timestamp):
        probe = Probe("SSID", self.mac, timestamp)
        self.probes.append(probe)
        return probe
    def __str__(self):
        return 'Device: '+ self.mac.address+'\n'.join([str(probe) for probe in self.probes])
    
@dataclass
class Person:
    uuid: str
    device: Device
    pictures: List[Picture]
    staying_duration: int
    arrival: int
    def emit_picture(self, timestamp):
        picture = Picture(timestamp)
        self.pictures.append(picture)
        return picture
    def __str__(self):
        return 'Person: '+ self.uuid+'\n' + str(self.device)+"\n".join([str(picture) for picture in self.pictures])
    

class Simulation:
    probe_probability = 0.8
    picture_probability = 0.1
    simulation_duration = 100
    def __init__(self, people, fk_place, starting_datetime):
        self.people = people
        self.fk_place = fk_place
        self.starting_datetime = starting_datetime
        self.current_datetime = starting_datetime
        self.events = []
    def run_one_time_unit(self):
        for person in self.people:
            if self.current_datetime < self.starting_datetime + timedelta(minutes=person.arrival) or timedelta(minutes=person.staying_duration) < self.current_datetime - self.starting_datetime -timedelta(minutes=person.arrival):
                continue
            random_sample = random.random()
            if random_sample <= Simulation.probe_probability:
                probe = person.device.emit_probe_request(self.current_datetime)
                self.events.append((probe.timestamp.timestamp() - self.starting_datetime.timestamp(), person.uuid, "green"))
            if random_sample <= Simulation.picture_probability:
                picture = person.emit_picture(self.current_datetime)
                self.events.append((picture.timestamp.timestamp() - self.starting_datetime.timestamp(), person.uuid, "blue"))
        self.current_datetime += timedelta(minutes=(1))

    def display_result(self):
        for person in self.people:
            print(str(person.device.mac.address)+" "+str(person.arrival) + " " + str(person.staying_duration) + " " + str(len(person.pictures)) + " " + str(len(person.device.probes)))

    def plot_graph(self):
        colors = {'blue': 'b', 'green': 'g', 'red': 'r'}
        dataset = self.events
        for person in self.people:
            dataset.append((timedelta(minutes=person.arrival-1).total_seconds(), person.uuid, "red"))
            dataset.append((timedelta(minutes=person.arrival+person.staying_duration+1).total_seconds(), person.uuid, "red"))

        plt = timeline.plot_timeline(self.events, colors=colors, savefig="timeline.svg")
            

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
                        in zip(*[iter('{:012X}'.format(intAddress))]*2)])

def generate_people(nb_person):
    current_address = "AA:AA:AA:AA:AA:AA"
    people = []
    for i in range(nb_person):
        current_MAC = MAC(current_address)
        current_address = int_to_mac(mac_to_int(current_address)+1)
        current_device = Device(current_MAC, [])
        arrival_time = random.randint(0, Simulation.simulation_duration)
        duration_time = random.randint(0, Simulation.simulation_duration - arrival_time)
        current_person = Person(str(uuid4()),current_device,[],duration_time,arrival_time)
        people.append(current_person)
    return people


def main():
    people = generate_people(100)
    simulation = Simulation(people, 1, datetime.now(timezone.utc))
    for i in range(Simulation.simulation_duration):
        simulation.run_one_time_unit()
    
    simulation.plot_graph()
    simulation.display_result()

if __name__ == "__main__":
    # execute only if run as a script
    main()