###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import json, io, os, time

from requests import Response

from ..oops import HKBError
from .constants import DEBUG_MODE

__all__ = ['response_validator', 'generate_id']

def generate_id(entity):
    return str(hex(int(time.time() * id(entity))))

def response_validator(response : Response, whitelist=None, content='json'):
    """
    """
    
    res_code = response.status_code
    res_url = response.url
    try:
        if DEBUG_MODE:
            log_curl_command(response)
        if content == 'json':
            res_content = response.json()
        elif content == 'text':
            res_content = response.text
        elif content == 'raw':
            res_content = response.raw
        else:
            res_content = response.content
    except:
        res_content = None

    if res_code in whitelist if whitelist else 200 <= res_code < 300:
        return res_code, res_content
    else:
        if res_content is None:
            try:
                res_content = response.json()
            except:
                res_content = response.text
        raise HKBError(code=res_code, message=res_content, url=res_url)

def log_curl_command(response):
    """
    logs the curl command that corresponds to the request
    :param response:
    :return:
    """
    request = response.request
    command = "curl -X {method} -H {headers} -d '{data}' '{uri}'"
    method = request.method
    uri = request.url
    data = request.body
    headers = [f'"{k}: {v}"' for k, v in request.headers.items()]
    headers = ' -H '.join(headers)
    if isinstance(data, io.StringIO):
        data = data.getvalue()
    elif isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data)
    elif not data:
        data = '[]'

    print(command.format(method=method, headers=headers, data=data, uri=uri))

def generate_json_file(fname, data_format='hkobj', *args):
    """
    """

    t = []
    for a in args:
        if(data_format == 'hkobj'):
            a = list(a.to_dict())
        for i in a:
            t.append(i)
    with open(fname, 'w') as f:
        f.write(json.dumps(t, indent=2))
