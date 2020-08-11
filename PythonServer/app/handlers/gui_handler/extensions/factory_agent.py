# -*- coding: utf-8 -*-

# project imports
from ....ks import models
from ..utils import change_animator_state


def gui_pick_material(self, world, gui_event):
    # [GuiEvent(GuiEventType.PickMaterial, side=side, agent=self, materials=materials)]
    self._last_gui_event = gui_event
    change_animator_state(world, self._gui_ref, 'Use')
    self._gui_update_materials(world)
    world.bases[gui_event.side].backline_delivery.gui_update_materials(world, gui_event)


def gui_put_material(self, world, gui_event):
    # [GuiEvent(GuiEventType.PutMaterial, side=side, agent=self, machine=machine)]
    self._last_gui_event = gui_event
    change_animator_state(world, self._gui_ref, 'Use')
    self._gui_update_materials(world)
    gui_event.machine.gui_put_material(world, gui_event)
    # raise NotImplementedError
    pass


def gui_pick_ammo(self, world, gui_event):
    # [GuiEvent(GuiEventType.PickAmmo, side=side, agent=self, machine=machine, ammo_type=ammo_type)]
    self._last_gui_event = gui_event
    change_animator_state(world, self._gui_ref, 'Use')
    self._gui_update_ammos(world)
    gui_event.machine.gui_pick_ammo(world, gui_event)
    # raise NotImplementedError
    pass


def gui_put_ammo(self, world, gui_event):
    # [GuiEvent(GuiEventType.PutAmmo, side=side, agent=self, ammos=ammos)]
    self._last_gui_event = gui_event
    change_animator_state(world, self._gui_ref, 'Use')
    self._gui_update_ammos(world)
    world.bases[gui_event.side].backline_delivery.gui_update_ammos(world, gui_event)


models.FactoryAgent.gui_pick_material = gui_pick_material
models.FactoryAgent.gui_put_material = gui_put_material
models.FactoryAgent.gui_pick_ammo = gui_pick_ammo
models.FactoryAgent.gui_put_ammo = gui_put_ammo
