###
# Copyright (c) 2022-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from lark import Lark, Token
from lark import Transformer

from hkpy.hklib.fi import FI, FIOperator, FIAnchor
from hkpy.hklib.fi.fi import BasicHKID, ExtendedHKID, IriHKID, HKID
from hkpy.hklib.fi.grammar import FI_GRAMMAR
import ast as astlib


def parse_fi(fi: str) -> FI:
    """
    Parse an FI string and returned the instantiated FI
    """

    parser = Lark(FI_GRAMMAR)
    ast = parser.parse(fi)
    obj_fi = postProcessTree(ast)

    return obj_fi

def parse_id(id: str) -> HKID:
    parser = Lark(FI_GRAMMAR, start="id")
    ast = parser.parse(id)
    obj_id = processId(ast)

    return obj_id

def parse_anchor(anchor: str) -> HKID:
    parser = Lark(FI_GRAMMAR, start="anchor")
    ast = parser.parse(anchor)
    obj_anchor = processAnchor(ast)

    return obj_anchor

def postProcessTree(ast):
    return processFijs(ast)


def processFijs(ast):
    ast = ast.children[0]
    if len(ast.children) == 1:
        artifact = processId(ast.children[0])
        return FI(artifact)
    elif len(ast.children) >= 2:
        firstArtifact = processId(ast.children[0])
        anchor = processAnchor(ast.children[1])

        lastFI = FI(firstArtifact, anchor)
        for i in range(2, len(ast.children)):
            # start on the 2nd anchor, if any
            anchor = processAnchor(ast.children[i])
            lastFI = FI(lastFI, anchor)
        return lastFI
    else:
        raise Exception(f"Error parsing {ast.text}")


def processAnchor(ast):
    if len(ast.children) == 1:
        indexer = processIndexer(ast.children[0])
        return FIAnchor(indexer)
    elif len(ast.children) == 2:
        indexer = processIndexer(ast.children[0])
        if isinstance(ast.children[1], Token) and ast.children[1].type == 'operator':
            return FIAnchor(indexer, None, FIOperator.DESCRIPTION)
        else:
            token = processToken(ast.children[1])
            return FIAnchor(indexer, token)
    elif len(ast.children) == 3:
        indexer = processIndexer(ast.children[0])
        token = processToken(ast.children[2])
        return FIAnchor(indexer, token, FIOperator.DESCRIPTION)
    else:
        raise Exception(f"Error parsing {ast}")


def processToken(ast):
    return processJsonPlus(ast.children[0])


def processJsonPlus(ast):
    ast = ast.children[0]
    if isinstance(ast, Token):
        if ast.type == 'FALSE': return False
        if ast.type == 'NULL': return None
        if ast.type == 'TRUE': return True
        if ast.type == 'NUMBER': return astlib.literal_eval(ast)
        if ast.type == 'STRING': return astlib.literal_eval(ast)
    else:
        if ast.data == 'fijs': return processFijs(ast)
        if ast.data == 'object': return processObject(ast)
        if ast.data == 'array': return processArray(ast)


def processArray(ast):
    array = []
    if len(ast.children) > 0:
        members = ast.children
        for member in members:
            element = processJsonPlus(member)
            array.append(element)
    return array


def processObject(ast):
    object = {}
    if len(ast.children) > 0:
        members = ast.children
        for member in members:
            pair = processMember(member)
            object[pair[0]] = pair[1]
    return object


def processMember(ast):
    key = None
    if isinstance(ast.children[0], Token) and ast.children[0].type == 'STRING':
        key = ast.children[0][1:-1]
    elif ast.children[0].data == 'id':
        key = processId(ast.children[0])
    else:
        raise Exception(f"Error processing: {ast.children[0]}")

    value = processJsonPlus(ast.children[1])
    return [key, value]


def processIndexer(ast):
    return processId(ast.children[0])


def processId(ast):
    ast = ast.children[0]
    if ast.type == 'IDSIMPLE':
        return BasicHKID(ast.__str__())
    elif ast.type == 'IDEXTENDED':
        return ExtendedHKID(ast[2:-2])
    elif ast.type == 'IRI':
        return IriHKID(ast[1:-1])
    else:
        raise Exception(f"Error parsing {ast}")
