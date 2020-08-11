# -*- coding: utf-8 -*-

# project imports
from ..ks.models import Machine, MachineStatus
from ..gui_events import GuiEvent, GuiEventType


def tick(self, world, side):
    if self.status != MachineStatus.Working:
        return []

    self.construction_rem_time -= 1
    if self.construction_rem_time > 0:
        return []

    self.status = MachineStatus.AmmoReady
    return [GuiEvent(GuiEventType.MachineAmmoReady, side=side, machine=self)]


Machine.tick = tick
