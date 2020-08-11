# -*- coding: utf-8 -*-

# project imports
from ..ks.models import Warehouse
from ..gui_events import GuiEvent, GuiEventType


def tick(self, world, side):
    self.materials_reload_rem_time -= 1
    if self.materials_reload_rem_time > 0:
        return []

    self.materials_reload_rem_time = self.c_materials_reload_duration
    for material in self.materials.values():
        material.count = material.c_capacity
    return [GuiEvent(GuiEventType.WarehouseReload, side=side)]


Warehouse.tick = tick
