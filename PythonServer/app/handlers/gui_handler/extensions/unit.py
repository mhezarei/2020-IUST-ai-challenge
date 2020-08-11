# -*- coding: utf-8 -*-

# python imports
import random
import math

# chillin imports
from chillin_server.gui.scene_actions import InstantiateBundleAsset, ChangeTransform, Vector3, Asset
from chillin_server.gui.reference_manager import default_reference_manager as drm

# project imports
from ....ks.models import Unit, UnitType, AmmoType
from ..utils import change_text, change_blackboard_int, change_animator_state, change_audio
from ..constants import LEFT_SIDE


STATUS_UPDATE_DURATION = 0.5
RELOADING_DURATION = {
    UnitType.Soldier: 1,
    UnitType.Tank: 1,
    UnitType.HeavyMachineGunner: 0,
    UnitType.Mortar: 1,
    UnitType.GoldenTank: 2,
}
HAS_PROJECTILE = {
    UnitType.Soldier: False,
    UnitType.Tank: True,
    UnitType.HeavyMachineGunner: False,
    UnitType.Mortar: True,
    UnitType.GoldenTank: True,
}
DIE_SOUND_DURATION = {
    UnitType.Soldier: 1,
    UnitType.Tank: 6,
    UnitType.HeavyMachineGunner: 3,
    UnitType.Mortar: 0.5,
    UnitType.GoldenTank: 6,
}
DIE_DELAY = 0.95
DISAPPEAR_DELAY = 3
DISAPPEAR_DURATION = 1
RELOAD_MAX_DELAY = 0.85
PROJECTILE_FLY_DURATION = 1
PROJECTILE_SOUND_DURATION = 3
SHOOT_DURATION = 1


def gui_init(self, world, side):
    self._gui_shooting_refs = {}  # key is ref, value is (remaining shoot animation cycles, delay only)
    self._gui_alive_refs = []
    gui_alives = random.sample(
        range(world.location.MAX_UNITS[self.type]),
        min(self.num_alives(), world.location.MAX_UNITS[self.type]),
    )

    for i in gui_alives:
        self._gui_alive_refs.append(drm.new())
        world.scene.add_action(InstantiateBundleAsset(
            ref = self._gui_alive_refs[-1],
            parent_ref = world.location.ref,
            parent_child_ref = 'Frontline/{}/{}/{}'.format(side, self.type.name, i),
            asset = Asset(bundle_name = 'main', asset_name = '{}{}'.format(side, self.type.name)),
        ))

    self._gui_update_health(world, side)
    self._gui_update_ammo(world, side)
    self._gui_update_reload_timer(world, side)
    self._gui_update_damage_done(world, side, 0)
    self._gui_update_damage_taken(world, side, 0)


def gui_reloading(self, world, gui_event):
    # GuiEvent(GuiEventType.UnitReloading, side=side, unit=unit)
    if RELOADING_DURATION[self.type] > 0:
        self._gui_update_reload_timer(world, gui_event.side)

        cycles_required = RELOADING_DURATION[self.type] + (SHOOT_DURATION if HAS_PROJECTILE[self.type] else 0)
        if self.reload_rem_time == cycles_required:
            ammo_count = self.ammo_count
            for delivery in world.bases[gui_event.side].frontline_deliveries:
                if delivery.delivery_rem_time < self.reload_rem_time:
                    ammo_type = AmmoType(self.type.value)
                    box_size = world.bases[gui_event.side].factory.c_ammo_box_sizes[ammo_type]
                    ammo_count += delivery.ammos[ammo_type] * box_size

            num_reloading = min(self.num_alives(), ammo_count)

            for ref in self._gui_alive_refs[:num_reloading]:
                delay = random.uniform(0.01, RELOAD_MAX_DELAY)
                self._gui_shooting_refs[ref] = (delay + RELOADING_DURATION[self.type] + SHOOT_DURATION, delay)

                change_animator_state(world, ref, 'Reload', cycle = delay)
                change_audio(world, ref, clip = '{}Shooting'.format(self.type.name), cycle = delay)

        if HAS_PROJECTILE[self.type] and self.reload_rem_time - SHOOT_DURATION == 0:
           # Fire
           for ref, times in self._gui_shooting_refs.items():
                _, delay = times
                change_animator_state(world, ref, 'Shoot', cycle = delay)

                projectile_child_ref = 'XReverse/Projectile' if gui_event.side == LEFT_SIDE else 'Projectile'
                projectile_delay = delay
                change_animator_state(world, ref, 'Shoot', child_ref = projectile_child_ref, cycle = projectile_delay)
                change_audio(world, ref, child_ref = projectile_child_ref, play = True, cycle = projectile_delay)
                change_audio(world, ref, child_ref = projectile_child_ref, play = False, cycle = projectile_delay + PROJECTILE_SOUND_DURATION)


