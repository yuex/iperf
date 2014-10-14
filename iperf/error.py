#!/usr/bin/env python

_ERROR_DICT = {
    4004: "data not found"
    ,4001: "user not found"
    ,4002: "app not found"
    ,6001: "null post data"
    }

_UNDEFINED_ERROR_MSG = "undefined error type"
_UNDEFINED_ERROR_CODE = -1

class _ErrorCls(object):
    def __init__(self, error_dict):
        self._error_dict = {}
        self._error_dict.update(error_dict)
        self._error_dict.update({v:k for k,v in error_dict.items()})

    def __getitem__(self, key):
        if isinstance(key, int):
            try:
                return self._error_dict[key]
            except KeyError:
                return "%s: %d" % (_UNDEFINED_ERROR_MSG, key)
        elif isinstance(key, str):
            try:
                return self._error_dict[key]
            except KeyError:
                return _UNDEFINED_ERROR_CODE
        else:
            raise KeyError("ERROR_DICT supports only int and str as key")

ERROR_DICT = _ErrorCls(_ERROR_DICT)
