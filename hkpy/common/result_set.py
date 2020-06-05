###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

from typing import List, Any, Optional, TypeVar, Generic, Union

__all__ = ['ResultRow', 'ResultSet']


from typing import List, Any, Optional, TypeVar, Generic, Union


class ResultSetIterator(object):
    def __init__(self, result_set):
        self._result_set = result_set
        self._index = 0

    def __next__(self):
        if self._index < len(self._result_set._result):
            result = self._result_set._result[self._index]
            self._index += 1
            return result
        raise StopIteration


T = TypeVar('T')


class ResultRow(Generic[T]):
    def __init__(self, result_set: 'ResultSet', row: List[T]):
        self._result_set = result_set
        self._row = row

    def __getitem__(self, key: Union[str, int]) -> T:
        if isinstance(key, str):
            index = self._result_set._get_key_index(key)
        else:
            index = key
        return self._row[index]

    def get_keys(self) -> List[str]:
        return self._result_set._keys

    def __len__(self):
        return len(self._row)


T2 = TypeVar('T2')


class ResultSet(Generic[T2]):
    def __init__(self, keys: Optional[List[str]] = None, result: Optional[List[ResultRow[T2]]] = None):
        self._keys = keys
        if result is None:
            result = list()
        self._result = result

    @classmethod
    def build(cls, row_matrix: List[List[T2]], keys: Optional[List[str]] = None) -> 'ResultSet[T2]':
        instance = cls(keys)
        instance._result = [ResultRow[T2](instance, row) for row in row_matrix]
        return instance

    def _get_key_index(self, key) -> int:
        return self._keys.index(key)

    def __iter__(self):
        return ResultSetIterator(self)

    def __len__(self) -> int:
        return len(self._result)

    def __add__(self, other: 'ResultSet[T2]') -> 'ResultSet[T2]':
        if self._keys != other._keys:
            raise ValueError(f'Result set keys should match. ({self._keys}) and ({other._keys})')
        return ResultSet[T2](self._keys, self._result.extend(other._result))
