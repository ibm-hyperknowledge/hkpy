# MIT License

# Copyright (c) 2019 IBM Hyperlinked Knowledge Graph

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json, io, os, time

from ..oops import HKBError
from .constants import DEBUG_MODE

__all__ = ['response_validator', 'generate_id']

def generate_id(entity):
    return str(hex(int(time.time() * id(entity))))

def response_validator(response, whitelist=None):
    """
    """
    
    res_code = response.status_code
    res_url = response.url
    try:
        if DEBUG_MODE:
            log_curl_command(response)
        res_content = response.json()
    except:
        res_content = None

    if(res_code in whitelist if whitelist else 200 <= res_code < 300):
        return res_code, res_content
    else:
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
