# -*- coding: utf-8 -*-
import json
from collections import namedtuple


def convertStrToTuple(response):
    _tuple = json.loads(
        response
        , object_hook=lambda d: namedtuple('_tuple', d.keys())(*d.values()))
    return _tuple

''' 샘플
{
    "ret": 0, 
    "msg": "", 
    "data": 
    {
        "id": "yk1226ull", 
        "pw": "sha1$$356a192b7913b04c54574d18c28d46e6395428ab", 
        "name": "이영균", 
        "telegram_key": "806709206:AAFYP71lHpTHxsn0SU3ixUDpIu1xcg0nWro", 
        "telegram_chat_id": "679304200", 
        "expired_date": "2019-05-02", 
        "permissions": ["LOGIN_ALLOW"], 
        "group": ["지도기술개발팀"], 
        "permission_group": [], 
        "teamLeader": []
    }
}
'''