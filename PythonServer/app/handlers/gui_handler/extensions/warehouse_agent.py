# -*- coding: utf-8 -*-

# chillin imports
from chillin_server.gui.scene_actions import ChangeIsActive

# project imports
from ....ks import models
from ..utils import change_animator_state


def gui_pick_material(self, world, gui_event):
    # [GuiEvent(GuiEventType.PickMaterial, side=side, agent=self, material=material)]
    self._last_gui_event = gui_event
    change_animator_state(world, self._gui_ref, 'Use')
    self._gui_update_materials(world)
    gui_event.material.gui_pick(world, gui_event)


def gui_put_material(self, world, gui_event):
    # [GuiEvent(GuiEventType.PutMaterial, side=side, agent=self, materials=materials)]
    self._last_gui_event = gui_event
    change_animator_state(world, self._gui_ref, 'Use')
    self._gui_update_materials(world)
    world.bases[gui_event.side].backline_delivery.gui_update_materials(world, gui_event)


def gui_pick_ammo(self, world, gui_event):
    # [GuiEvent(GuiEventType.PickAmmo, side=side, agent=self, ammos=ammos)]
    self._last_gui_event = gui_event
    change_animator_state(world, self._gui_ref, 'Use')
    self._gui_update_ammos(world)
    world.bases[gui_event.side].backline_delivery.gui_update_ammos(world, gui_event)


def gui_put_ammo(self, world, gui_event):
    # [GuiEvent(GuiEventType.PutAmmo, side=side, agent=self, ammos=ammos, frontline_delivery=frontline_delivery)]
    self._last_gui_event = gui_event
    change_animator_state(world, self._gui_ref, 'Use')
    self._gui_update_ammos(world)
    gui_event.frontline_delivery.gui_put_ammo(world, gui_event)
    pass


models.WarehouseAgent.gui_pick_material = gui_pick_material
models.WarehouseAgent.gui_put_material = gui_put_material
models.WarehouseAgent.gui_pick_ammo = gui_pick_ammo
models.WarehouseAgent.gui_put_ammo = gui_put_ammo
