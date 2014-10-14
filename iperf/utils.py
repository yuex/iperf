from init import db
from init import app
from inspect import isclass,isfunction

from inspect import getargspec
from inspect import isfunction
from functools import wraps

from flask import jsonify
from flask import request
from error import ERROR_DICT

METHODS_TYPE = ('GET','POST','PUT','DELETE')
url_dict=app.url_dict

def rest_register_old(cls):
    cls_n = cls.__name__.lower()
    base_url = '/%s' % cls_n
    id_url  = base_url + '/<int:theid>'
    pub_keys = cls.public()

    url = {}

    # /user/<int:id>/<attr>
    for i in pub_keys:
        url[i] = id_url + '/<string:attr>'

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

    # /user/<int:id>
    # get at /user/<int:theid> and /user/<int:theid>/<attr>
    @app.route(id_url, endpoint=cls_n+'_get', methods=['GET'])
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

def rest_register(url=None, method=['GET']):
    ''' a decorator to register class or function to url with specified methods
        to decorate class, it should define classmethod GET(), POST(), etc

        class: 
            @rest_register
            @rest_register('/hello')
            @rest_register(['/hello', '/world'])
        function:
            @rest_register('/hello')
            @rest_register('/hello', 'GET')
            @rest_register('/hello', ['GET','POST'])
            @rest_register(['/hello', '/world'], 'GET')
            @rest_register(['/hello', '/world'], ['GET','POST'])
    '''
    def _listify(obj):
        ''' not list -> []
            str -> [str]
            list -> list
            _ -> raise ValueError
        '''
        if not obj:
            ret = []
        elif isinstance(obj, str):
            ret = [obj]
        elif isinstance(obj, list):
            ret = obj
        else:
            raise ValueError("unknown type of obj (%r)" % type(obj))
        return ret

    def _register_url(tds):
        for url in tds:
            url_dict[url] = tds[url]

    def _rest_register_class(obj, urls=[]):
        t_urls = urls

        if not isclass(obj):
            raise ValueError("obj must be class")
        if not isinstance(t_urls, list):
            raise ValueError("t_urls must be list")

        cls_name = obj.__name__.lower()
        t_urls.insert(0, '/%s' % cls_name)
        tds = {}
        for m in METHODS_TYPE:
            if not hasattr(obj,m):
                continue
            td = {
                    m: {
                    'endpoint': 'cls_%s_%s' % (cls_name, m)
                    ,'view_function': getattr(obj, m)
                    }
                }
            temp_urls = t_urls
            if m != 'POST':
                temp_urls = [ t_url + '/<int:theid>' for t_url in t_urls ]
            for t_url in temp_urls:
                if not t_url in tds:
                    tds[t_url] = {}
                tds[t_url].update(td)
        return tds

    def _rest_register_function(obj, t_urls, t_methods):
        if not isfunction(obj):
            raise ValueError("obj must be function")
        if not isinstance(t_urls, list):
            raise ValueError("t_urls must be list")
        if not isinstance(t_methods, list):
            raise ValueError("t_methods must be list")
        td = { 
                m: { 
                'endpoint': 'func_%s_%s' % (obj.func_name, m)
                ,'view_function': obj
                } for m in t_methods if m in METHODS_TYPE
            }
        tds = {t_url:td for t_url in t_urls}
        return tds

    def _rest_register_no_arg(obj):
        if not isclass(obj):
            # XXX: is it meanful to register a function without url?
            raise TypeError("can only decorate class if no args provided")
        tds = _rest_register_class(obj)
        _register_url(tds)
        return obj

    def _rest_register_with_args(obj):
        t_urls = _listify(url)
        t_methods = _listify(method)
        if isclass(obj):
            tds = _rest_register_class(obj, t_urls)
        elif isfunction(obj):
            tds = _rest_register_function(obj, t_urls, t_methods)
        else:
            raise TypeError("can only decorates class or function")
        _register_url(tds)
        return obj

    if isclass(url) or isfunction(url):
        return _rest_register_no_arg(url)
    else:
        return _rest_register_with_args

def url_dict_install(url_dict):
    for url,methods in url_dict.items():
        for method,func in methods.items():
            method = method.upper()
            app.add_url_rule(
                    url
                    ,func['endpoint']
                    ,func['view_function']
                    ,methods=[method])

def flatten(obj):
    ''' recursively convert dict or list containing DbBase
    to plain dict or list
    '''
    ret = obj
    if isinstance(obj, list):
        ret = [flatten(item) for item in obj]
    elif isinstance(obj, dict):
        ret = { k:flatten(v) for k,v in obj.items() }
    elif isinstance(obj, DbBase):
        ret = flatten(dict(ret))
    else:
        pass
    return ret

