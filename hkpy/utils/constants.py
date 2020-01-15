###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import requests
from enum import Enum, unique

__all__ = ['DEBUG_MODE', 'SSL_VERIFY', 'LAMBDA', 'HKType', 'AnchorType', 'ConnectorType', 'ContentType']

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
class ConnectorType(Enum):
    HIERARCHY = "h"
    FACTS = "f"
    REASONING = "r"
    CONSTRAINT = "c"
    CAUSAL = "C"

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