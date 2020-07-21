FROM python:3
ADD . /
RUN mkdir pictures
RUN chmod +x /start.sh
RUN pip3 install -r requirements.txt
ENV AWS_DEFAULT_REGION=us-east-1
CMD ["/start.sh"]
