###
# Copyright (c) 2022-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import re
from typing import Optional, Union

from hkpy.hklib.fi.fianchor import FIAnchor


class FI:

    def __init__(self, artifact : [str, 'FI'], anchor: Optional[Union[FIAnchor, str]] = None):
        if isinstance(artifact, str):

            if not anchor:
                from hkpy.hklib.fi.fiparser import parse_fi
                fi = parse_fi(artifact)
                artifact = fi._artifact
                anchor = fi._anchor
            else:
                from hkpy.hklib.fi.fiparser import parse_id
                id = parse_id(artifact)
                artifact = id

        if isinstance(artifact, str):
            from hkpy.hklib.fi.fiparser import parse_anchor
            anchor = parse_anchor(artifact)

        if anchor and not isinstance(anchor, FIAnchor):
            raise Exception('Argument anchor must be an HKAnchor')

        self._artifact = artifact
        self._anchor = anchor

    @property
    def artifact(self):
        #never return string;
        if isinstance(self._artifact, HKID):
            return FI(self._artifact)

        return self._artifact;

    @property
    def anchor(self):
        return self._anchor

    def has_anchor(self) -> bool:
        return self.anchor is not None

    def __str__(self):
        strFI = self._artifact.__str_decorated__() if isinstance(self._artifact, HKID) else self._artifact.__str__()
        strFI = f"""{strFI}.{self._anchor}""" if self._anchor else strFI
        return strFI


class HKID:

    def __init__(self, id_ : str):
        self._id = id_

    def __str__(self):
        return self._id

    def __str_decorated__(self):
        pass


class BasicHKID(HKID):
    def __init__(self, id_):
        # let ast = PARSER.getAST(id, target = 'idSimple');
        super().__init__(id_)

    def __str_decorated__(self):
        return self._id


class ExtendedHKID(HKID):

    def __init__(self, id_):
        # let ast = PARSER.getAST(`\`\`${id}\`\``, target = 'idExtended');
        super().__init__(id_)

    def __str_decorated__(self):
        return "``" + self._id + "``"


class IriHKID(HKID):

    def __init__(self, id_):
        # let ast = PARSER.getAST(`<${id}>`, target = 'iri');
        super().__init__(id_)

    def __str_decorated__(self):
        return "<" + self._id + ">"

