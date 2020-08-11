# -*- coding: utf-8 -*-

# project imports
from ....ks.models import Machine, ECell, MachineStatus
from ..utils import change_animator_state, change_text


def gui_init(self, world, side):
    self._gui_cell_ref, self._gui_panel_ref = ECell.Machine.gui_init(world, side, self.position)


def gui_put_material(self, world, gui_event):
    change_animator_state(world, self._gui_cell_ref, 'Working')
    change_text(world, self._gui_panel_ref, 'Status', self.status.name)
    change_text(world, self._gui_panel_ref, 'CurrentAmmo', self.current_ammo.name)


def gui_pick_ammo(self, world, gui_event):
    change_animator_state(world, self._gui_cell_ref, 'Idle')
    change_text(world, self._gui_panel_ref, 'Status', self.status.name)
    change_text(world, self._gui_panel_ref, 'CurrentAmmo', '-')


def gui_ammo_ready(self, world, gui_event):
    # [GuiEvent(GuiEventType.MachineAmmoReady, side=side, machine=self)]
    change_animator_state(world, self._gui_cell_ref, 'AmmoReady')
    change_text(world, self._gui_panel_ref, 'Status', self.status.name)
    change_text(world, self._gui_panel_ref, 'RemTime', '-')


def gui_update_timer(self, world):
    if self.status == MachineStatus.Working:
        change_text(world, self._gui_panel_ref, 'RemTime', str(self.construction_rem_time))


Machine.gui_init = gui_init
Machine.gui_put_material = gui_put_material
Machine.gui_pick_ammo = gui_pick_ammo
Machine.gui_ammo_ready = gui_ammo_ready
Machine.gui_update_timer = gui_update_timer
