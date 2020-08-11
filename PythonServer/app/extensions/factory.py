# -*- coding: utf-8 -*-

# project imports
from ..ks.models import Factory


def tick(self, world, side):
    gui_events = []
    for machine in self.machines.values():
        gui_events.extend(machine.tick(world, side))
    return gui_events


Factory.tick = tick
