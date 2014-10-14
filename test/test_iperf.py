#!/usr/bin/env python
from iperf.__init__ import db
from iperf.__init__ import app

from iperf.model import User
from iperf.model import Application
from iperf.model import Plan
from iperf.model import TestUnit
from iperf.model import Metric
from iperf.model import CountResponseCode
from iperf.model import CountOSType
from iperf.model import CountOSVersion
from iperf.model import CountGeoRegion
from iperf.model import CountNetworkType
from iperf.model import CountIsp

import json

def reset_db():
    db.drop_all()
    db.create_all()

app.config['TESING']=True
reset_db()
server = app.test_client()
from example_data import *

def insert_db(obj, cls):
    obj_db = cls(**obj)
    db.session.add(obj_db)
    db.session.commit()
    return obj_db.id

def get_name(cls,num=1,base_url=False):
    name = cls.__name__.lower()
    if base_url:
        url = '/%s' % name
    else:
        url = '/%s/%s' % (name,num)
    obj = eval('_'.join([name,str(num)]))
    return name,url,obj

def assert_200(resp):
    assert resp.status == '200 OK'
    data = json.loads(resp.data)
    assert not 'errorCode' in data
    return data

def assert_dict(obj, data, key=None):
    if key:
        assert obj[key] == data[key]
        return
    for name in obj:
        assert obj[name] == data[name]

def json_dump(a_dict):
    data = json.dumps(a_dict)
    header=[
        ('Content-Type','application/json')
        ,('Content-Length',len(data))
        ]
    return header, data

def check_model_get(cls,data_id=1):
    name,url,obj = get_name(cls,data_id)
    obj_id = insert_db(obj, cls)

    #resp = server.get('%s/%s' % (url, obj_id))
    resp = server.get(url)
    data = assert_200(resp)

    assert_dict(obj, data)
    return obj_id

def check_model_delte(cls,obj_id):
    name,url,obj = get_name(cls)
    #resp = server.delete('%s/%s' % (url,obj_id))
    resp = server.delete(url)
    assert_200(resp)
    obj = cls.query.filter_by(id=obj_id).first()
    assert obj == None

def check_model_put(cls, obj_id, data_id):
    name, url, _ = get_name(cls, obj_id)
    _,_,obj = get_name(cls, data_id)
    for key in obj:
        headers, data = json_dump({key:obj[key]})
        resp = server.put(
                url
                ,headers=headers
                ,data=data)
        assert_200(resp)
        obj_db = cls.query.filter_by(id=obj_id).first()
        assert_dict(obj, obj_db, key)

def check_model_post(cls,data_id=1):
    name, url, obj = get_name(cls, base_url=True)
    headers, data = json_dump(obj)
    resp = server.post(
            url
            ,headers=headers
            ,data=data)
    data = assert_200(resp)
    obj_id = data["id"]
    obj_db = cls.query.filter_by(id=obj_id).first()
    assert_dict(obj, obj_db)
    return obj_id

for cls in [
    User
    ,Application
    ,Plan
    ,TestUnit
    ,Metric
    ,CountResponseCode
    ,CountOSType
    ,CountOSVersion
    ,CountGeoRegion
    ,CountNetworkType
    ,CountIsp
    ]:

    name = cls.__name__
    #get: reset db, db.insert #1 example data, http get
    #put: #1 -> #2, db.get
    #post: reset db, post #1, db.get
    #delete: delete #1
    cmd = '''
def test_{0}():
    cls = {0}
    reset_db()
    obj_id = check_model_get(cls,data_id=1)
    check_model_put(cls,obj_id,2)
    reset_db()
    obj_id = check_model_post(cls,1)
    check_model_delte(cls, obj_id)
    '''.format(name)
    exec(cmd)
