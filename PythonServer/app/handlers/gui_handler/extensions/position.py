# -*- coding: utf-8 -*-

# project imports
from ....ks.models import Position


def set_gui_offsets(gui_offsets):
    Position._gui_offsets = gui_offsets


def get_gui_offset(self):
    return self._gui_offsets[self]


Position.set_gui_offsets = set_gui_offsets
Position.get_gui_offset = get_gui_offset
