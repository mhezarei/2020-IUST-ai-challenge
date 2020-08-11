# -*- coding: utf-8 -*-

# python imports
import collections
import functools
import itertools
import operator
import random

# chillin imports
from chillin_client import RealtimeAI

from ks.commands import (Move, PickMaterial, PutMaterial, PickAmmo, PutAmmo,
                         CommandAmmoType, CommandAgentType)
# project imports
from ks.models import ECell, AmmoType, AgentType, MachineStatus, Position


class AI(RealtimeAI):

	def __init__(self, world):
		super(AI, self).__init__(world)
		self.stage = 0
		self.batch_sequence = []  # total 9 triple ammos
		self.ammo_materials = []  # total 9 materials for the total 9 triple ammos
		self.current_batch = []  # current triple ammos
		self.current_ammo_mat = {}  # current material for current triple ammos
		self.ammo_mat_cnt = {  # number of total materials required for each ammo type
			0: 3,
			1: 4,
			2: 5,
			3: 3,
			4: 6
		}

	def initialize(self):  # create the 9 batches of triple ammos
		print('initialize')
		base = self.world.bases[self.my_side]
		# THIS PART IS CANCER. TRY TO AVOID READING IT AS MUCH AS POSSIBLE
		while len(self.batch_sequence) < 9:
			batch = list(random.choice(list(set(itertools.product([0, 1, 2, 3, 4], repeat=3)))))
			if sum(self.ammo_mat_cnt[batch[i]] for i in range(3)) > 15:
				continue
			hello = {}
			for ammo in batch:
				ammo_name = AmmoType(int(ammo))
				if ammo_name in hello:
					hi = [hello.get(ammo_name), base.factory.c_mixture_formulas[ammo_name]]
					hello[ammo_name] = dict(functools.reduce(operator.add, map(collections.Counter, hi)))
				else:
					hello[ammo_name] = base.factory.c_mixture_formulas[ammo_name]
			materials = dict(functools.reduce(operator.add, map(collections.Counter, [dct for dct in hello.values()])))
			for ammo, cnt in materials.items():
				if cnt > base.warehouse.materials[Position(ammo.value + 1)].count:
					continue
			self.batch_sequence.append(batch)
			self.ammo_materials.append(materials)

	def decide(self):
		# print('decide')

		base = self.world.bases[self.my_side]
		wagent = base.agents[AgentType.Warehouse]
		fagent = base.agents[AgentType.Factory]

		if self.stage == 0:  # haven't selected a batch to make
			self.current_batch = self.batch_sequence[-1]
			self.batch_sequence.pop()
			self.current_ammo_mat = self.ammo_materials[-1]
			self.ammo_materials.pop()
			self.stage += 1

		elif self.stage == 1:  # select materials for bullets and put them in BLD
			self.warehouse_agent_move(forward=True)
			if base.c_area[wagent.position] == ECell.Material:
				material_type = base.warehouse.materials[wagent.position].type
				if material_type in self.current_ammo_mat.keys() and wagent.materials_bag[material_type] < self.current_ammo_mat[
					material_type]:
					self.warehouse_agent_pick_material()
			elif base.c_area[wagent.position] == ECell.BacklineDelivery:
				self.warehouse_agent_put_material()
				self.stage += 1

		elif self.stage == 2:  # fagent picking material up
			if fagent.position == Position(6):
				self.factory_agent_pick_material(materials=self.current_ammo_mat)
				self.stage += 1
			else:
				self.factory_agent_move(forward=False)

		elif self.stage == 3:  # fagent putting in the first machine
			if fagent.position == Position(7) and base.factory.machines[fagent.position].status == MachineStatus.Idle:
				self.factory_agent_put_material(
					desired_ammo=AmmoType(int(self.current_batch[fagent.position.index - 7])))
				self.stage += 1
			else:
				self.factory_agent_move(forward=True)

		elif self.stage == 4:  # fagent putting in the second machine
			if fagent.position == Position(8) and base.factory.machines[fagent.position].status == MachineStatus.Idle:
				self.factory_agent_put_material(
					desired_ammo=AmmoType(int(self.current_batch[fagent.position.index - 7])))
				self.stage += 1
			else:
				self.factory_agent_move(forward=True)

		elif self.stage == 5:  # fagent putting in the third machine
			if fagent.position == Position(9) and base.factory.machines[fagent.position].status == MachineStatus.Idle:
				self.factory_agent_put_material(
					desired_ammo=AmmoType(int(self.current_batch[fagent.position.index - 7])))
				self.stage += 1
			else:
				self.factory_agent_move(forward=True)

		elif self.stage == 6:  # fagent waiting for the third machine to finish and picking ammo
			if fagent.position == Position(9) and base.factory.machines[fagent.position].status == MachineStatus.AmmoReady:
				self.factory_agent_pick_ammo()
				self.stage += 1

		elif self.stage == 7:  # fagent waiting for the second machine to finish and picking ammo
			if fagent.position == Position(8):
				if base.factory.machines[fagent.position].status == MachineStatus.AmmoReady:
					self.factory_agent_pick_ammo()
					self.stage += 1
			else:
				self.factory_agent_move(forward=False)

		elif self.stage == 8:  # fagent waiting for the first machine to finish and picking ammo
			if fagent.position == Position(7):
				if base.factory.machines[fagent.position].status == MachineStatus.AmmoReady:
					self.factory_agent_pick_ammo()
					self.stage += 1
			else:
				self.factory_agent_move(forward=False)

		elif self.stage == 9:  # fagent putting ammo in BLD
			if fagent.position == Position(6):
				self.factory_agent_put_ammo()
				self.stage += 1
			else:
				self.factory_agent_move(forward=False)

		elif self.stage == 10:  # wagent picking ammo
			ammos = {}
			for ammo, cnt in base.backline_delivery.ammos.items():
				if cnt > 0:
					ammos[ammo] = cnt
			self.warehouse_agent_pick_ammo(ammos=ammos)
			self.stage += 1

		elif self.stage == 11:  # wagent putting ammo in FLD
			if wagent.position == Position(0):
				self.warehouse_agent_put_ammo()
				self.stage = 0
			else:
				self.warehouse_agent_move(forward=False)

	# Warehouse Agent Commands

	def warehouse_agent_move(self, forward):
		self.send_command(Move(agent_type=CommandAgentType.Warehouse, forward=forward))

	def warehouse_agent_pick_material(self):
		self.send_command(PickMaterial(agent_type=CommandAgentType.Warehouse, materials={}))

	def warehouse_agent_put_material(self):
		self.send_command(PutMaterial(agent_type=CommandAgentType.Warehouse, desired_ammo=CommandAmmoType.RifleBullet))

	def warehouse_agent_pick_ammo(self, ammos):
		self.send_command(PickAmmo(agent_type=CommandAgentType.Warehouse, ammos=ammos))

	def warehouse_agent_put_ammo(self):
		self.send_command(PutAmmo(agent_type=CommandAgentType.Warehouse))

	# Factory Agent Commands

	def factory_agent_move(self, forward):
		self.send_command(Move(agent_type=CommandAgentType.Factory, forward=forward))

	def factory_agent_pick_material(self, materials):
		self.send_command(PickMaterial(agent_type=CommandAgentType.Factory, materials=materials))

	def factory_agent_put_material(self, desired_ammo):
		self.send_command(PutMaterial(agent_type=CommandAgentType.Factory, desired_ammo=desired_ammo))

	def factory_agent_pick_ammo(self):
		self.send_command(PickAmmo(agent_type=CommandAgentType.Factory, ammos={}))

	def factory_agent_put_ammo(self):
		self.send_command(PutAmmo(agent_type=CommandAgentType.Factory))
