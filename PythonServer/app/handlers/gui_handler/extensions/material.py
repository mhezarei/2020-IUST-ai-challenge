# -*- coding: utf-8 -*-

# chillin imports
from chillin_server.gui.scene_actions import ChangeImage, ChangeText, Asset

# project imports
from ....ks.models import Material, ECell, MaterialType
from ..utils import change_blackboard_int


UPDATE_DURATION = 0.5
MATERIAL_ASSET_INDEX = {
    MaterialType.Powder: 3,
    MaterialType.Iron: 2,
    MaterialType.Carbon: 0,
    MaterialType.Gold: 1,
    MaterialType.Shell: 4,
}


def gui_init(self, world, side):
    self._gui_cell_ref, self._gui_panel_ref = ECell.Material.gui_init(world, side, self.position)

    # Update panel
    world.scene.add_action(ChangeImage(
        ref = self._gui_panel_ref,
        child_ref = 'Image',
        sprite_asset = Asset(bundle_name = 'main', asset_name = 'MaterialsIcon', index = MATERIAL_ASSET_INDEX[self.type]),
    ))
    world.scene.add_action(ChangeText(
        ref = self._gui_panel_ref,
        child_ref = 'Capacity',
        text = '{}'.format(self.c_capacity)
    ))
    self._gui_update_count(world)



def _gui_update_count(self, world):
    change_blackboard_int(world, self._gui_panel_ref, 'Count', UPDATE_DURATION, self.count)


def gui_pick(self, world, gui_event):
    self._gui_update_count(world)


def gui_reload(self, world, gui_event):
    self._gui_update_count(world)


Material.gui_init = gui_init
Material._gui_update_count = _gui_update_count
Material.gui_pick = gui_pick
Material.gui_reload = gui_reload