def to_json(with_name_prefix=False):
    def _to_json(func):
        @wraps(func)
        def __to_json(*args,**kwargs):
            v = func(*args,**kwargs)
            name_prefix = False
            v = flatten(v)
            if isinstance(with_name_prefix, bool):
                name_prefix = with_name_prefix
            if isinstance(v,str):
                name_prefix = False
                v = { 
                        "errorCode":ERROR_DICT[v]
                        ,"errorMsg":v
                        }
            elif isinstance(v,int):
                name_prefix = False
                v = { 
                        "errorCode":v
                        ,"errorMsg":ERROR_DICT[v]
                        }
            elif isinstance(v, dict):
                if name_prefix:
                    v = {v.__name__:v}
            else:
                raise TypeError("function decorated by auto_json must "\
                        "return a heir of DbBase (%s given)" % type(v))
            return jsonify(v)
        return __to_json

    if isfunction(with_name_prefix):
        return _to_json(with_name_prefix)
    return _to_json

def result_jsonify_old(name_prefix=None, empty_error_code=None):
    ''' convert DbBase to json
    '''
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
            if isinstance(v, DbBase):
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
                raise TypeError("function decorated by auto_json must return a heir of DbBase (%s given)" % type(v))

            if name_prefix:
                return jsonify({name_prefix:v})
            else:
                return jsonify(**v)
        return wrapper
    return auto_json_noarg

def result_jsonify(name_prefix=None, empty_error_code=None):
    '''
    dict -> json
    str -> { errorCode, errorMsg = str }
    int -> { errorCode = int, errorMsg }
    '''
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
            if isinstance(v,str):
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
            elif not isinstance(v, dict):
                raise TypeError("function decorated by auto_json must "\
                        "return a heir of DbBase (%s given)" % type(v))

            if name_prefix:
                return jsonify({name_prefix:v})
            else:
                return jsonify(**v)
        return wrapper
    return auto_json_noarg

def autoinit(init_func):
    names, args, keywords, defaults = getargspec(init_func)
    @wraps(init_func)
    def _autoinit(self, *args, **kwargs):
        for name,arg in zip(names[1:], args) + kwargs.items():
            if hasattr(self, name):
                setattr(self, name, arg)
        if defaults:
            for name, default in zip(reversed(names),reversed(defaults)):
                if not hasattr(self, name):
                    setattr(self, name, default)
        init_func(self, *args, **kwargs)
    return _autoinit

class DbBase(object):
    def __getitem__(self, name):
        if hasattr(self,name):
            return getattr(self, name)
    
    def __setitem__(self, name, value):
        if hasattr(self, name):
            setattr(self, name, value)
            return value

    def __iter__(self):
        ''' feed to dict() or list() '''
        #return iter({k:getattr(self,k) for k in self.public()}.items())
        for k in self.public():
            yield k,getattr(self,k)

    @classmethod
    def public(cls):
        return {k for k in cls.__dict__ if k[0] != '_'}

    def __init__(self, *args, **kwargs):
        for name,value in kwargs.items():
            if not name in self.public():
                raise TypeError("__init__() got an unexpected keyword argument '%s'" % name)
            else:
                setattr(self, name, value)

    @classmethod
    def help(cls):
        return {k:k for k in cls.public()}

    @classmethod
    @to_json
    def GET(cls, theid, attr=None):
        ret = cls.query.filter_by(id=theid).first()
        if ret == None:
            return '%s not found' % cls.__name__
        elif attr:
            if hasattr(ret,attr):
                ret = {attr:ret[attr]}
            else:
                return 'invalid key'
        return ret
    
    @classmethod
    @to_json
    def POST(cls):
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

    @classmethod
    @to_json
    def DELETE(cls, theid):
        obj = cls.query.filter_by(id=theid).first()
        ret = obj
        if ret != None:
            db.session.delete(obj)
            db.session.commit()
        else:
            return '%s not found' % cls.__name__
        return ret

    @classmethod
    @to_json
    def PUT(cls, theid):
        if not request.json:
            return 'null post data'
        for k in request.json:
            if not hasattr(cls, k):
                return 'invalid key'
        ret = cls.query.filter_by(id=theid).first()
        if ret == None:
            return '%s not found' % cls.__name__
        for k,v in request.json.items():
            ret[k] = v
        try:
            db.session.commit()
        except Exception as e:
            return str(e)
        return ret
