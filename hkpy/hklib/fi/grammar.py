###
# Copyright (c) 2022-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

FI_GRAMMAR = r"""
start               : fijs
fijs				: id (_DOT_OP anchor)*

anchor              : indexer ( OPERATOR )? ( _BEGIN_PARAM token _END_PARAM )?
indexer             : id

token               : jsonvalue

_DOT_OP              : "."
OPERATOR            : "*"
_BEGIN_PARAM         : WS* "(" WS*
_END_PARAM           : WS* ")" WS*


jsonvalue            : fijs | FALSE | NULL | TRUE | object | array | NUMBER | STRING
_BEGIN_ARRAY          : WS* "[" WS*
_BEGIN_OBJECT         : WS* "{" WS*
_END_ARRAY            : WS* "]" WS*
_END_OBJECT           : WS* "}" WS*
_NAME_SEPARATOR       : WS* ":" WS*
_VALUE_SEPARATOR      : WS* "," WS*
FALSE                : "false"
NULL                 : "null"
TRUE                 : "true"
object               : _BEGIN_OBJECT (member (_VALUE_SEPARATOR member)*)? _END_OBJECT
member               : (STRING | id) _NAME_SEPARATOR jsonvalue
array                : _BEGIN_ARRAY (jsonvalue (_VALUE_SEPARATOR jsonvalue)*)? _END_ARRAY


id                  : IDSIMPLE | IDEXTENDED | IRI
IDSIMPLE		    : /[_a-zA-Z][a-zA-Z0-9_-]*/
IDEXTENDED          : /``[^\\x60\\x5C\\xA\\xD]*``/
IRI                 : "<" ("a".."z" | "A".."Z" | "0".."9" | "!" | "\x23".."\x2F" | ":" | ";" | "=" | "?" | "@" | "[" | "]" | "_" | "|" | "~")* ">"

%import common.ESCAPED_STRING -> STRING
%import common.SIGNED_NUMBER -> NUMBER
%import common.WS

"""
