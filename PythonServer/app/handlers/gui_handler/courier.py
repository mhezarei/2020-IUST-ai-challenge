# -*- coding: utf-8 -*-

# chillin imports
from chillin_server.gui.reference_manager import default_reference_manager as drm
from chillin_server.gui.scene_actions import (InstantiateBundleAsset, ChangeTransform, ChangeRectTransform, \
                                              ChangeIsActive, Asset, Vector2, Destroy)

# project imports
from .utils import change_animator_state, change_text


ARRIVE_DURATION_CYCLES = 2


class Courier:
    def __init__(self, world, side, delivery_duration, pivot,
                 start_position, arrive_position, end_position,
                 is_frontline_delivery, return_duration, ammos = None):

        self._gui_ref = drm.new()

        world.scene.add_action(InstantiateBundleAsset(
            ref = self._gui_ref,
            parent_ref = world.location.ref,
            parent_child_ref = 'Support/{}/{}'.format(side, pivot),
            asset = Asset(bundle_name = 'main', asset_name = '{}Courier'.format(side)),
        ))
        world.scene.add_action(ChangeTransform(
            ref = self._gui_ref,
            position = start_position,
            change_local = True,
        ))
        world.scene.add_action(ChangeTransform(
            ref = self._gui_ref,
            duration_cycles = delivery_duration,
            position = arrive_position,
            change_local = True,
        ))
        world.scene.add_action(ChangeTransform(
            ref = self._gui_ref,
            cycle = delivery_duration + ARRIVE_DURATION_CYCLES,
            duration_cycles = return_duration,
            position = end_position,
            change_local = True,
        ))
        world.scene.add_action(Destroy(
            ref = self._gui_ref,
            cycle = delivery_duration + ARRIVE_DURATION_CYCLES + return_duration,
        ))

        change_animator_state(world, self._gui_ref, 'Arrive', cycle = delivery_duration)
        change_animator_state(world, self._gui_ref, 'Run', cycle = delivery_duration + ARRIVE_DURATION_CYCLES)

        if is_frontline_delivery:
            for ammo_type, ammo_count in ammos.items():
                change_text(world, self._gui_ref, 'Canvas/Ammos/{}/Count'.format(ammo_type.name), str(ammo_count))
        else:
            world.scene.add_action(ChangeIsActive(
                ref = self._gui_ref,
                child_ref = 'Canvas/Ammos',
                is_active = False,
            ))
            world.scene.add_action(ChangeRectTransform(
                ref = self._gui_ref,
                child_ref = 'Canvas',
                size = Vector2(y = 40),
            ))

        self.gui_update_rem_cycles(world, delivery_duration)
        self.gui_update_rem_cycles(world, '-', delivery_duration)


    def gui_update_rem_cycles(self, world, rem_cycles, cycle = None):
        change_text(
            world,
            self._gui_ref,
            'Canvas/RemCycle',
            str(rem_cycles) if type(rem_cycles) is int else rem_cycles,
            cycle = cycle,
        )
