#!/usr/bin/env python

from flask import Flask
from flask import jsonify
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy

from functools import wraps
import inspect
import json

from settings import settings
from error import ERROR_DICT

app = Flask(__name__)
app.config.update(settings)
db = SQLAlchemy(app)

from model import *

# recursively flatten DBJSON, dict(DBJSON), or list(DBJSON)
def flatten(obj):
    ret = obj
    if isinstance(ret, list):
        li = []
        for i in range(len(ret)):
            li.append(flatten(ret[i]))
        ret = li
    elif isinstance(ret, dict):
        di = {}
        for k,v in ret.items():
            di[k] = flatten(v)
        ret = di
    elif isinstance(ret, DBJSON):
        ret = flatten(dict(ret))
    else:
        pass
    return ret

class DBJSON(object):
    __prefix__ = None
    __empty__ = None

    def __getitem__(self, name):
        if hasattr(self,name):
            return getattr(self, name)
    
    def __setitem__(self, name, value):
        if hasattr(self, name):
            setattr(self, name, value)
            return value

    def __iter__(self):
        return iter({k:getattr(self,k) for k in self.public()}.items())

    @classmethod
    def public(cls):
        return {k for k in cls.__dict__ if k[0] != '_'}

    #def __repr__(self):
        #return str(flatten(self))

