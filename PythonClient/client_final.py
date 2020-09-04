# -*- coding: utf-8 -*-
import enum
import logging
import math
from collections import Counter

from chillin_client import RealtimeAI
from ks.commands import (Move, PickMaterial, PutMaterial, PickAmmo, PutAmmo,
                         CommandAmmoType, CommandAgentType)
from ks.models import ECell, AmmoType, AgentType, MachineStatus, Position, UnitType, MaterialType


class FactoryState(enum.Enum):
	Idle = 0
	MakingAmmo = 1
	PickingAmmo = 2
	GoingToBLD = 3


class WarehouseState(enum.Enum):
	Idle = 0
	PickingMaterial = 1
	BringingAmmo = 2
	GoingToBLD = 3
	GoingToFLD = 4


class AI(RealtimeAI):
	def __init__(self, world):
		super(AI, self).__init__(world)
		self.f_state = FactoryState.Idle
		self.ammo_to_make = []
		self.rdy_machines = []
		
		self.ammo_queue = []
		
		self.ammo_choice_cnt = {AmmoType.RifleBullet: 0, AmmoType.TankShell: 0, AmmoType.HMGBullet: 0, AmmoType.MortarShell: 0, AmmoType.GoldenTankShell: 0}
		self.max_ammo_choice_cnt = {AmmoType.RifleBullet: 1, AmmoType.TankShell: 5, AmmoType.HMGBullet: 2, AmmoType.MortarShell: 100, AmmoType.GoldenTankShell: 100}
		
		self.w_state = WarehouseState.Idle
		self.picking_scheme = {MaterialType.Powder: 0, MaterialType.Iron: 0, MaterialType.Carbon: 0, MaterialType.Gold: 0, MaterialType.Shell: 0}
		self.picking_ammo = []
		
		self.banned_ammo = []
		
		self.w_forward = True
		self.f_forward = True
		
		self.unit_ammo = {UnitType.Soldier: AmmoType.RifleBullet, UnitType.Tank: AmmoType.TankShell, UnitType.HeavyMachineGunner: AmmoType.HMGBullet,
		                  UnitType.Mortar: AmmoType.MortarShell, UnitType.GoldenTank: AmmoType.GoldenTankShell}
		self.zero_scheme = {MaterialType.Powder: 0, MaterialType.Iron: 0, MaterialType.Carbon: 0, MaterialType.Gold: 0, MaterialType.Shell: 0}
		
		self.w_pos = None
		self.f_pos = None
	
	def initialize(self):
		print('initialize client ai')
	
	def decide(self):
		base = self.world.bases[self.my_side]
		wagent = base.agents[AgentType.Warehouse]
		fagent = base.agents[AgentType.Factory]
		f_pos = fagent.position
		w_pos = wagent.position
		machines = base.factory.machines
		
		if self.current_cycle == 300 or self.world.total_healths[self.my_side] == 0 or self.world.total_healths[self.other_side] == 0:
			print("CLIENT CHOSEN AMMO", self.ammo_choice_cnt)
		
		self.check_and_ban_ammo(base)
		
		self.factory_agent_handler(base, fagent, f_pos, w_pos, machines)
		
		self.warehouse_agent_handler(base, wagent, w_pos, machines)
		
		print(self.w_state)
		print(self.f_state)
	
	# Warehouse Agent Commands
	
	def warehouse_agent_move(self, forward):
		self.send_command(Move(agent_type=CommandAgentType.Warehouse, forward=forward))
	
	def warehouse_agent_pick_material(self):
		self.send_command(PickMaterial(agent_type=CommandAgentType.Warehouse, materials={}))
	
	def warehouse_agent_put_material(self):
		self.send_command(PutMaterial(agent_type=CommandAgentType.Warehouse, desired_ammo=CommandAmmoType.RifleBullet))
	
	def warehouse_agent_put_ammo(self):
		self.send_command(PutAmmo(agent_type=CommandAgentType.Warehouse))
	
	def warehouse_agent_pick_ammo(self, ammos):
		self.send_command(PickAmmo(agent_type=CommandAgentType.Warehouse, ammos=ammos))
	
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
	
	# My functions
	
	def total_warehouse_material_count(self, base):
		return sum(base.warehouse.materials[Position(i)].count for i in range(1, 6))
	
	def total_BLD_ammo_count(self, base):
		return sum(base.backline_delivery.ammos.values())
	
	def can_w_pick_mat(self, wagent):
		return sum(wagent.materials_bag.values()) < wagent.c_materials_bag_capacity
	
	def can_f_pick_mat(self, fagent, ammo_type, base):
		bld_mat = base.backline_delivery.materials
		new_dict = {**bld_mat, **base.factory.c_mixture_formulas[ammo_type]}
		can_do = True
		for i in range(len(new_dict.values())):
			if list(new_dict.values())[i] > list(bld_mat.values())[i]:
				can_do = False
		return can_do and sum(base.factory.c_mixture_formulas[ammo_type].values()) + sum(fagent.materials_bag.values()) <= fagent.c_materials_bag_capacity
	
	def check_and_ban_ammo(self, base):
		for unit in base.units.values():
			a_type = self.unit_ammo[unit.type]
			soldier = unit.type == UnitType.Soldier and (unit.health <= 5 * unit.c_individual_health or self.ammo_choice_cnt[a_type] >= self.max_ammo_choice_cnt[a_type])
			tank = unit.type == UnitType.Tank and unit.health <= unit.c_individual_health
			hmg = unit.type == UnitType.HeavyMachineGunner and (unit.health <= 2 * unit.c_individual_health or self.ammo_choice_cnt[a_type] >= self.max_ammo_choice_cnt[a_type])
			mortar = unit.type == UnitType.Mortar and (unit.health <= unit.c_individual_health or self.ammo_choice_cnt[a_type] >= self.max_ammo_choice_cnt[a_type])
			gtank = unit.type == UnitType.GoldenTank and unit.health <= 200
			if a_type not in self.banned_ammo and (soldier or tank or hmg or mortar or gtank):
				self.banned_ammo.append(a_type)
				print("REMOVED", a_type)
	
	def merge_sum_dicts(self, A, B):
		return {x: A.get(x, 0) + B.get(x, 0) for x in set(A).union(B)}
	
	def sub_dicts(self, A, B):
		temp = A.copy()
		for mat in B.keys():
			temp[Position(mat.value + 1)].count -= B[mat]
		return temp
	
	def can_make_ammo(self, ammo, base, materials):
		answer = ammo not in self.banned_ammo and self.ammo_choice_cnt[ammo] < self.max_ammo_choice_cnt[ammo]
		mix = base.factory.c_mixture_formulas[ammo]
		
		for i in range(1, 6):
			if materials[Position(i)].type in list(mix.keys()) and materials[Position(i)].count < mix[materials[Position(i)].type]:
				answer = False
		
		if ammo == AmmoType.GoldenTankShell:
			answer = answer and (materials[Position(4)].count == 2 or (materials[Position(4)].count < 2 and base.warehouse.materials_reload_rem_time < 18))
		
		return answer
	
	def choose_scheme(self, base):
		scheme = self.zero_scheme.copy()
		mixture = base.factory.c_mixture_formulas
		ammo_sequence = []
		adjusted_materials = base.warehouse.materials.copy()
		possible_ammo = [AmmoType.GoldenTankShell, AmmoType.MortarShell, AmmoType.HMGBullet, AmmoType.RifleBullet, AmmoType.TankShell]
		
		while len(ammo_sequence) < 3:
			if all(not self.can_make_ammo(ammo, base, adjusted_materials) for ammo in possible_ammo):
				break
			for ammo in possible_ammo:
				if self.can_make_ammo(ammo, base, adjusted_materials):
					scheme = self.merge_sum_dicts(scheme, mixture[ammo])
					ammo_sequence.append(ammo)
					self.ammo_choice_cnt[ammo] += 1
					adjusted_materials = self.sub_dicts(adjusted_materials, mixture[ammo])
					print("PICKED THIS AMMO TO MAKE", ammo)
				if len(ammo_sequence) == 3:
					break
		
		self.picking_scheme = scheme.copy()
		self.ammo_queue.append(ammo_sequence.copy())
		self.picking_ammo = ammo_sequence.copy()
		print("I CHOOSE THIS SCHEME", self.picking_scheme)
	
	def should_go_for(self, machine):
		# pos = machine.position.index
		return machine.status == MachineStatus.AmmoReady or 1 <= machine.construction_rem_time <= 8
	
	# FACTORY AGENT PART
	
	def factory_agent_handler(self, base, fagent, f_pos, w_pos, machines):
		if self.f_state == FactoryState.Idle:
			if f_pos == Position(6):
				self.rdy_machines += [i for i in range(7, 10) if self.should_go_for(machines[Position(i)]) and i not in self.rdy_machines]
				if len(self.rdy_machines) > 0:
					self.f_state = FactoryState.PickingAmmo
					self.f_forward = True
					self.factory_agent_move(self.f_forward)
				elif any(machines[Position(i)].status == MachineStatus.Idle for i in range(7, 10)) and self.total_BLD_material_count(base):  # any of the machines is idle
					self.f_state = FactoryState.MakingAmmo
			else:
				self.f_forward = False
				self.factory_agent_move(self.f_forward)
		
		elif self.f_state == FactoryState.MakingAmmo:
			if f_pos == Position(6):
				if len(self.ammo_queue) > 0:
					for i, a_type in enumerate(self.ammo_queue[0]):
						if self.can_f_pick_mat(fagent, a_type, base):
							self.factory_agent_pick_material(base.factory.c_mixture_formulas[a_type])
							self.ammo_queue[0].pop(i)
							self.ammo_to_make.append(a_type)
							return
				
				if len(self.ammo_to_make) > 0:
					self.f_forward = True
					self.factory_agent_move(self.f_forward)
					self.ammo_queue.pop(0)
				else:
					self.f_state = FactoryState.Idle
			elif machines[f_pos].status == MachineStatus.AmmoReady:
				self.factory_agent_pick_ammo()
			elif len(self.ammo_to_make) == 0 and machines[f_pos].status == MachineStatus.Working and machines[f_pos].construction_rem_time <= 6:
				return
			elif len(self.ammo_to_make) == 0 or all(machines[Position(i)].status != MachineStatus.Idle for i in range(7, 10)):
				if any(machines[Position(i)].status == MachineStatus.AmmoReady for i in range(f_pos.index + 1, 10)):
					self.f_forward = True
					self.factory_agent_move(self.f_forward)
				else:
					self.f_state = FactoryState.GoingToBLD
			elif machines[f_pos].status == MachineStatus.Idle and sum(fagent.materials_bag.values()) > 0 and len(self.ammo_to_make) > 0:
				self.factory_agent_put_material(self.ammo_to_make[0])
				self.ammo_to_make.pop(0)
			else:
				if f_pos == Position(9):
					self.f_forward = False
				else:
					self.f_forward = True
				self.factory_agent_move(self.f_forward)
		
		elif self.f_state == FactoryState.PickingAmmo:
			self.rdy_machines += [i for i in range(7, 10) if self.should_go_for(machines[Position(i)]) and i not in self.rdy_machines]
			if f_pos == Position(6):
				self.f_forward = True
				self.factory_agent_move(self.f_forward)
			elif len(self.rdy_machines) == 0:
				self.f_state = FactoryState.GoingToBLD
				self.f_forward = False
				self.factory_agent_move(self.f_forward)
			elif machines[f_pos].status == MachineStatus.AmmoReady:
				self.factory_agent_pick_ammo()
				self.rdy_machines.remove(f_pos.index)
			elif machines[f_pos].status == MachineStatus.Idle and sum(fagent.materials_bag.values()) > 0 and len(self.ammo_to_make) > 0:
				self.factory_agent_put_material(self.ammo_to_make[0])
				self.ammo_to_make.pop(0)
			else:
				if self.should_go_for(machines[Position(9)]) or (self.should_go_for(machines[Position(8)]) and f_pos != Position(9)) or (self.should_go_for(machines[Position(7)]) and f_pos == Position(6)):
					self.f_forward = True
				else:
					self.f_forward = False
				self.factory_agent_move(self.f_forward)
		
		elif self.f_state == FactoryState.GoingToBLD:
			if f_pos == Position(6):
				self.f_state = FactoryState.Idle
				self.factory_agent_put_ammo()
			elif machines[f_pos].status == MachineStatus.AmmoReady:
				self.factory_agent_pick_ammo()
			elif len(self.ammo_to_make) == 0 and machines[f_pos].status == MachineStatus.Working and machines[f_pos].construction_rem_time <= 6:
				return
			elif machines[f_pos].status == MachineStatus.Idle and sum(fagent.materials_bag.values()) > 0 and len(self.ammo_to_make) > 0:
				self.factory_agent_put_material(self.ammo_to_make[0])
				self.ammo_to_make.pop(0)
			else:
				self.f_forward = False
				self.factory_agent_move(self.f_forward)
	
	# WAREHOUSE AGENT PART
	
	def warehouse_agent_handler(self, base, wagent, w_pos, machines):
		if self.w_state == WarehouseState.Idle:
			if w_pos == Position(0):  # FLD
				if self.total_warehouse_material_count(base) > 5:
					self.w_state = WarehouseState.PickingMaterial
					self.choose_scheme(base)
					self.w_forward = True
					self.warehouse_agent_move(self.w_forward)
				else:
					if base.warehouse.materials_reload_rem_time > 15:
						if self.total_BLD_ammo_count(base) > 0:
							self.w_state = WarehouseState.BringingAmmo
						# elif any(self.machine_near_rdy(machines, i, 10) for i in range(7, 10)):
						# 	self.w_state = WarehouseState.GoingToBLD
						self.w_forward = True
						self.warehouse_agent_move(self.w_forward)
			elif w_pos == Position(6):  # BLD
				if self.f_state == FactoryState.PickingAmmo or (self.total_f_ammo_count(base) > 0):
					return
				elif self.total_BLD_ammo_count(base) > 0 and (self.f_state == FactoryState.MakingAmmo or (self.f_state == FactoryState.Idle and self.total_f_ammo_count(base) == 0)):
					self.take_ammo(base)
					return
				else:
					if self.total_warehouse_material_count(base) > 5:
						self.w_state = WarehouseState.PickingMaterial
						self.choose_scheme(base)
						self.w_forward = False
						self.warehouse_agent_move(self.w_forward)
					else:
						if base.warehouse.materials_reload_rem_time <= 15:
							self.w_state = WarehouseState.GoingToFLD
							self.w_forward = False
							self.warehouse_agent_move(self.w_forward)
		
		elif self.w_state == WarehouseState.PickingMaterial:
			if w_pos == Position(6):
				if sum(wagent.materials_bag.values()) > 0:
					self.warehouse_agent_put_material()
				elif self.f_state == FactoryState.PickingAmmo or (self.total_f_ammo_count(base) > 0):
					return
				elif self.total_BLD_ammo_count(base) > 0 and (self.f_state == FactoryState.MakingAmmo or (self.f_state == FactoryState.Idle and self.total_f_ammo_count(base) == 0)):
					self.take_ammo(base)
				else:
					self.w_state = WarehouseState.Idle
			else:
				mat_type = base.warehouse.materials[w_pos].type
				if base.warehouse.materials[w_pos].count > 0 and wagent.materials_bag[mat_type] < self.picking_scheme[mat_type] and self.can_w_pick_mat(wagent):
					self.warehouse_agent_pick_material()
				elif w_pos == Position(1) and not self.w_forward:
					self.w_state = WarehouseState.GoingToBLD
					self.w_forward = True
					self.warehouse_agent_move(self.w_forward)
				else:
					self.warehouse_agent_move(self.w_forward)
		
		elif self.w_state == WarehouseState.BringingAmmo:
			if w_pos == Position(0):
				self.warehouse_agent_put_ammo()
				self.w_state = WarehouseState.Idle
			else:
				self.w_forward = False
				self.warehouse_agent_move(self.w_forward)
		
		elif self.w_state == WarehouseState.GoingToBLD:
			if w_pos == Position(6):
				if sum(wagent.materials_bag.values()) > 0:
					self.warehouse_agent_put_material()
				elif self.f_state == FactoryState.PickingAmmo or (self.total_f_ammo_count(base) > 0):
					return
				elif self.total_BLD_ammo_count(base) > 0 and (self.f_state == FactoryState.MakingAmmo or (self.f_state == FactoryState.Idle and self.total_f_ammo_count(base) == 0)):
					self.take_ammo(base)
				else:
					self.w_state = WarehouseState.Idle
			else:
				self.w_forward = True
				self.warehouse_agent_move(self.w_forward)
		
		elif self.w_state == WarehouseState.GoingToFLD:
			if w_pos == Position(0):
				self.warehouse_agent_put_ammo()
				self.w_state = WarehouseState.Idle
			else:
				self.w_forward = False
				self.warehouse_agent_move(self.w_forward)
	
	def take_ammo(self, base):
		ammo = {a_type: a_count for a_type, a_count in base.backline_delivery.ammos.items()}
		while sum(ammo.values()) > 5:
			for a_type, cnt in ammo.items():
				if cnt > 1:
					ammo[a_type] -= 1
					if sum(ammo.values()) == 5:
						break
		self.warehouse_agent_pick_ammo(ammo)
		self.w_state = WarehouseState.BringingAmmo
	
	def total_BLD_material_count(self, base):
		return sum(base.backline_delivery.materials.values())
	
	def total_f_ammo_count(self, base):
		return sum(base.agents[AgentType.Factory].ammos_bag.values())
	
	def should_w_wait_in_BLD(self, machines):
		waiting = False
		for ammo in self.picking_ammo:
			if ammo == AmmoType.RifleBullet or ammo == AmmoType.HMGBullet:
				waiting = True
				break
		return self.f_state != FactoryState.MakingAmmo or waiting
