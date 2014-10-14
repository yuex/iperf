user_1 = dict(
    username="yuexin"
    ,email="yuecn41@gmail.com"
    ,password="iloveyou"
    ,usertype="test needer"
    )

user_2 = dict(
    username="fucheng"
    ,email="fucheng.zhang@163.com"
    ,password="iwantyou"
    ,usertype="app provider"
    )

application_1 = dict(
    appname="fuTianQi"
    ,owner=1
    )

application_2 = dict(
    appname="fuChat"
    ,owner=2
    )

plan_1 = dict(
    planname="yue's plan 1"
    ,count=100
    ,owner=1
    )

plan_2 = dict(
    planname="yue's plan 2"
    ,count=200
    ,owner=2
    )

testunit_1 = dict(
    belong_to=1
    ,datetime_start=1409544000
    ,datetime_end=1409547600
    ,url="http://yuex.in"
    ,http_type="GET"
    ,data=''
    ,count=10
    ,interval_mean=1
    ,interval_var=0
    ,interval_dist="uniform"
    )

testunit_2 = dict(
    belong_to=2
    ,datetime_start=1409500800
    ,datetime_end=1409502600
    ,url="www.sina.com.cn"
    ,http_type="POST"
    ,data='hello'
    ,count=20
    ,interval_mean=2
    ,interval_var=2
    ,interval_dist="poisson"
    )

metric_1 = dict(
    src_app = 1
    ,dst_test_unit = 1
    ,datetime_start=1409544000
    ,datetime_end=1409547600
    ,count_enduser=1000
    ,count_url_access=10000
    ,count_response_time_avg=10
    )

metric_2 = dict(
    src_app = 2
    ,dst_test_unit = 2
    ,datetime_start=2409544000
    ,datetime_end=2409547600
    ,count_enduser=2000
    ,count_url_access=20000
    ,count_response_time_avg=20
    )

countresponsecode_1 = dict(
    belong_to=1
    ,response_code='100'
    ,count=100
    )
countresponsecode_2 = dict(
    belong_to=2
    ,response_code='200'
    ,count=200
    )

countostype_1 = dict(
    belong_to=1
    ,os_type='Android'
    ,count=100
    )

countostype_2 = dict(
    belong_to=2
    ,os_type='Android'
    ,count=200
    )

countosversion_1 = dict(
    belong_to=1
    ,os_version='Android 1.1'
    ,count=100
    )

countosversion_2 = dict(
    belong_to=2
    ,os_version='Android 2.2'
    ,count=200
    )

countmodelname_1 = dict(
    belong_to=1
    ,model_name='xiaomi 1s'
    ,count=100
    )

countmodelname_2 = dict(
    belong_to=2
    ,model_name='xiaomi 2s'
    ,count=200
    )

countgeoregion_1 = dict(
    belong_to=1
    ,geo_region='Beijing#1'
    ,count=100
    )

countgeoregion_2 = dict(
    belong_to=2
    ,geo_region='Beijing#2'
    ,count=200
    )

countnetworktype_1 = dict(
    belong_to=1
    ,network_type='wifi#1'
    ,count=10
    )

countnetworktype_2 = dict(
    belong_to=2
    ,network_type='wifi#2'
    ,count=20
    )

countisp_1 = dict(
    belong_to=1
    ,isp='cmcc111'
    ,count=100
    )

countisp_2 = dict(
    belong_to=2
    ,isp='cmcc222'
    ,count=200
    )
