FROM python:3
ADD . /
RUN chmod +x /start.sh
RUN pip3 install -r requirements.txt

#CMD [ "python3","./build_database.py", "&&","python3", "./server.py" ]
CMD ["/start.sh"]
