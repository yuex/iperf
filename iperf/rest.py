#!/usr/bin/env python
from init import app
from utils import rest_register
from flask import request
from flask import jsonify

@rest_register([
'/hello'
,'/foo'
,'/bar'
,'/world'
])
def hello():
    return 'hello'

#@rest_register(app.url_dict, '/user/1', ['GET','POST'])
@rest_register(url='/world', method=['GET'])
def world():
    return 'world'

@rest_register(url='/post', method=['POST'])
def post_data():
    from kafka import KafkaClient
    from kafka import SimpleProducer

    kafka = KafkaClient(app.config['KAFKA_SERVER'])
    producer = SimpleProducer(kafka)
    if not request.json:
        resp = 'null post data'
    else:
        resp = producer.send_messages(app.config['KAFKA_TOPIC'], str(request.json))
        if resp:
            resp = {'error':resp[0].error,'offset':resp[0].offset}
    kafka.close()
    return jsonify(resp)
    #return request
