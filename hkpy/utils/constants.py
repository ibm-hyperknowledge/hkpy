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

import requests
from enum import Enum, unique

__all__ = ['DEBUG_MODE', 'SSL_VERIFY', 'LAMBDA', 'HKType', 'AnchorType', 'ContentType']

DEBUG_MODE = False

SSL_VERIFY = False
if not SSL_VERIFY:
    requests.packages.urllib3.disable_warnings()

AUTH_TOKEN = None

LAMBDA = 'λ'

@unique
class HKType(Enum):
    CONNECTOR = 'connector'
    CONTEXT = 'context'
    NODE = 'node'
    LINK = 'link'
    REFERENCENODE = 'ref'

    def __str__(self):
        return self.value
    
    def __eq__(self, other):
        return other == self.value

@unique
class AnchorType(Enum):
    SPATIAL = 'spatial'
    TEMPORAL = 'temporal'
    TEXT = 'text'

    def __str__(self):
        return self.value
    
    def __eq__(self, other):
        return other == self.value

@unique
class ContentType(Enum):
    JSON = 'application/json'
    RDF = 'application/rdf+xml'
    TRIG = 'application/trig'
    NQUADS = 'application/n-quads'
    NTRIPLES = 'application/n-triples'
    TURTLE = 'text/turtle'
    TEXT = 'text/plain'

    def __str__(self):
        return self.value
    
    def __eq__(self, other):
        return other == self.value