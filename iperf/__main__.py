#!/usr/bin/env python
from __init__ import *

if __name__ == '__main__':

    def reset_db():
        db.drop_all()
        db.create_all()

        db.session.add(User(
            username="yuexin"
            ,email="yuecn41@gmail.com"
            ,password="iloveyou"
            ,usertype="test needer"))
        db.session.add(User(
            username="fucheng"
            ,email="fucheng.zhang@163.com"
            ,password="iloveyou"
            ,usertype="app provider"))
        db.session.add(Application(
            appname="fuTianQi"
            ,owner=2))
        db.session.add(Application(
            appname="fuChat"
            ,owner=2))
        db.session.add(Plan(
            planname="yue's plan A"
            ,count=100
            ,owner=1))
        db.session.add(Plan(
            planname="yue's plan B"
            ,count=42
            ,owner=1))
        db.session.add(TestUnit(
            belong_to=1
            ,datetime_start=1409544000
            ,datetime_end=1409547600
            ,url="http://yuex.in"
			,http_type="GET"
			,data=''
			,count=10
			,interval_mean=1
			,interval_var=0
			,interval_dist="uniform"))
        db.session.add(TestUnit(
            belong_to=1
			,datetime_start=1409500800
			,datetime_end=1409502600
            ,url="http://yuex.in"
			,http_type="GET"
			,data=''
			,count=10
			,interval_mean=1
			,interval_var=0
			,interval_dist="uniform"))

        db.session.commit()

    reset_db()
    #print app.url_dict
    #print app.url_dict['/hello']
    app.run(host=app.config['HOSTNAME'], port=app.config['PORT'])
