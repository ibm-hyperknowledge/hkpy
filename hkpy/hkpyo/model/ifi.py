





# IFI := artifact | artifact '#' fragment
# artifact := IFI | '<' IFI '>' | atom
# fragment := '<' IFI '>' | atom
# atom := url-like_encoded_with_no_spaces_string | '"' no_spaces_string '"'

class IRI(str):
    pass

class IFIBase():
    pass

class IFIAtom():

    def __init__(self, expression) -> None:
        super().__init__()
        self._expression = expression
        # if isinstance(expression, str):
        #     self.expression = IFIAtom.processString(expression)

    def __str__(self) -> str:
        return self._expression

    def __repr__(self) -> str:
        return self.__str__()

class IFI(IFIBase):

    @classmethod
    def parse_string(cls, expression : str) -> tuple:
        #re.split(r'("[^"|(?<!\\)]+")', expression) #split at matching, non-nesting paretheses
        #TODO: replace with lexical parser, like lark

        global_parts = []
        in_quoted_expression = False
        in_diamond = 0

        # SOME_CHAR = 0
        # FIRST_CHAR = 1
        # LAST_CHAR = 2
        #
        # what_char = SOME_CHAR
        current_part = ''
        # TODO: add support to escaped /" and /< and />
        for i in range(0,len(expression)):
            c = expression[i]
            # what_char = LAST_CHAR if i == len(expression) - 1 else FIRST_CHAR if i == 0 else SOME_CHAR

            if not in_quoted_expression and c == '"':
                in_quoted_expression = True
                current_part += c
            elif in_quoted_expression:
                if c == '"':
                    in_quoted_expression = False
                # ignore any char in non-nesting double quotes
                current_part += c
            else:
                if c == '#' and in_diamond == 0:
                    #restart part
                    if expression[i-1] != '>': global_parts.append(current_part)
                    current_part = ''
                elif c == '<':
                    if in_diamond == 0:
                        if i != 0 and expression[i-1] != '#':
                            raise Exception('< must be first char in part')
                    in_diamond += 1
                elif c == '>':
                    in_diamond -= 1
                    if in_diamond == 0:
                        #found matching
                        #if what_char is not LAST_CHAR and expression(i+1) != '#': raise Exception('> must be last char in part')
                        global_parts.append(IFI.parse_string(current_part))
                        current_part = ''
                    elif in_diamond < 0:
                        raise Exception('Closing diamond without opening one')
                    else:
                        current_part += c
                else:
                    if len(current_part) == 0 and i != 0 and expression[i-1] not in ['#', '<']:
                        raise Exception('> must be last char in part')
                    current_part += c

        if in_quoted_expression:
            raise Exception("Quote not closed")
        elif in_diamond != 0:
            raise Exception("Unmatched")

        if not(expression[0] == '<' and expression[-1] == '>'):
            global_parts.append(current_part) #last part

        return tuple(global_parts)




    @classmethod
    def processTuple(cls, *segments):
        if len(segments) == 1:
            if isinstance(segments[0], IFI):
                artifact = segments[0].artifact
                fragment = segments[0].fragment
            elif isinstance(segments[0], str):
                artifact = IFIAtom(segments[0])
                fragment = None
            elif isinstance(segments[0], tuple):
                artifact = IFI(*segments[0])
                fragment = None
            else:
                raise Exception('Wrong type:', type(segments[0]))
        elif len(segments) == 2:
            if isinstance(segments[0], IFI):
                artifact = segments[0] if segments[0].fragment is not None else segments[0].artifact
            elif isinstance(segments[0], tuple):
                artifact = IFI(*segments[0])
            else:
                artifact = IFIAtom(segments[0])

            if isinstance(segments[1], IFI):
                fragment = segments[1]
            elif isinstance(segments[1], tuple):
                fragment = IFI(*segments[1])
            else:
                fragment = IFIAtom(segments[1])
        elif len(segments) > 2:
            artifact = IFI(*segments[:-1])

            if isinstance(segments[-1], IFI):
                fragment = segments[-1]
            elif isinstance(segments[-1], tuple):
                fragment = IFI(*segments[-1])
            else:
                fragment = IFIAtom(segments[-1])
        else: #len == 0
            artifact = None
            fragment = None

        return artifact, fragment

    def __init__(self, *segments):
        if isinstance(segments, str):
            (a, f) = IFI.processTuple(IFI.parse_string(segments))
        else:
            expanded_segments = []
            for s in segments:
                # if isinstance(s, IRI):
                #     expanded_segments += IFI.parse_string(f"<{s.__str__()}>")
                if isinstance(s, str):
                    expanded_segments += IFI.parse_string(s)
                else:
                    expanded_segments.append(s)

            (a, f) = IFI.processTuple(*expanded_segments)

        self._artifact = a
        self._fragment = f

    @property
    def artifact(self) -> IFIBase:
        return self._artifact

    @property
    def fragment(self) -> IFIBase:
        return self._fragment

    @property
    def artifact_or_fragment(self) -> IFIBase:
        """
        Return fragment if not None, else returns artifact
        :return:
        """
        return self.fragment if self.fragment is not None else self.artifact

    def __eq__(self, o: object) -> bool:
        return super().__eq__(o)

    def __str__(self) -> str:
        if self._fragment is None:
            return f'{self.artifact.__str__()}'
        elif isinstance(self._fragment, IFIAtom):
            return f'{self.artifact.__str__()}#{self.fragment.__str__()}'
        else:
            return f'{self.artifact.__str__()}#<{self.fragment.__str__()}>'

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return super().__hash__()


# class IFI():
#
#     def __init__(self, artifact : Union[IFI, str, IRI], fragment : Union[IFI, str, IRI, None] = None):
#         if isinstance(artifact, str) or isinstance(artifact, IRI):
#             self._artifact = IFIAtom(artifact)
#         elif isinstance(artifact, IFI):
#             self._artifact = artifact
#         else:
#             raise Exception('Artifact must be IFI or str')
#
#         if isinstance(fragment, str) or isinstance(fragment, IRI):
#             self._fragment = IFIAtom(fragment)
#         elif isinstance(artifact, IFI):
#             self._fragment = fragment
#         elif fragment is None:
#             self._fragment = None
#         else:
#             raise Exception('Fragment must be IFI, str or None')
#
#     @property
#     def artifact(self) -> IFI:
#         return self._artifact
#
#     @property
#     def fragment(self) -> IFI:
#         return self._fragment
#
#     def __eq__(self, o: object) -> bool:
#         return super().__eq__(o)
#
#     def __str__(self) -> str:
#         return f'{self.artifact.__str__()}#{self.fragment.__str__()}'
#
#     def __hash__(self) -> int:
#         return super().__hash__()
#
# class IFIAtom(IFI):
#
#     def __init__(self, expression : Union[str, IRI]) -> None:
#         super().__init__(artifact=self)
#         self._expression =  expression
#
#     @property
#     def artifact(self) -> IFI:
#         return self
#
#     @property
#     def fragment(self) -> IFI:
#         return None
#
#     def expression(self) -> str:
#         return self._expression
#
#     def __str__(self) -> str:
#         return self._expression