# decorator auto_json 
def result_jsonify(name_prefix=None, empty_error_code=None):
    outerArgs = { 
            "name_prefix": name_prefix
            ,"empty_error_code":empty_error_code
            }
    def auto_json_noarg(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name_prefix = outerArgs["name_prefix"]
            empty_error_code = outerArgs["empty_error_code"]

            v = func(*args, **kwargs)
            #vt = type(v)
            if isinstance(v, DBJSON):
                v = flatten(v)
            elif isinstance(v, dict):
                v = flatten(v)
            elif isinstance(v, list):
                v = flatten(v)
                if not name_prefix:
                    if len(v) == 1:
                        v = v[0]
                    else:
                        raise TypeError("can't JSON sequentialize list without a name prefix")
            elif isinstance(v,str):
                name_prefix = None
                v = { 
                        "errorCode":ERROR_DICT[v]
                        ,"errorMsg":v
                        }
            elif isinstance(v,int):
                name_prefix = None
                v = { 
                        "errorCode":v
                        ,"errorMsg":ERROR_DICT[v]
                        }
            else:
                raise TypeError("function decorated by auto_json must return a heir of DBJSON (%s given)" % type(v))

            if name_prefix:
                return jsonify({name_prefix:v})
            else:
                return jsonify(**v)
        return wrapper
    return auto_json_noarg

def register_rest(cls):
    cls_n = cls.__name__.lower()
    base_url = '/%s' % cls_n
    id_url  = base_url + '/<int:theid>'
    pub_keys = cls.public()

    url = {}

    # /user/<int:id>/<attr>
    for i in pub_keys:
        url[i] = id_url + '/<string:attr>'

    # /user/<int:id>
    url[None] = id_url

    for k,v in url.items():
        # get at /user/<int:theid> and /user/<int:theid>/<attr>
        @app.route(url[k], endpoint=cls_n+'_get_%s'%k, methods=['GET'])
        @result_jsonify(cls.__prefix__, cls.__empty__)
        def get(theid,attr=None):
            ret = cls.query.filter_by(id=theid).first()
            if ret == None:
                return '%s not found' % cls_n
            elif attr:
                if hasattr(ret,attr):
                    ret = {attr:ret[attr]}
                else:
                    return 'invalid key'
            return ret

    # put at /user/<int:theid>
    @app.route(id_url, endpoint=cls_n+'_put', methods=['PUT'])
    @result_jsonify(cls.__prefix__, cls.__empty__)
    def put(theid):
        if not request.json:
            return 'null post data'
        for k in request.json:
            if not hasattr(cls, k):
                return 'invalid key'
        ret = cls.query.filter_by(id=theid).first()
        if ret == None:
            return '%s not found' % cls_n
        for k,v in request.json.items():
            ret[k] = v
        try:
            db.session.commit()
        except Exception as e:
            return str(e)
        return ret

    # post new record at /user
    @app.route(base_url, endpoint=cls_n+'_post', methods=['POST'])
    @result_jsonify(cls.__prefix__, cls.__empty__)
    def insert():
        if not request.json:
            return 'null post data'
        ret = request.json
        try:
            ret = cls(**ret)
        except Exception as e:
            return str(e)
        db.session.add(ret)
        try:
            db.session.commit()
        except Exception as e:
            return str(e)
        return ret

    # delete record at /user/<int:theid>
    @app.route(id_url, endpoint=cls_n+'_delete', methods=['DELETE'])
    @result_jsonify(cls.__prefix__, cls.__empty__)
    def delete(theid):
        obj = cls.query.filter_by(id=theid).first()
        ret = obj
        if ret != None:
            db.session.delete(obj)
            db.session.commit()
        else:
            return '%s not found' % cls_n
        return ret

    # /user/help
    url['help'] = base_url
    @app.route(url['help'], endpoint=cls_n+'_help', methods=['GET'])
    @result_jsonify(cls.__prefix__, cls.__empty__)
    def help():
        d = {}
        for k in pub_keys:
            d[k] = k
        return d

    return cls

def autoinit(init_func):
    names, args, keywords, defaults = inspect.getargspec(init_func)
    @wraps(init_func)
    def init(self, *args, **kwargs):
        if defaults:
            for name, default in zip(reversed(names),reversed(defaults)):
                if not hasattr(self, name):
                    setattr(self, name, default)
        for name,arg in zip(names[1:], args) + kwargs.items():
            if hasattr(self, name):
                setattr(self, name, arg)
        init_func(self, *args, **kwargs)
    return init

@register_rest
class User(DBJSON,db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    usertype = db.Column(db.String(20), nullable=False)

    apps = db.relationship('App', cascade='all,delete-orphan')
    plans = db.relationship('Plan', cascade='all,delete-orphan')

    @autoinit
    def __init__(self, username, email, password, usertype):
        pass

@register_rest
class App(DBJSON,db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appname = db.Column(db.String(80), nullable=False)

    @autoinit
    def __init__(self, appname, owner):
        pass

@register_rest
class Plan(DBJSON,db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    planname = db.Column(db.String(80), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    test_units = db.relationship('TestUnit', cascade='all,delete-orphan')

    @autoinit
    def __init__(self, planname, count, owner):
        pass

@register_rest
class TestUnit(DBJSON,db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    datetime_start = db.Column(db.Integer, nullable=False)
    datetime_end   = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(1024), nullable=False)
    http_type = db.Column(db.String(20), nullable=False)
    data = db.Column(db.Text, nullable=True)
    count = db.Column(db.Integer, nullable=False)
    interval_mean = db.Column(db.Float, nullable=False)
    interval_var  = db.Column(db.Float, nullable=False)
    interval_dist = db.Column(db.String(20), nullable=False)

    @autoinit
    def __init__(self,
            belong_to, datetime_start, datetime_end,
            url, http_type, data, count,
            interval_mean, interval_var , interval_dist):
        pass

@register_rest
class Metric(DBJSON,db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    src_app = db.Column(db.Integer, db.ForeignKey('app.id'), nullable=False)
    dst_test_unit = db.Column(db.Integer, db.ForeignKey('test_unit.id'), nullable=False)
    datetime_start = db.Column(db.Integer, nullable=False)
    datetime_end   = db.Column(db.Integer, nullable=False)
    count_enduser    = db.Column(db.Integer, nullable=False)
    count_url_access = db.Column(db.Integer, nullable=False)
    count_response_time_avg = db.Column(db.Float, nullable=False)

    #app_metric = db.relationship('App', backref=db.backref('metrics', lazy='dynamic'))
    #test_unit_metric = db.relationship('TestUnit', backref=db.backref('metrics', lazy='dynamic'))

    @autoinit
    def __init__(self,
            src_app, dst_test_unit, datetime_start, datetime_end,
            count_enduser, count_url_access, count_response_time_avg):
        pass

@register_rest
class CountResponseCode(DBJSON, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey('metric.id'), nullable=False)
    response_code = db.Column(db.String(3), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    
    @autoinit
    def __init__(self, belong_to, response_code, count):
        pass

@register_rest
class CountOSType(DBJSON, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey('metric.id'), nullable=False)
    os_type = db.Column(db.String(10), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    
    @autoinit
    def __init__(self, belong_to, os_type, count):
        pass

@register_rest
class CountOSVersion(DBJSON, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey('metric.id'), nullable=False)
    os_version = db.Column(db.String(10), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    @autoinit
    def __init__(self, belong_to, os_version, count):
        pass

@register_rest
class CountModelName(DBJSON, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey('metric.id'), nullable=False)
    model_name = db.Column(db.String(20), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    @autoinit
    def __init__(self,
            id, belong_to, model_name, count):
        pass

@register_rest
class CountGeoRegion(DBJSON, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey('metric.id'), nullable=False)
    geo_region = db.Column(db.String(20), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    @autoinit
    def __init__(self, belong_to, geo_region, count):
        pass

@register_rest
class CountNetworkType(DBJSON, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey('metric.id'), nullable=False)
    network_type = db.Column(db.String(20), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    @autoinit
    def __init__(self, belong_to, network_type, count):
        pass

@register_rest
class CountIsp(DBJSON, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey('metric.id'), nullable=False)
    isp = db.Column(db.String(20), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    @autoinit
    def __init__(self, belong_to, isp, count):
        pass

def init_db():
    db.drop_all()
    db.create_all()
    db.session.add(User("yuexin", "yuecn41@gmail.com", "iloveyou", "test needer"))
    db.session.add(User("fucheng", "fucheng.zhang@163.com", "iloveyou", "app provider"))
    db.session.add(App("fuTianQi", 2))
    #db.session.add(App("fuChat", 2))
    db.session.add(App(appname="fuChat", owner=2))
    db.session.add(Plan("yue's plan A", 100, 1))
    db.session.add(Plan("yue's plan B", 42, 1))
    db.session.add(TestUnit(1, 1409544000, 1409547600,
        "http://yuex.in", "GET", '', 10, 1, 0, "uniform"))
    db.session.add(TestUnit(1, 1409500800, 1409502600,
        "http://yuex.in", "GET", '', 10, 1, 0, "uniform"))

    db.session.commit()

if __name__ == '__main__':
    #app.run()
    #init_db()
    #print User.query.filter_by(username='yuexin').all()

    #user = User("yuexin","yuecn41@gmail.com")
    #print user.__public__
    #print json.dumps({"user":user.__public__})
    app.run()
