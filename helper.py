#!/usr/bin/env python
# -*-coding:utf-8-*-
import json
import sys
import os


def toDict(val):
    # convert any 'AttributeDict' type found to 'dict'
    parsedDict = dict(val)
    for key, val in parsedDict.items():
        if 'list' in str(type(val)):
            parsedDict[key] = [_parseValue(x) for x in val]
        else:
            parsedDict[key] = _parseValue(val)
    return parsedDict


def _parseValue(val):
    # check for nested dict structures to iterate through
    if 'dict' in str(type(val)).lower():
        return toDict(val)
    # convert 'HexBytes' type to 'str'
    elif 'HexBytes' in str(type(val)):
        return val.hex()
    else:
        return val


def to_many_request(e):
    if "Draining connection" in str(e):
        return True
    elif "Too many requests" in str(e):
        return True
    elif "HTTP 429" in str(e):
        return True
    elif "execution aborted" in str(e):
        return True
    else:
        return False
