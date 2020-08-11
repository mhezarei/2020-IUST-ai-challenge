# -*- coding: utf-8 -*-

# project imports
from ..ks.models import Position


def __eq__(self, other):
    if isinstance(other, Position):
        return self.index == other.index
    return NotImplemented


def __ne__(self, other):
    r = self.__eq__(other)
    if r is not NotImplemented:
        return not r
    return NotImplemented


def __hash__(self):
    return self.index


def __add__(self, other):
    if isinstance(other, Position):
        return Position(index = self.index + other.index)
    if isinstance(other, int):
        return Position(index = self.index + other)
    return NotImplemented


def __iadd__(self, other):
    if isinstance(other, Position):
        self.index += other.index
    elif isinstance(other, int):
        self.index += other
    else:
        return NotImplemented


def __sub__(self, other):
    if isinstance(other, Position):
        return Position(index = self.index - other.index)
    if isinstance(other, int):
        return Position(index = self.index - other)
    return NotImplemented


def __isub__(self, other):
    if isinstance(other, Position):
        self.index -= other.index
    elif isinstance(other, int):
        self.index -= other
    else:
        return NotImplemented


def __repr__(self):
    return '<index: {}>'.format(self.index)


Position.__eq__ = __eq__
Position.__ne__ = __ne__
Position.__hash__ = __hash__
Position.__add__ = __add__
Position.__iadd__ = __iadd__
Position.__sub__ = __sub__
Position.__isub__ = __isub__
Position.__repr__ = __repr__