def gui_fired(self, world, gui_event):
    # GuiEvent(GuiEventType.UnitFired, side=side, unit=unit, damage=unit_distributed_damage, used_ammo_count=used_ammo_count)
    self._gui_update_ammo(world, gui_event.side)
    self._gui_update_damage_done(world, gui_event.side, sum(gui_event.damage.values()))
    self._gui_update_damage_done(world, gui_event.side, 0, 1)

    if RELOADING_DURATION[self.type] > 0:
        if not HAS_PROJECTILE[self.type]:
            for ref, times in self._gui_shooting_refs.items():
                _, delay = times

                change_animator_state(world, ref, 'Shoot', cycle = delay)
    else:
        for ref in self._gui_alive_refs[:gui_event.used_ammo_count]:
            if ref not in self._gui_shooting_refs:
                change_audio(world, ref, clip = '{}Shooting'.format(self.type.name))

            self._gui_shooting_refs[ref] = (1.001, 0)
            change_animator_state(world, ref, 'Shoot')


def gui_damaged(self, world, gui_event):
    # GuiEvent(GuiEventType.UnitDamaged, side=enemy_side, unit=unit, damage=damage)
    self._gui_update_health(world, gui_event.side)
    self._gui_update_damage_taken(world, gui_event.side, gui_event.damage)
    self._gui_update_damage_taken(world, gui_event.side, 0, 1)

    if self.num_alives() < len(self._gui_alive_refs):
        for ref in self._gui_alive_refs[self.num_alives():]:
            delay = DIE_DELAY
            if ref in self._gui_shooting_refs:
                rem_cycles, _ = self._gui_shooting_refs[ref]
                if rem_cycles < DIE_DELAY:
                    delay = rem_cycles

                del self._gui_shooting_refs[ref]

            change_animator_state(world, ref, 'Die', cycle = delay)  # Die at end of cycle
            world.scene.add_action(ChangeTransform(
                ref = ref,
                cycle = delay + DISAPPEAR_DELAY,
                duration_cycles = DISAPPEAR_DURATION,
                rotation = Vector3(x=90),
            ))
            world.scene.add_action(ChangeTransform(
                ref = ref,
                cycle = delay + DISAPPEAR_DELAY + DISAPPEAR_DURATION,
                position = Vector3(z=10),
            ))
            change_audio(world, ref, clip = '{}Die'.format(self.type.name), cycle = delay)
            change_audio(world, ref, play = False, cycle = delay + DIE_SOUND_DURATION[self.type])

        self._gui_alive_refs = self._gui_alive_refs[:self.num_alives()]


def gui_update_animator(self, world):
    for ref, times in list(self._gui_shooting_refs.items()):
        rem_cycles, delay = times
        if rem_cycles < 1:
            change_animator_state(world, ref, 'Idle', cycle = rem_cycles)
            change_audio(world, ref, play = False, cycle = rem_cycles)
            del self._gui_shooting_refs[ref]
        else:
            self._gui_shooting_refs[ref] = (rem_cycles - 1, delay)


def gui_ammo_delivered(self, world, gui_event):
    # GuiEvent(GuiEventType.AmmoDelivered, side=side, frontline_delivery=self)
    if gui_event.frontline_delivery.ammos[AmmoType(self.type.value)] > 0:
        self._gui_update_ammo(world, gui_event.side)


def _gui_update_health(self, world, side):
    change_blackboard_int(world, world.location.ref, 'Frontline/{}/StatusCanvas/Panel/{}/TotalHealth'.format(side, self.type.name),
                          STATUS_UPDATE_DURATION, self.health)
    change_blackboard_int(world, world.location.ref, 'Frontline/{}/StatusCanvas/Panel/{}/UnitsCount'.format(side, self.type.name),
                          STATUS_UPDATE_DURATION, self.num_alives())


def _gui_update_ammo(self, world, side):
    change_blackboard_int(world, world.location.ref, 'Frontline/{}/StatusCanvas/Panel/{}/AmmoCount'.format(side, self.type.name),
                          STATUS_UPDATE_DURATION, self.ammo_count)


def _gui_update_reload_timer(self, world, side):
    text = str(self.reload_rem_time) if self.reload_rem_time > 0 else '-'
    change_text(world, world.location.ref, 'Frontline/{}/StatusCanvas/Panel/{}/ReloadRemTime'.format(side, self.type.name), text)


def _gui_update_damage_done(self, world, side, damage, cycle = None):
    text = str(damage) if damage > 0 else '-'
    change_text(world, world.location.ref, 'Frontline/{}/StatusCanvas/Panel/{}/DamageDone'.format(side, self.type.name),
                text, cycle = cycle)


def _gui_update_damage_taken(self, world, side, damage, cycle = None):
    text = str(damage) if damage > 0 else '-'
    change_text(world, world.location.ref, 'Frontline/{}/StatusCanvas/Panel/{}/DamageTaken'.format(side, self.type.name),
                text, cycle = cycle)


Unit.gui_init = gui_init
Unit.gui_reloading = gui_reloading
Unit.gui_fired = gui_fired
Unit.gui_damaged = gui_damaged
Unit.gui_update_animator = gui_update_animator
Unit.gui_ammo_delivered = gui_ammo_delivered
Unit._gui_update_health = _gui_update_health
Unit._gui_update_ammo = _gui_update_ammo
Unit._gui_update_reload_timer = _gui_update_reload_timer
Unit._gui_update_damage_done = _gui_update_damage_done
Unit._gui_update_damage_taken = _gui_update_damage_taken
