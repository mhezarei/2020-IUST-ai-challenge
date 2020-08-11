# -*- coding: utf-8 -*-

# chillin imports
from chillin_server.gui.scene_actions import ChangeSprite, ChangeIsActive, Asset

# project imports
from ....ks.models import BacklineDelivery, ECell
from ..utils import change_blackboard_int


UPDATE_DURATION = 0.5


def gui_init(self, world, side, position):
    self._gui_cell_ref, self._gui_panel_ref = ECell.BacklineDelivery.gui_init(world, side, position)


def gui_update_materials(self, world, gui_event):
    # [GuiEvent(GuiEventType.PutMaterial, side=side, agent=self, materials=materials)]
    for mat_type, mat_count in gui_event.materials.items():
        if mat_count == 0:
            continue

        change_blackboard_int(world, self._gui_panel_ref, 'Materials/{}/Count'.format(mat_type.name), UPDATE_DURATION, self.materials[mat_type])


def gui_update_ammos(self, world, gui_event):
    # [GuiEvent(GuiEventType.PickAmmo, side=side, agent=self, ammos=ammos)]
    for ammo_type, ammo_count in gui_event.ammos.items():
        if ammo_count == 0:
            continue

        change_blackboard_int(world, self._gui_panel_ref, 'Ammos/{}/Count'.format(ammo_type.name), UPDATE_DURATION, self.ammos[ammo_type])


BacklineDelivery.gui_init = gui_init
BacklineDelivery.gui_update_materials = gui_update_materials
BacklineDelivery.gui_update_ammos = gui_update_ammos
