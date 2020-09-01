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
	PickingMaterial = 3
	GoingToBLD = 4


class WarehouseState(enum.Enum):
	Idle = 0
	PickingMaterial = 1
	BringingAmmo = 2
	FullBag = 3
	GoingToBLD = 4
	GoingToFLD = 5


class AI(RealtimeAI):
	def __init__(self, world):
		super(AI, self).__init__(world)
		self.f_state = FactoryState.Idle
		self.ammo_to_make = []
		self.ammo_priority = []
		self.base_ammo_priority = []
		self.normal_ammo_priority = [AmmoType.TankShell, AmmoType.MortarShell, AmmoType.RifleBullet, AmmoType.HMGBullet]
		self.ammo_choice_cnt = {AmmoType.RifleBullet: 0, AmmoType.HMGBullet: 0, AmmoType.MortarShell: 0, AmmoType.TankShell: 0, AmmoType.GoldenTankShell: 0}
		self.max_ammo_choice_cnt = {AmmoType.RifleBullet: 2, AmmoType.HMGBullet: 2, AmmoType.MortarShell: 100, AmmoType.TankShell: 100, AmmoType.GoldenTankShell: 100}
		
		self.w_state = WarehouseState.Idle
		self.rdy_machines = []
		self.picking_scheme = {MaterialType.Powder: 0, MaterialType.Iron: 0, MaterialType.Carbon: 0, MaterialType.Gold: 0, MaterialType.Shell: 0}
		self.base_picking_scheme = {MaterialType.Powder: 0, MaterialType.Iron: 0, MaterialType.Carbon: 0, MaterialType.Gold: 0, MaterialType.Shell: 0}
		
		self.banned_ammo = []
		
		self.specific_ammo = []
		self.numeric_ammo = []
		# state of the game for factory and warehouse agents. True for taking an action, False for making specific
		self.f_normal_specific = False
		self.w_normal_specific = False
		
		self.w_forward = True
		self.f_forward = True
		
		self.unit_ammo = {UnitType.Soldier: AmmoType.RifleBullet, UnitType.Tank: AmmoType.TankShell, UnitType.HeavyMachineGunner: AmmoType.HMGBullet, UnitType.Mortar: AmmoType.MortarShell, UnitType.GoldenTank: AmmoType.GoldenTankShell}
		self.zero_scheme = {MaterialType.Powder: 0, MaterialType.Iron: 0, MaterialType.Carbon: 0, MaterialType.Gold: 0, MaterialType.Shell: 0}
	
		# self.cycle_hp = []
		
	def initialize(self):
		# print('initialize client ai')
		self.ammo_priority = self.normal_ammo_priority.copy()
		self.base_ammo_priority = self.normal_ammo_priority.copy()
		self.base_ammo_priority = self.zero_scheme.copy()
	
	def decide(self):
		base = self.world.bases[self.my_side]
		wagent = base.agents[AgentType.Warehouse]
		fagent = base.agents[AgentType.Factory]
		f_pos = fagent.position
		w_pos = wagent.position
		machines = base.factory.machines
		
		# print(self.w_state)
		# print(self.f_state)
		
		# prediction/calculation
		# if unit type near death, ban ammo type
		# if self.current_cycle == 0:
		# 	if not self.w_normal_specific and not self.f_normal_specific:
		# 		self.make_specific_state(base)
		
		# self.cycle_hp.append([unit.health for unit in self.world.bases[self.my_side].units.values()])
		
		self.check_and_ban_ammo(base)
		
		if self.current_cycle == 0:
			self.make_specific_state(base)
		
		self.factory_agent_handler(base, fagent, f_pos, w_pos, machines)
		
		self.warehouse_agent_handler(base, wagent, w_pos, machines)
	
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
			soldier = unit.type == UnitType.Soldier and (unit.health <= 5 * unit.c_individual_health or unit.ammo_count > 150 or self.ammo_choice_cnt[a_type] == self.max_ammo_choice_cnt[a_type])
			tank = unit.type == UnitType.Tank and unit.health <= 2 * unit.c_individual_health
			hmg = unit.type == UnitType.HeavyMachineGunner and (unit.health <= 2 * unit.c_individual_health or unit.ammo_count > 200 or self.ammo_choice_cnt[a_type] == self.max_ammo_choice_cnt[a_type])
			mortar = unit.type == UnitType.Mortar and unit.health <= 2 * unit.c_individual_health
			gtank = unit.type == UnitType.GoldenTank and unit.health <= 200
			if a_type not in self.banned_ammo:
				if soldier or tank or hmg or mortar or gtank:
					self.banned_ammo.append(a_type)
					if a_type in self.normal_ammo_priority:
						self.normal_ammo_priority.remove(a_type)
						# print("REMOVED", a_type)
	
	def merge_sum_dicts(self, A, B):
		return {x: A.get(x, 0) + B.get(x, 0) for x in set(A).union(B)}
	
	def make_specific_state(self, base):
		self.numeric_ammo = [1, 2, 3, 4]
		self.specific_ammo = [AmmoType(ammo) for ammo in self.numeric_ammo]
		
		scheme_dict = self.zero_scheme.copy()
		for a_type in self.specific_ammo:
			scheme_dict = self.merge_sum_dicts(scheme_dict, base.factory.c_mixture_formulas[a_type])
		self.base_picking_scheme = {x: scheme_dict[x] for x, y in self.base_picking_scheme.items()}
		
		self.base_ammo_priority = self.specific_ammo.copy()
		self.f_normal_specific = True
		self.w_normal_specific = True
	
	def choose_scheme(self, base, pos):
		# TODO ADD POSITION-BASED OPERATION
		# TODO ADD THE PICKING VARIATIONS (LIKE RELOAD COMING) TO SPECIFIC
		if self.w_normal_specific:
			# if pos == Position(0):
			# scheme_dict = self.zero_scheme.copy()
			# for a_type in self.specific_ammo:
			# 	scheme_dict = self.merge_sum_dicts(scheme_dict, base.factory.c_mixture_formulas[a_type])
			# self.base_picking_scheme = {x: scheme_dict[x] for x, y in self.base_picking_scheme.items()}
			# print("I PICKED SCHEME START", self.base_picking_scheme)
			if sum(self.base_picking_scheme.values()) == 0:
				# here, normal_specific should be 0
				pass
			elif sum(self.base_picking_scheme.values()) <= 15:
				self.picking_scheme = self.base_picking_scheme.copy()
			else:
				ammo_to_make = []
				temp = self.specific_ammo.copy()
				scheme_dict = self.zero_scheme.copy()
				i = 0
				if self.numeric_ammo.count(4) == 2:
					scheme_dict = self.merge_sum_dicts(scheme_dict, base.factory.c_mixture_formulas[AmmoType.GoldenTankShell])
					ammo_to_make.append(AmmoType.GoldenTankShell)
					temp.remove(AmmoType.GoldenTankShell)
					i += 1
				for ammo in self.specific_ammo:
					if ((self.numeric_ammo.count(4) == 2 and ammo != AmmoType.GoldenTankShell) or self.numeric_ammo.count(4) < 2) and sum(dict(Counter(scheme_dict) + Counter(base.factory.c_mixture_formulas[ammo])).values()) <= 15:
						scheme_dict = self.merge_sum_dicts(scheme_dict, base.factory.c_mixture_formulas[ammo])
						ammo_to_make.append(ammo)
						temp.remove(ammo)
						i += 1
					if i == 3:
						break
				scheme_dict = {x: scheme_dict[x] for x, y in self.base_picking_scheme.items()}
				self.picking_scheme = {x: scheme_dict[x] for x, y in self.base_picking_scheme.items()}
				# if len(self.ammo_priority) == 0:
				self.ammo_priority = ammo_to_make.copy() + temp.copy()
				self.specific_ammo = ammo_to_make.copy() + temp.copy()
				# print(self.ammo_priority, self.specific_ammo)
			# this whole section tries to fill the picking materials by adding 1 to each
			# print("I PICKED SCHEME BEFORE FILLING", self.picking_scheme)
			while sum(self.picking_scheme.values()) < 15:
				for mat in [base.warehouse.materials[Position(i)] for i in range(5, 0, -1)]:
					if mat.type == MaterialType.Gold and mat.count == 2:
						self.picking_scheme[MaterialType.Gold] = 2
					elif mat.count > 0 and self.picking_scheme[mat.type] <= mat.count:
						self.picking_scheme[mat.type] += 1
						if sum(self.picking_scheme.values()) == 15:
							break
						continue
			# print("I PICKED SCHEME FINAL", self.picking_scheme)
		# elif pos == Position(6):
		# 	pass
		else:
			if all(base.warehouse.materials[Position(i)].count == base.warehouse.materials[Position(i)].c_capacity for i in range(1, 6)):
				scheme_list = [4, 2, 2, 2, 5]
			elif base.warehouse.materials_reload_rem_time < 18 and base.warehouse.materials[Position(4)].count == 0:
				scheme_list = [6, 1, 1, 2, 5]
			elif base.warehouse.materials[Position(4)].count > 0:
				scheme_list = [8 - base.warehouse.materials[Position(4)].count, 1, 1, base.warehouse.materials[Position(4)].count, 5]
			else:
				scheme_list = [8, 1, 1, 0, 5]
			self.picking_scheme = {x: scheme_list[i] for i, (x, y) in enumerate(self.picking_scheme.items())}
			self.base_picking_scheme = self.picking_scheme.copy()
			# print("normal scheme is " + str(self.picking_scheme))
	
	def should_go_for(self, machine):
		pos = machine.position.index
		return machine.status == MachineStatus.AmmoReady or 1 <= machine.construction_rem_time <= (pos - 6 + 1)
	
	# FACTORY AGENT PART
	
	def factory_agent_handler(self, base, fagent, f_pos, w_pos, machines):
		# print("making prio is", self.ammo_priority, self.ammo_to_make, self.f_normal_specific)
		if self.f_state == FactoryState.Idle:
			if f_pos == Position(6):
				self.rdy_machines += [i for i in range(7, 10) if self.should_go_for(machines[Position(i)]) and i not in self.rdy_machines]
				if len(self.rdy_machines) > 0:
					self.f_state = FactoryState.PickingAmmo
					self.f_forward = True
					self.factory_agent_move(self.f_forward)
				elif any(machines[Position(i)].status == MachineStatus.Idle for i in range(7, 10)) and len(self.ammo_priority) > 0:  # any of the machines is idle
					self.f_state = FactoryState.MakingAmmo
			else:
				self.f_forward = False
				self.factory_agent_move(self.f_forward)
		
		elif self.f_state == FactoryState.MakingAmmo:
			if f_pos == Position(6):
				if self.f_normal_specific:
					can_do = True
					for i in range(len(self.picking_scheme.values())):
						if list(base.backline_delivery.materials.values())[i] < list(self.picking_scheme.values())[i]:
							can_do = False
					if not can_do:
						if self.w_state and w_pos.index < 4:
							self.ammo_priority = self.normal_ammo_priority.copy()
							# return
						else:  # maybe change this to wait?
							if f_pos == Position(6) and len(self.ammo_to_make) == 0:
								self.rdy_machines += [i for i in range(7, 10) if self.should_go_for(machines[Position(i)]) and i not in self.rdy_machines]
								if len(self.rdy_machines) > 0:
									self.f_state = FactoryState.PickingAmmo
									self.f_forward = True
									self.factory_agent_move(self.f_forward)
								else:
									self.ammo_priority = self.normal_ammo_priority.copy()
					else:
						self.ammo_priority = self.specific_ammo
				else:
					self.ammo_priority = self.normal_ammo_priority.copy()
					
				picked_up = False
				# Gtank is special, pick it whenever you can.
				a_type = AmmoType.GoldenTankShell
				if self.can_f_pick_mat(fagent, a_type, base) and a_type not in self.ammo_to_make:
					self.factory_agent_pick_material(base.factory.c_mixture_formulas[a_type])
					self.ammo_to_make.append(a_type)
					if a_type in self.ammo_priority:
						self.ammo_priority.remove(a_type)
					if not self.f_normal_specific:
						self.ammo_priority.append(a_type)
					picked_up = True
				if not picked_up:
					for i in range(len(self.ammo_priority)):
						a_type = self.ammo_priority[i]
						if self.can_f_pick_mat(fagent, a_type, base) and any(machines[Position(i)].current_ammo != a_type for i in range(7, 10)):
							self.factory_agent_pick_material(base.factory.c_mixture_formulas[a_type])
							self.ammo_to_make.append(a_type)
							self.ammo_priority.pop(i)
							if not self.f_normal_specific:
								self.ammo_priority.append(a_type)
								self.normal_ammo_priority.pop(i)
								self.normal_ammo_priority.append(a_type)
							picked_up = True
							break
				if not picked_up:
					if len(self.ammo_to_make) > 0:
						self.f_forward = True
						self.factory_agent_move(self.f_forward)
					else:
						self.f_state = FactoryState.Idle
			elif machines[f_pos].status == MachineStatus.AmmoReady:
				self.factory_agent_pick_ammo()
			elif len(self.ammo_to_make) == 0 or all(machines[Position(i)].status != MachineStatus.Idle for i in range(7, 10)):
				if any(machines[Position(i)].status == MachineStatus.AmmoReady for i in range(f_pos.index + 1, 10)):
					self.f_forward = True
					self.factory_agent_move(self.f_forward)
				else:
					self.f_state = FactoryState.GoingToBLD
			elif machines[f_pos].status == MachineStatus.Idle and sum(fagent.materials_bag.values()) > 0 and len(self.ammo_to_make) > 0:
				self.factory_agent_put_material(self.ammo_to_make[0])
				self.ammo_choice_cnt[self.ammo_to_make[0]] += 1
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
				self.ammo_choice_cnt[self.ammo_to_make[0]] += 1
				self.ammo_to_make.pop(0)
			else:
				if self.should_go_for(machines[Position(9)]) or (self.should_go_for(machines[Position(8)]) and f_pos != Position(9)) or (self.should_go_for(machines[Position(7)]) and f_pos == Position(6)):
					self.f_forward = True
				else:
					self.f_forward = False
				self.factory_agent_move(self.f_forward)
		
		elif self.f_state == FactoryState.GoingToBLD:
			if f_pos == Position(6):
				self.factory_agent_put_ammo()
				self.f_state = FactoryState.Idle
				if self.f_normal_specific and len(self.ammo_priority) == 0:
					self.f_normal_specific = False
					self.ammo_priority = self.normal_ammo_priority.copy()
			elif machines[f_pos].status == MachineStatus.AmmoReady:
				self.factory_agent_pick_ammo()
			elif machines[f_pos].status == MachineStatus.Idle and sum(fagent.materials_bag.values()) > 0 and len(self.ammo_to_make) > 0:
				self.factory_agent_put_material(self.ammo_to_make[0])
				self.ammo_choice_cnt[self.ammo_to_make[0]] += 1
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
					self.choose_scheme(base, w_pos)
					self.w_forward = True
					self.warehouse_agent_move(self.w_forward)
				else:
					if base.warehouse.materials_reload_rem_time > 15:
						if self.total_BLD_ammo_count(base) > 0:
							self.w_state = WarehouseState.BringingAmmo
						elif any(self.machine_near_rdy(machines, i, 10) for i in range(7, 10)):
							self.w_state = WarehouseState.GoingToBLD
						self.w_forward = True
						self.warehouse_agent_move(self.w_forward)
			elif w_pos == Position(6):  # BLD
				if self.total_BLD_ammo_count(base):
					self.take_ammo_if_possible(base)
					pass
				else:
					if self.total_warehouse_material_count(base) > 5:
						self.w_state = WarehouseState.PickingMaterial
						self.choose_scheme(base, w_pos)
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
					if sum(self.picking_scheme.values()) <= sum(self.base_picking_scheme.values()):
						self.base_picking_scheme = {x: self.base_picking_scheme[x] - self.picking_scheme[x] for x, y in self.base_picking_scheme.items()}
					else:
						self.base_picking_scheme = self.zero_scheme.copy()
					if self.w_normal_specific and sum(self.base_picking_scheme.values()) == 0:
						self.w_normal_specific = False
						self.ammo_priority = self.normal_ammo_priority.copy()
				elif self.total_BLD_ammo_count(base) > 0:
					self.take_ammo_if_possible(base)
					pass
				# elif self.f_state != FactoryState.MakingAmmo and self.f_state != FactoryState.PickingMaterial:
				# 	pass
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
					if sum(self.picking_scheme.values()) <= sum(self.base_picking_scheme.values()):
						self.base_picking_scheme = {x: self.base_picking_scheme[x] - self.picking_scheme[x] for x, y in self.base_picking_scheme.items()}
					else:
						self.base_picking_scheme = self.zero_scheme.copy()
					if self.w_normal_specific and sum(self.base_picking_scheme.values()) == 0:
						self.w_normal_specific = False
						self.ammo_priority = self.normal_ammo_priority.copy()
				elif self.total_BLD_ammo_count(base) > 0:
					self.take_ammo_if_possible(base)
					pass
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
	
	# def w_handle_phase(self, base):
	# 	if self.w_normal_specific:
	# 		if sum(self.base_picking_scheme.values()) > 15:
	# 			if not self.does_warehouse_satisfy(base):
	# 				self.picking_scheme = self.zero_scheme.copy()
	# 				for pos in range(1, 6):
	# 					mat = base.warehouse.materials[Position(pos)]
	# 					self.picking_scheme[mat.type] = min(mat.count, int(mat.c_capacity / 2))
	# 				while sum(self.picking_scheme.values()) > 15:
	# 					self.picking_scheme[MaterialType.Powder] -= 1
	# 			else:
	# 				self.base_picking_scheme = {x: self.base_picking_scheme[x] - self.picking_scheme[x] for x, y in self.base_picking_scheme.items()}
	# 				if sum(self.base_picking_scheme.values()) < 15:
	# 					for pos in range(1, 6):
	# 						mat = base.warehouse.materials[Position(pos)]
	# 						if self.base_picking_scheme[mat.type] == 0 and mat.count > 0:
	# 							self.base_picking_scheme[mat.type] = min(mat.count, int(mat.c_capacity / 2))
	# 					while sum(self.base_picking_scheme.values()) > 15:
	# 						self.base_picking_scheme[MaterialType.Powder] -= 1
	# 				self.picking_scheme = self.base_picking_scheme.copy()
	# 			print("scheme is", self.picking_scheme)
	# 		else:
	# 			self.w_normal_specific = False
	# 			self.ammo_priority = self.normal_ammo_priority.copy()

	def take_ammo_if_possible(self, base):
		if self.f_state == FactoryState.MakingAmmo or self.f_state == FactoryState.PickingMaterial:
			ammo = {a_type: a_count for a_type, a_count in base.backline_delivery.ammos.items()}
			while sum(ammo.values()) > 5:
				for a_type, cnt in ammo.items():
					if cnt > 1:
						ammo[a_type] -= 1
						if sum(ammo.values()) == 5:
							break
			self.warehouse_agent_pick_ammo(ammo)
			self.w_state = WarehouseState.BringingAmmo
	
	def does_warehouse_satisfy(self, base):
		return any(base.warehouse.materials[Position(pos)].count < self.base_picking_scheme[base.warehouse.materials[Position(pos)].type] for pos in range(1, 6))
	
	def machine_near_rdy(self, machines, i, rem_cycles):
		return machines[Position(i)].status == MachineStatus.Working and machines[Position(i)].construction_rem_time < rem_cycles
	
	# def identify_ban(self, unit, base):
	# 	hp_diff = self.cycle_hp[self.current_cycle][unit.type.value] - self.cycle_hp[self.current_cycle - 30][unit.type.value]
	# 	if unit.type == UnitType.Soldier:
	# 		if hp_diff > 500:
	# 			return True
	# 	elif unit.type == UnitType.Tank:
	# 		pass
	# 	elif unit.type == UnitType.HeavyMachineGunner:
	# 		if hp_diff > 500:
	# 			return True
	# 	elif unit.type == UnitType.Mortar:
	# 		pass
	# 	elif unit.type == UnitType.GoldenTank:
	# 		pass
	# 	return False

