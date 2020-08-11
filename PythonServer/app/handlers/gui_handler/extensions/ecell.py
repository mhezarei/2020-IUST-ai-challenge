# -*- coding: utf-8 -*-

# chillin imports
from chillin_server.gui.scene_actions import InstantiateBundleAsset, ChangeTransform, Vector3, Asset
from chillin_server.gui.reference_manager import default_reference_manager as drm

# project imports
from ....ks.models import ECell
from ..constants import LEFT_SIDE
from ..utils import change_text


GUI_WIDTH = {
    ECell.Empty: 2,
    ECell.FrontlineDelivery: 2,
    ECell.Material: 2,
    ECell.BacklineDelivery: 3,
    ECell.Machine: 3,
}


def gui_init(self, world, side, position):
    cell_ref = drm.new()
    panel_ref = drm.new()
    cell_offset = position.get_gui_offset()

    # Create cell
    world.scene.add_action(InstantiateBundleAsset(
        ref = cell_ref,
        parent_ref = world.location.ref,
        parent_child_ref = 'Support/{}/CellPivots'.format(side),
        asset = Asset(bundle_name = 'main', asset_name = '{}Cell'.format(self.name)),
    ))
    world.scene.add_action(ChangeTransform(
        ref = cell_ref,
        position = Vector3(x = cell_offset, y = 0, z = 0),
        change_local = True,
    ))

    # Create panel
    panel_asset = '{}Panel'.format(self.name)
    if self == ECell.BacklineDelivery:
        panel_asset = '{}{}Panel'.format(side, self.name)

    world.scene.add_action(InstantiateBundleAsset(
        ref = panel_ref,
        parent_ref = world.location.ref,
        parent_child_ref = 'Support/{}/PanelPivots'.format(side),
        asset = Asset(bundle_name = 'main', asset_name = panel_asset),
    ))
    panel_extra_offset = self.get_gui_width() * 100 if side == LEFT_SIDE else 0
    panel_scale = Vector3(x = -1) if side == LEFT_SIDE else None
    world.scene.add_action(ChangeTransform(
        ref = panel_ref,
        position = Vector3(x = cell_offset * 100 + panel_extra_offset, y = 0, z = 0),
        scale = panel_scale,
        change_local = True,
    ))
    change_text(world, panel_ref, 'CellIndex', 'Position: {}'.format(position.index))

    return cell_ref, panel_ref


def get_gui_width(self):
    return GUI_WIDTH[self]


ECell.gui_init = gui_init
ECell.get_gui_width = get_gui_width
