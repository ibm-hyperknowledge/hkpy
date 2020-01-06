###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

__all__ = ['HKBError', 'HKpyError']

class HKBError(Exception):
    """
    """

    def __init__(self, *args, **kwargs):
        if args and kwargs:
            super().__init__(args, kwargs)
        elif args:
            super().__init__(args)
        elif kwargs:
            super().__init__(kwargs)
        else:
            super().__init__()

class HKpyError(Exception):
    """
    """

    def __init__(self, *args, **kwargs):
        if args and kwargs:
            super().__init__(args, kwargs)
        elif args:
            super().__init__(args)
        elif kwargs:
            super().__init__(kwargs)
        else:
            super().__init__()