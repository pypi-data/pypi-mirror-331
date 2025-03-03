# -*- coding: utf-8 -*-

"""
Argument manipulation utilities.
"""

import typing as T


class REQ:
    def __eq__(self, other):
        return isinstance(other, REQ)


class NA:
    def __eq__(self, other):
        # print(self, other)
        return isinstance(other, NA)


T_KWARGS = T.Dict[str, T.Any]


def rm_na(**kwargs) -> T_KWARGS:
    """
    Remove NA values from kwargs.
    """
    return {
        key: value for key, value in kwargs.items() if isinstance(value, NA) is False
    }


if __name__ == "__main__":
    pass
