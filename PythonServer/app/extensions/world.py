# -*- coding: utf-8 -*-

# python imports
import math

# project imports
from ..ks.models import World, AgentType, UnitType
from ..ks.commands import Move, PickMaterial, PutMaterial, PickAmmo, PutAmmo
from ..gui_events import GuiEvent, GuiEventType


METHOD = lambda world, side, command: {
    Move.name(): world.bases[side].agents[command.agent_type].move,
    PickMaterial.name(): world.bases[side].agents[command.agent_type].pick_material,
    PutMaterial.name(): world.bases[side].agents[command.agent_type].put_material,
    PickAmmo.name(): world.bases[side].agents[command.agent_type].pick_ammo,
    PutAmmo.name(): world.bases[side].agents[command.agent_type].put_ammo
}.get(command.name())

ARGS = lambda command: {
    Move.name(): \
        lambda command: (command.forward,),
    PickMaterial.name(): \
        lambda command: (command.materials,) if command.agent_type == AgentType.Factory else (),
    PutMaterial.name(): \
        lambda command: (command.desired_ammo,) if command.agent_type == AgentType.Factory else (),
    PickAmmo.name(): \
        lambda command: (command.ammos,) if command.agent_type == AgentType.Warehouse else (),
    PutAmmo.name(): \
        lambda command: ()
}[command.name()](command)


def apply_commands(self, commands):
    gui_events = []

    for side in commands:
        commands_queue = []
        for command in commands[side].values():
            if command.agent_type == AgentType.Warehouse and command.name() == PutMaterial.name() or\
               command.agent_type == AgentType.Factory and command.name() == PutAmmo.name():
                commands_queue.append(command)
            else:
                commands_queue.insert(0, command)

        for command in commands_queue:
            method = METHOD(self, side, command)
            if method is not None:
                args = ARGS(command)
                gui_events.extend(method(self, side, *args))

    return gui_events


def tick(self):
    gui_events = []
    gui_events.extend(self._tick_war())
    gui_events.extend(self._tick_bases())
    return gui_events


def _tick_war(self):
    gui_events = []
    sides = self.bases.keys()
    total_damage = {side: {ut: 0 for ut in list(UnitType)} for side in sides}

    for side in sides:
        for unit in self.bases[side].units.values():
            used_ammo_count = min(unit.num_alives(), unit.ammo_count)
            if used_ammo_count <= 0:
                continue

            unit.reload_rem_time -= 1
            gui_events.append(GuiEvent(GuiEventType.UnitReloading, side=side, unit=unit))
            if unit.reload_rem_time > 0:
                continue

            unit_damage = used_ammo_count * unit.c_individual_damage
            unit_distributed_damage = {}
            for enemy_unit_type, coefficient in unit.c_damage_distribution.items():
                dmg = int(math.ceil(unit_damage * coefficient))
                unit_distributed_damage[enemy_unit_type] = dmg
                total_damage[side][enemy_unit_type] += dmg

            unit.ammo_count -= used_ammo_count
            unit.reload_rem_time = unit.c_reload_duration
            gui_events.append(
                GuiEvent(GuiEventType.UnitFired, side=side, unit=unit,
                         damage=unit_distributed_damage, used_ammo_count=used_ammo_count)
            )

    for side in sides:
        enemy_side = [s for s in sides if s != side][0]
        for unit in self.bases[enemy_side].units.values():
            damage = total_damage[side][unit.type]
            if damage > 0 and unit.health > 0:
                damage = min(damage, unit.health)
                unit.health -= damage
                self.total_healths[enemy_side] -= damage
                gui_events.append(
                    GuiEvent(GuiEventType.UnitDamaged, side=enemy_side, unit=unit, damage=damage)
                )

    return gui_events


def _tick_bases(self):
    gui_events = []

    for side, base in self.bases.items():
        for frontline_delivery in base.frontline_deliveries[:]:
            gui_events.extend(frontline_delivery.tick(self, side))
        gui_events.extend(base.warehouse.tick(self, side))
        gui_events.extend(base.factory.tick(self, side))

    return gui_events


def check_end_game(self, current_cycle):
    return (current_cycle >= self.max_cycles - 1) or (0 in self.total_healths.values())


def get_winner(self):
    # Check if healths are equal
    if len(set(self.total_healths.values())) == 1:
        return None
    # Find side with maximum health
    return max(self.total_healths.keys(), key=(lambda key: self.total_healths[key]))


World.apply_commands = apply_commands
World.tick = tick
World._tick_war = _tick_war
World._tick_bases = _tick_bases
World.check_end_game = check_end_game
World.get_winner = get_winner
