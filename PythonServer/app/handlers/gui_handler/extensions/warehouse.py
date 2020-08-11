# -*- coding: utf-8 -*-

# project imports
from ....ks.models import Warehouse
from ..courier import Courier


def gui_reload(self, world, gui_event):
    for material in self.materials.values():
        material.gui_reload(world, gui_event)

    self.gui_create_courier(world, gui_event.side)


def gui_create_courier(self, world, side):
    self._courier = Courier(
        world,
        side,
        self.c_materials_reload_duration,
        'WarehouseDeliveryPivot',
        world.location.WAREHOUSE_DELIVERY_START,
        world.location.WAREHOUSE_DELIVERY_ARRIVE,
        world.location.WAREHOUSE_DELIVERY_END,
        False,
        self.c_materials_reload_duration / 3,
    )


def gui_update_courier_rem_cycles(self, world):
    self._courier.gui_update_rem_cycles(world, self.materials_reload_rem_time)


Warehouse.gui_reload = gui_reload
Warehouse.gui_create_courier = gui_create_courier
Warehouse.gui_update_courier_rem_cycles = gui_update_courier_rem_cycles
