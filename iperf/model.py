from init import db
from utils import DbBase
from utils import rest_register

@rest_register
class User(DbBase,db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    usertype = db.Column(db.String(20), nullable=False)

    apps = db.relationship('Application', cascade='all,delete-orphan')
    plans = db.relationship('Plan', cascade='all,delete-orphan')

@rest_register(url='/app')
class Application(DbBase,db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    appname = db.Column(db.String(80), nullable=False)

@rest_register
class Plan(DbBase,db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    planname = db.Column(db.String(80), nullable=False)
    count = db.Column(db.Integer, nullable=False)

    test_units = db.relationship('TestUnit', cascade='all,delete-orphan')

@rest_register
class TestUnit(DbBase,db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey(Plan.id), nullable=False)
    datetime_start = db.Column(db.Integer, nullable=False)
    datetime_end   = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(1024), nullable=False)
    http_type = db.Column(db.String(20), nullable=False)
    data = db.Column(db.Text, nullable=True)
    count = db.Column(db.Integer, nullable=False)
    interval_mean = db.Column(db.Float, nullable=False)
    interval_var  = db.Column(db.Float, nullable=False)
    interval_dist = db.Column(db.String(20), nullable=False)

@rest_register
class Metric(DbBase,db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    src_app = db.Column(db.Integer, db.ForeignKey(Application.id), nullable=False)
    dst_test_unit = db.Column(db.Integer, db.ForeignKey(TestUnit.id), nullable=False)
    datetime_start = db.Column(db.Integer, nullable=False)
    datetime_end   = db.Column(db.Integer, nullable=False)
    count_enduser    = db.Column(db.Integer, nullable=False)
    count_url_access = db.Column(db.Integer, nullable=False)
    count_response_time_avg = db.Column(db.Float, nullable=False)

    #app_metric = db.relationship('Application', backref=db.backref('metrics', lazy='dynamic'))
    #test_unit_metric = db.relationship('TestUnit', backref=db.backref('metrics', lazy='dynamic'))

@rest_register
class CountResponseCode(DbBase, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey(Metric.id), nullable=False)
    response_code = db.Column(db.String(3), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    
@rest_register
class CountOSType(DbBase, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey(Metric.id), nullable=False)
    os_type = db.Column(db.String(10), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    
@rest_register
class CountOSVersion(DbBase, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey(Metric.id), nullable=False)
    os_version = db.Column(db.String(10), nullable=False)
    count = db.Column(db.Integer, nullable=False)

@rest_register
class CountModelName(DbBase, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey(Metric.id), nullable=False)
    model_name = db.Column(db.String(20), nullable=False)
    count = db.Column(db.Integer, nullable=False)

@rest_register
class CountGeoRegion(DbBase, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey(Metric.id), nullable=False)
    geo_region = db.Column(db.String(20), nullable=False)
    count = db.Column(db.Integer, nullable=False)

@rest_register
class CountNetworkType(DbBase, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey(Metric.id), nullable=False)
    network_type = db.Column(db.String(20), nullable=False)
    count = db.Column(db.Integer, nullable=False)

@rest_register
class CountIsp(DbBase, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    belong_to = db.Column(db.Integer, db.ForeignKey(Metric.id), nullable=False)
    isp = db.Column(db.String(20), nullable=False)
    count = db.Column(db.Integer, nullable=False)
