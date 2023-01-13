###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import requests
from enum import Enum, unique

__all__ = ['DEBUG_MODE', 'SSL_VERIFY', 'LAMBDA', 'HKType', 'ConnectorType', 'RoleType', 'AnchorType', 'ContentType']

DEBUG_MODE = False

SSL_VERIFY = False
if not SSL_VERIFY:
    requests.packages.urllib3.disable_warnings()

AUTH_TOKEN = None

LAMBDA = 'λ'

class BaseEnum(Enum):
    def __str__(self):
        return self.value
    
    def __eq__(self, other):
        return other == self.value

@unique
class HKType(BaseEnum):
    CONNECTOR = 'connector'
    CONTEXT = 'context'
    NODE = 'node'
    LINK = 'link'
    REFERENCENODE = 'ref'
    TRAIL = 'trail'
    ANCHOR = 'anchor'
    GRAPH = 'graph'

@unique
class ConnectorType(BaseEnum):
    HIERARCHY = 'h'
    FACTS = 'f'
    REASONING = 'r'
    CONSTRAINT = 'c'
    CAUSAL = 'C'

@unique
class RoleType(BaseEnum):
    NONE = 'n'
    SUBJECT = 's'
    OBJECT = 'o'
    PARENT = 'p'
    CHILD = 'c'

@unique
class AnchorType(BaseEnum):
    SPATIAL = 'spatial'
    TEMPORAL = 'temporal'
    TEXT = 'text'

@unique
class ContentType(BaseEnum):
    JSON = 'application/json'
    RDF = 'application/rdf+xml'
    TRIG = 'application/trig'
    NQUADS = 'application/n-quads'
    NTRIPLES = 'application/n-triples'
    TURTLE = 'text/turtle'
    TEXT = 'text/plain'
