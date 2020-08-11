# -*- coding: utf-8 -*-

# chillin imports
from chillin_server.gui.scene_actions import InstantiateBundleAsset, ChangeTransform, ChangeSprite, Vector3, Asset
from chillin_server.gui.reference_manager import default_reference_manager as drm

# project imports
from ....ks.models import Agent, AgentType, ECell
from ....gui_events import GuiEventType
from ..constants import LEFT_SIDE
from ..utils import change_animator_state, change_text, change_blackboard_int


def gui_init(self, world, side):
    self._last_gui_event = None
    self._gui_is_idle = True
    self._gui_ref = drm.new()
    cell_offset = self._get_gui_offset(world.bases[side].c_area)

    world.scene.add_action(InstantiateBundleAsset(
        ref = self._gui_ref,
        parent_ref = world.location.ref,
        parent_child_ref = 'Support/{}/AgentPivots'.format(side),
        asset = Asset(bundle_name = 'main', asset_name = 'Agent'),
    ))
    world.scene.add_action(ChangeTransform(
        ref = self._gui_ref,
        position = Vector3(x = cell_offset, y = 0, z = 0),
        change_local = True,
    ))
    if side == LEFT_SIDE:
        world.scene.add_action(ChangeTransform(
            ref = self._gui_ref,
            child_ref = 'Status',
            scale = Vector3(x = -0.01),
            change_local = True,
        ))
    # Status Panel
    self._gui_status = drm.new()
    world.scene.add_action(InstantiateBundleAsset(
        ref = self._gui_status,
        parent_ref = self._gui_ref,
        parent_child_ref = 'Status',
        asset = Asset(bundle_name = 'main', asset_name = '{}AgentPanel'.format(side)),
    ))


def gui_move(self, world, gui_event):
    # [GuiEvent(GuiEventType.Move, side=side, agent=self, forward=forward)]
    self._last_gui_event = gui_event
    cell_offset = self._get_gui_offset(world.bases[LEFT_SIDE].c_area)
    world.scene.add_action(ChangeTransform(
        ref = self._gui_ref,
        duration_cycles = 1,
        position = Vector3(x = cell_offset, y = 0, z = 0),
        change_local = True,
    ))
    world.scene.add_action(ChangeSprite(
        ref = self._gui_ref,
        flip_x = not gui_event.forward,
    ))
    change_animator_state(world, self._gui_ref, 'Walk')


def _get_gui_offset(self, c_area):
    offset = self.position.get_gui_offset()
    if c_area[self.position] == ECell.BacklineDelivery:
        coeff = 1 if self.type == AgentType.Factory else 3
        return offset + c_area[self.position].get_gui_width() * coeff / 4
    else:
        return offset + c_area[self.position].get_gui_width() / 2


def gui_update_status(self, world):
    if self._last_gui_event == None:
        if not self._gui_is_idle:
            change_text(world, self._gui_status, 'LastAction', '-')
            change_animator_state(world, self._gui_ref, 'Idle')
        self._gui_is_idle = True
    else:
        self._gui_is_idle = False
        text = self._last_gui_event.type.name
        if self._last_gui_event.type == GuiEventType.Move:
            text += 'Forward' if self._last_gui_event.forward else 'Backward'
        change_text(world, self._gui_status, 'LastAction', text)

    self._last_gui_event = None


def _gui_update_materials(self, world):
    update_duration = 0.5
    for mat_type, mat_count in self.materials_bag.items():
        change_blackboard_int(world, self._gui_status, 'Materials/{}/Count'.format(mat_type.name), update_duration, mat_count)


def _gui_update_ammos(self, world):
    update_duration = 0.5
    for ammo_type, ammo_count in self.ammos_bag.items():
        change_blackboard_int(world, self._gui_status, 'Ammos/{}/Count'.format(ammo_type.name), update_duration, ammo_count)


Agent.gui_init = gui_init
Agent.gui_move = gui_move
Agent._get_gui_offset = _get_gui_offset
Agent.gui_update_status = gui_update_status
Agent._gui_update_materials = _gui_update_materials
Agent._gui_update_ammos = _gui_update_ammos
