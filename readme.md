# Intro

A REST server , built on flask, exposes database tables for CRUD-style access.

It's still very primitive. But the way it exploits to automatically generates REST URLs from the declarations of database tables may be of some interests.

# Execution

```shell
$ python iperf
```

# URL Patterns

`localhost:5000/<table>/<record-id>/<attr>`

* localhost:5000, the url prefix for localhost testing
* table: table name in the database, e.g., user, app, plan, testunit, metric, etc
* record-id: database table record id, a.k.a the primary key
* attr: field name in the record, if omitted, return available attribute

# Testing

## Manual

```shell
$ curl localhost:5000/user/2/apps
$ curl localhost:5000/user/1/plans
$ curl localhost:5000/app/1
$ curl -X DELETE localhost:5000/user/2
$ curl -iH 'Content-Type: application/json' -X PUT -d '{"username":"yuex-jr-xin}' localhost:5000/user/1
$ cat user
{
    "email": "yuecn42@gmail.com", 
    "password": "iloveyou", 
    "username": "yuecn42", 
    "usertype": "test needer"
}
$ curl -iH 'Content-Type: application/json' -X POST -d @user localhost:5000/user
```

## Automatic

```shell
$ nosetests
```

# Docker Build

```shell
$ docker build -t iperf .
```

# Todo

* ~~Support GET~~
* ~~Support PUT~~
* ~~Support POST~~
* ~~Support DELETE~~
* ~~datetime string or seconds from epoch?~~ utc epoch
* Implement testing plans distributes logic
* ~~Dockerize it~~
* REST api access authentication, oAuth/oAuth2, perhaps
* Migrate to mysql
* ~~Add cases and tools for testing~~ deps `nose`. use cmd `nosetests` to test
* ~~Refactor the code structure~~
    * ~~Refactor model.py~~
* More realistic testing database

# Requirements

* python 2.7
* flask 0.10
* flask-sqlalchemy 1.0
* sqlite3
* nose
* kafka-python