# def is_stable_future(self, num_cycles, my_base, op_base):
	# 	# we literally play the game in this function to determine whether in the next "num_cycles" the game is stable!
	# 	dmg_dist = [[x / 10 for x in sub] for sub in [[6, 0, 1, 3, 0], [2, 5, 1, 1, 1], [4, 0, 2, 4, 0], [2, 3, 2, 2, 1], [1, 3, 1, 2, 3]]]
	# 	base_hp = [my_base.units[u_type].c_individual_health for u_type in UnitType]
	# 	base_dmg = [my_base.units[u_type].c_individual_damage for u_type in UnitType]
	# 	max_rem = [my_base.units[u_type].c_reload_duration for u_type in UnitType]
	#
	# 	hp = [my_base.units[u_type].health for u_type in UnitType]
	# 	count = [math.ceil(my_base.units[u_type].health / base_hp[i]) for i, u_type in enumerate(UnitType)]
	# 	ammo = [my_base.units[u_type].ammo_count for u_type in UnitType]
	# 	rem = [my_base.units[u_type].reload_rem_time for u_type in UnitType]
	# 	did_dmg = [False for i in range(5)]
	#
	# 	hp2 = [op_base.units[u_type].health for u_type in UnitType]
	# 	count2 = [math.ceil(op_base.units[u_type].health / base_hp[i]) for i, u_type in enumerate(UnitType)]
	# 	ammo2 = [op_base.units[u_type].ammo_count for u_type in UnitType]
	# 	rem2 = [op_base.units[u_type].reload_rem_time for u_type in UnitType]
	# 	did_dmg2 = [False for i in range(5)]
	#
	# 	if all(ammo[i] == 0 or count[i] == 0 for i in range(5)):
	# 		return False
	#
	# 	for curr_cycle in range(num_cycles):
	# 		taken2 = [0 for i in range(5)]
	# 		taken = [0 for i in range(5)]
	# 		for i in range(5):
	# 			count[i] = math.ceil(hp[i] / base_hp[i])
	# 			count2[i] = math.ceil(hp2[i] / base_hp[i])
	#
	# 		for i in range(5):
	# 			if rem[i] == max_rem[i] and ammo[i] > 0:
	# 				for j in range(5):
	# 					taken2[j] += math.ceil((min(count[i], ammo[i]) * base_dmg[i]) * dmg_dist[i][j])
	# 				ammo[i] = max(ammo[i] - count[i], 0)
	# 				did_dmg[i] = True
	# 			if rem2[i] == max_rem[i] and ammo2[i] > 0:
	# 				for j in range(5):
	# 					taken[j] += math.ceil((min(count2[i], ammo2[i]) * base_dmg[i]) * dmg_dist[i][j])
	# 				ammo2[i] = max(ammo2[i] - count2[i], 0)
	# 				did_dmg2[i] = True
	#
	# 			if i == 2:
	# 				continue
	#
	# 			if did_dmg[i]:
	# 				rem[i] -= 1
	# 				if rem[i] == 0:
	# 					rem[i] = max_rem[i]
	# 					did_dmg[i] = False
	#
	# 			if did_dmg2[i]:
	# 				rem2[i] -= 1
	# 				if rem2[i] == 0:
	# 					rem2[i] = max_rem[i]
	# 					did_dmg2[i] = False
	#
	# 		for i in range(5):
	# 			hp2[i] = max(hp2[i] - taken2[i], 0)
	# 			hp[i] = max(hp[i] - taken[i], 0)
	#
	# 	print("from ", [my_base.units[u_type].health for u_type in UnitType], [op_base.units[u_type].health for u_type in UnitType], [my_base.units[u_type].ammo_count for u_type in UnitType], [op_base.units[u_type].ammo_count for u_type in UnitType])
	# 	print("to", hp, hp2, ammo, ammo2)
	#
	# 	if all(ammo[i] == 0 or count[i] == 0 for i in range(5)) and self.world.total_healths[self.my_side] != 13950 and (len(self.stable_states) == 0 or (len(self.stable_states) > 0 and self.stable_states[-1] - self.current_cycle > 30)):
	# 		self.logger.info("Cycle " + str(self.current_cycle) + " with the range of " + str(num_cycles))
	# 		self.logger.info("  from " + str([my_base.units[u_type].health for u_type in UnitType]) + str([op_base.units[u_type].health for u_type in UnitType]) + str([my_base.units[u_type].ammo_count for u_type in UnitType]) + str([op_base.units[u_type].ammo_count for u_type in UnitType]))
	# 		self.logger.info("  to " + str(hp) + str(hp2) + str(ammo) + str(ammo2))
	# 		self.stable_states.append(self.current_cycle)
	# 		self.num_stable_states += 1
	# 		return True
	# 	return False
