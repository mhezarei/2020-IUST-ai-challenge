# -*- coding: utf-8 -*-

# project imports
from .ai import AI
from app.ks.models import ECell, MaterialType, AmmoType, AgentType, MachineStatus


class RebellionAI(AI):

    def __init__(self, my_side, other_side):
        super().__init__(my_side, other_side)


    def reset_episode(self, world):
        self.stage = 0


    def decide(self, world):
        ## Remember not to use the world's properties that are not in your vision! ##
        super().decide(world)

        base = world.bases[self.my_side]
        wagent = base.agents[AgentType.Warehouse]
        fagent = base.agents[AgentType.Factory]

        if self.stage == 0:
            self.warehouse_agent_move(forward=True)
            if base.c_area[wagent.position] == ECell.Material:
                material_type = base.warehouse.materials[wagent.position].type
                if wagent.materials_bag[material_type] == 0:
                    self.warehouse_agent_pick_material()
            elif base.c_area[wagent.position] == ECell.BacklineDelivery:
                self.warehouse_agent_put_material()
                self.stage += 1

        elif self.stage == 1:
            if base.c_area[fagent.position] == ECell.BacklineDelivery:
                required_materials = world.bases[self.my_side].factory.c_mixture_formulas[AmmoType.RifleBullet]
                self.factory_agent_pick_material(materials=required_materials)
                self.stage += 1
            else:
                self.factory_agent_move(forward=False)

        elif self.stage == 2:
            if (    base.c_area[fagent.position] == ECell.Machine and
                    base.factory.machines[fagent.position].status == MachineStatus.Idle):
                self.factory_agent_put_material(desired_ammo=AmmoType.RifleBullet)
                self.stage += 1
            else:
                self.factory_agent_move(forward=True)

        elif self.stage == 3:
            if base.factory.machines[fagent.position].status == MachineStatus.AmmoReady:
                self.factory_agent_pick_ammo()
                self.stage += 1

        elif self.stage == 4:
            if base.c_area[fagent.position] == ECell.BacklineDelivery:
                self.factory_agent_put_ammo()
                self.stage += 1
            else:
                self.factory_agent_move(forward=False)

        elif self.stage == 5:
            self.warehouse_agent_pick_ammo(ammos={AmmoType.RifleBullet: 1})
            self.stage += 1

        elif self.stage == 6:
            if base.c_area[wagent.position] == ECell.FrontlineDelivery:
                self.warehouse_agent_put_ammo()
                self.stage = 0
            else:
                self.warehouse_agent_move(forward=False)


    def update(self, world, next_world, events):
        actions = self.get_actions()
        reward = self._calculate_reward(world, next_world, events)
        # Implement the rest ...


    def _calculate_reward(self, world, next_world, events):
        return 0
