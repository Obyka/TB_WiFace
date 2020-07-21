#!/bin/bash
simulation=0
nb_person=10
duration=1000

if [[ $simulation -eq 1 ]];
then
	python build_database.py --nb_person $nb_person --duration $duration --simulation && python3 server.py
else
	python3 build_database.py && python3 server.py
fi
