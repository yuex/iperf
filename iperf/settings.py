#!/usr/bin/env python
settings = dict(
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/iperf.db'
    ,DEBUG = True
    ,HOSTNAME = '0.0.0.0'
    ,PORT = 5000
    ,KAFKA_SERVER = 'ibm.iliork.com:9092'
    ,KAFKA_TOPIC = 'test'
    )
