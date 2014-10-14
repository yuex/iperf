FROM ubuntu

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python
RUN apt-get -y install ipython
RUN apt-get -y install python-pip
RUN pip install flask
RUN pip install flask-sqlalchemy
RUN pip install nose
RUN pip install kafka-python

ADD iperf /root/iperf

EXPOSE 5000

ENTRYPOINT python /root/iperf
