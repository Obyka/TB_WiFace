from dataclasses import dataclass
from typing import List
from datetime import datetime, timedelta, timezone
import random
from uuid import uuid4
from test import timeline
import re
import numpy as np

from config import app, db
from models import (Identities, MacAddress, Pictures, Places,
                    Probes, Represents, User, Vendors)
import mariage

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
class Visit:
    arrival: int
    staying_duration: int

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
    visits: List[Visit]
    def emit_picture(self, timestamp):
        picture = Picture(timestamp)
        self.pictures.append(picture)
        return picture
    def __str__(self):
        return 'Person: '+ self.uuid+'\n' + str(self.device)+"\n".join([str(picture) for picture in self.pictures])
    

class Simulation:
    probe_probability = 0.6
    picture_probability = 0.05
    def __init__(self, people, fk_place, starting_datetime, simulation_duration):
        self.people = people
        self.fk_place = fk_place
        self.starting_datetime = starting_datetime
        self.current_datetime = starting_datetime
        self.simulation_duration = simulation_duration
        self.events = []
    
    def run_one_time_unit(self):
        for person in self.people:
            for visit in person.visits:
                if self.current_datetime < self.starting_datetime + timedelta(minutes=visit.arrival) or timedelta(minutes=visit.staying_duration) < self.current_datetime - self.starting_datetime -timedelta(minutes=visit.arrival):
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

    def plot_graph(self, wrong_uuid):
        colors = {'blue': 'b', 'green': 'g', 'red': 'r'}
        dataset = self.events
        for person in self.people:
            for visit in person.visits:
                dataset.append((timedelta(minutes=visit.arrival-1).total_seconds(), person.uuid, "red"))
                dataset.append((timedelta(minutes=visit.arrival+visit.staying_duration+1).total_seconds(), person.uuid, "red"))
        #title = "Timeline plot - success : " + str(rate[0]) + " failure : " + str(rate[1])
        plt = timeline.plot_timeline(self.events, len(self.people),self.simulation_duration ,colors=colors, savefig="timeline.svg", wrong_uuid=wrong_uuid)

    def export_to_db(self):
        count_person = 1
        count_picture = 1
        IDENTITY = []
        MACS = []
        PROBES = []
        PICTURES = []
        REPRESENTS = []

        dict_real_couple = {}
        for person in self.people:
            if len(person.pictures) > 0:
                dict_real_couple[count_person] = person.device.mac.address
                IDENTITY.append(Identities(id=count_person, firstname=str(count_person) + person.device.mac.address,lastname=None, mail=str(count_person) + person.device.mac.address, uuid=person.uuid, PP2I=True))
            MACS.append(MacAddress(address=person.device.mac.address, isRandom=False, fk_vendor="UNDEF", PP2I=True))
            for taken_picture in person.pictures:
                PICTURES.append(Pictures(id=count_picture, picPath="default_avatar.png",timestamp=taken_picture.timestamp, fk_place=1))
                REPRESENTS.append(Represents(probability=100,fk_identity=count_person, fk_picture=count_picture))
                count_picture+=1
            for sniffed_probe in person.device.probes:
                PROBES.append(Probes(ssid=sniffed_probe.ssid, timestamp=sniffed_probe.timestamp,fk_mac=person.device.mac.address, fk_place=1))
            count_person+=1

        db.session.bulk_save_objects(MACS)
        db.session.bulk_save_objects(PROBES)
        db.session.bulk_save_objects(IDENTITY)
        db.session.bulk_save_objects(PICTURES)
        db.session.bulk_save_objects(REPRESENTS)
        db.session.commit()

        mariage.mariage()
        wrong_identities = mariage.compute_success_rate(dict_real_couple)
        wrong_uuid = [one_identity.uuid for one_identity in IDENTITY if one_identity.id in wrong_identities]
        return wrong_uuid


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

def generate_people(nb_person, duration):
    current_address = "AA:AA:AA:AA:AA:AA"
    random_duration = np.random.normal(20, 5, nb_person) 
    people = []
    for i in range(nb_person):
        probs = np.exp(range(4,0, -1))
        probs /= probs.sum()
        sample = np.random.choice(range(1,5), p=probs, size=1)[0]
        visit_list = []
        current_MAC = MAC(current_address)
        current_address = int_to_mac(mac_to_int(current_address)+1)
        current_device = Device(current_MAC, [])
        for j in range(sample):
            arrival_time = random.randint(0, duration)
            duration_time = min(int(random_duration[i]), duration - arrival_time)
            visit = Visit(arrival_time, duration_time)
            visit_list.append(visit)
        current_person = Person(str(uuid4())[:12],current_device,[],duration_time,arrival_time, visit_list)
        people.append(current_person)
    return people

def launch_simulation(nb_person,duration):
    people = generate_people(nb_person, duration)
    simulation = Simulation(people, 1, datetime.now(timezone.utc), duration)
    for i in range(duration):
        simulation.run_one_time_unit()

    for person in simulation.people:
        if len(person.pictures) == 0:
            simulation.events = [event for event in simulation.events if event[1] != person.uuid]
            simulation.people.remove(person)

    wrong_uuid = simulation.export_to_db()
    simulation.plot_graph(wrong_uuid)