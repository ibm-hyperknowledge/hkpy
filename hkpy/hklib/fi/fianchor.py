###
# Copyright (c) 2022-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from collections import OrderedDict

from hkpy.hklib.fi.fioperator import FIOperator


class FIAnchor:

    def __init__(self, indexer, token = None, operator = FIOperator.NONE ):
        from hkpy.hklib.fi.fi import FI
        if not isinstance(indexer, FI):
            indexer = FI(indexer, )

        if isinstance(token, dict):
            token = OrderedDict(token)

        self.indexer = indexer;
        self.token = token;
        self.operator = operator;


    def __str__(self):
        from hkpy.hklib.fi.fi import FI

        strAnchor = ''
        strAnchor = strAnchor + self.indexer.__str__()
        strAnchor = strAnchor + (self.operator.value if self.operator != FIOperator.NONE and self.operator != None  else '')
        if self.token:
            if isinstance(self.token, FI):
                strAnchor = f"""{strAnchor}({self.token.__str__()})"""
            elif isinstance(self.token, dict) and len(self.token) > 0:
                args = []
                for param, value in self.token.items():
                    args.append(f"""{param}: {value}""")
                strArguments = ','.join(args)
                strAnchor = f"""{strAnchor}({{{strArguments}}})"""
            elif isinstance(self.token, list) and len(self.token) > 0:
                elements = []
                for value in self.token:
                    if isinstance(value, str):
                        elements.append(f'''"{value}"''')
                    else:
                        elements.append(f'''{value}''')
                str_elements = ','.join(elements)
                strAnchor = f"""{strAnchor}([{str_elements}])"""
            else:
                strAnchor = f"""{strAnchor}({self.token.__str__()})"""

        return f"""{strAnchor}"""
