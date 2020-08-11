# -*- coding: utf-8 -*-

# project imports
from app.ks.models import MaterialType, AmmoType, AgentType
from app.ks.commands import Move, PickMaterial, PutMaterial, PickAmmo, PutAmmo


class AI(object):

    def __init__(self, my_side, other_side):
        self.my_side, self.other_side = my_side, other_side
        self._last_commands = None


    def reset_episode(self, world):
        pass


    def decide(self, world):
        self._last_commands = []


    def update(self, world, next_world, events):
        NotImplementedError


    def get_actions(self):
        actions = {}
        for command in self._last_commands:
            actions[command.agent_type] = command
        return actions


    # Warehouse Agent Commands

    def warehouse_agent_move(self, forward):
        self._last_commands.append(Move(agent_type=AgentType.Warehouse, forward=forward))

    def warehouse_agent_pick_material(self):
        self._last_commands.append(PickMaterial(agent_type=AgentType.Warehouse, materials={}))

    def warehouse_agent_put_material(self):
        self._last_commands.append(PutMaterial(agent_type=AgentType.Warehouse, desired_ammo=AmmoType.RifleBullet))

    def warehouse_agent_pick_ammo(self, ammos):
        self._last_commands.append(PickAmmo(agent_type=AgentType.Warehouse, ammos=ammos))

    def warehouse_agent_put_ammo(self):
        self._last_commands.append(PutAmmo(agent_type=AgentType.Warehouse))

    # Factory Agent Commands

    def factory_agent_move(self, forward):
        self._last_commands.append(Move(agent_type=AgentType.Factory, forward=forward))

    def factory_agent_pick_material(self, materials):
        self._last_commands.append(PickMaterial(agent_type=AgentType.Factory, materials=materials))

    def factory_agent_put_material(self, desired_ammo):
        self._last_commands.append(PutMaterial(agent_type=AgentType.Factory, desired_ammo=desired_ammo))

    def factory_agent_pick_ammo(self):
        self._last_commands.append(PickAmmo(agent_type=AgentType.Factory, ammos={}))

    def factory_agent_put_ammo(self):
        self._last_commands.append(PutAmmo(agent_type=AgentType.Factory))
