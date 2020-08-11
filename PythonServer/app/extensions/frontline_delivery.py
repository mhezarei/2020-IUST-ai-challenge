# -*- coding: utf-8 -*-

# project imports
from ..ks.models import FrontlineDelivery, UnitType
from ..gui_events import GuiEvent, GuiEventType


def tick(self, world, side):
    base = world.bases[side]

    self.delivery_rem_time -= 1
    if self.delivery_rem_time > 0:
        return []

    base.frontline_deliveries.remove(self)
    for ammo_type, count in self.ammos.items():
        box_size = base.factory.c_ammo_box_sizes[ammo_type]
        base.units[UnitType(ammo_type.value)].ammo_count += count * box_size
    return [GuiEvent(GuiEventType.AmmoDelivered, side=side, frontline_delivery=self)]


FrontlineDelivery.tick = tick
