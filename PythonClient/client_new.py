# -*- coding: utf-8 -*-
import enum
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
	PuttingAmmo = 4
	GoingToBLD = 5


class WarehouseState(enum.Enum):
	Idle = 0
	PickingMaterial = 1
	BringingAmmo = 2
	FullBag = 3
	GoingToBLD = 4
	GoingToFLD = 5


def machine_near_rdy(machines, i, rem_cycles):
	return machines[Position(i)].status == MachineStatus.Working and machines[Position(i)].construction_rem_time < rem_cycles


class AI(RealtimeAI):
	def __init__(self, world):
		super(AI, self).__init__(world)
		"""
		FILL IN THE EXPLANATIONS BRO! I LUV YOU BRO!
		"""
		self.f_state = FactoryState.Idle
		self.ammo_to_make = []
		self.ammo_priority = []
		self.base_ammo_priority = []
		self.normal_ammo_priority = [AmmoType.GoldenTankShell, AmmoType.MortarShell, AmmoType.HMGBullet, AmmoType.TankShell, AmmoType.RifleBullet]
		
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
		
		self.unit_ammo = {UnitType.Soldier: AmmoType.RifleBullet, UnitType.Tank: AmmoType.TankShell,
		                  UnitType.HeavyMachineGunner: AmmoType.HMGBullet, UnitType.Mortar: AmmoType.MortarShell,
		                  UnitType.GoldenTank: AmmoType.GoldenTankShell}
		self.zero_scheme = {MaterialType.Powder: 0, MaterialType.Iron: 0, MaterialType.Carbon: 0, MaterialType.Gold: 0, MaterialType.Shell: 0}
	
	def is_future_stable(self):
		pass
	
	def initialize(self):
		print('initialize client ai')
		self.ammo_priority = self.normal_ammo_priority
		self.base_ammo_priority = self.normal_ammo_priority
		self.base_ammo_priority = self.zero_scheme.copy()
	
	def decide(self):
		base = self.world.bases[self.my_side]
		wagent = base.agents[AgentType.Warehouse]
		fagent = base.agents[AgentType.Factory]
		f_pos = fagent.position
		w_pos = wagent.position
		machines = base.factory.machines
		
		print(self.w_state)
		print(self.f_state)
		
		# prediction/calculation
		# if unit type near death, ban ammo type
		# if self.is_stable_future(num_cycles=20):
		# 	self.w_state = WarehouseState.BringingAmmo
		
		self.check_and_ban_ammo(base)
		
		self.make_specific_state(base)
		
		self.factory_agent_handler(base, fagent, f_pos, machines)
		
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
			soldier = unit == UnitType.Soldier and unit.health <= 3 * unit.c_individual_health
			tank = unit == UnitType.Tank and unit.health <= 2 * unit.c_individual_health
			hmg = unit == UnitType.HeavyMachineGunner and unit.health <= unit.c_individual_health
			mortar = unit == UnitType.Mortar and unit.health <= unit.c_individual_health
			gtank = unit == UnitType.GoldenTank and unit.health <= 300
			if a_type not in self.banned_ammo:
				if soldier or tank or hmg or mortar or gtank or unit.health <= unit.c_individual_health:
					self.banned_ammo.append(a_type)
					if a_type in self.normal_ammo_priority:
						self.normal_ammo_priority.remove(a_type)
	
	def merge_sum_dicts(self, A, B):
		return {x: A.get(x, 0) + B.get(x, 0) for x in set(A).union(B)}
	
	def make_specific_state(self, base):
		# TODO MAKE THE PREDICTION THING
		if self.current_cycle == 0:
			# self.numeric_ammo = [2, 3, 4]
			self.numeric_ammo = [2, 3, 3, 4, 4]
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
			print("I PICKED SCHEME START", self.base_picking_scheme)
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
				if len(self.ammo_priority) == 0:
					self.ammo_priority = ammo_to_make.copy() + temp.copy()
					self.specific_ammo = ammo_to_make.copy() + temp.copy()
			# this whole section tries to fill the picking materials by adding 1 to each
			print("I PICKED SCHEME BEFORE FILLING", self.picking_scheme)
			while sum(self.picking_scheme.values()) < 15:
				for mat in [base.warehouse.materials[Position(i)] for i in range(5, 0, -1)]:
					if mat.type == MaterialType.Gold and mat.count == 2:
						self.picking_scheme[MaterialType.Gold] = 2
					elif mat.count > 0 and self.picking_scheme[mat.type] <= mat.count:
						self.picking_scheme[mat.type] += 1
						if sum(self.picking_scheme.values()) == 15:
							break
						continue
			print("I PICKED SCHEME FINAL", self.picking_scheme)
		# elif pos == Position(6):
		# 	pass
		else:
			if all(base.warehouse.materials[Position(i)].count == base.warehouse.materials[Position(i)].c_capacity for i in range(1, 6)):
				scheme_list = [4, 3, 3, 2, 3]
			elif base.warehouse.materials_reload_rem_time < 18 and base.warehouse.materials[Position(4)].count == 0:
				scheme_list = [6, 2, 2, 2, 3]
			elif base.warehouse.materials[Position(4)].count > 0:
				scheme_list = [8 - base.warehouse.materials[Position(4)].count, 2, 2, base.warehouse.materials[Position(4)].count, 3]
			else:
				scheme_list = [8, 2, 2, 0, 3]
			self.picking_scheme = {x: scheme_list[i] for i, (x, y) in enumerate(self.picking_scheme.items())}
			self.base_picking_scheme = self.picking_scheme.copy()
			print("normal scheme is " + str(self.picking_scheme))
	
	def should_go_for(self, machine):
		pos = machine.position.index
		return machine.status == MachineStatus.AmmoReady or 1 <= machine.construction_rem_time <= (pos - 6 + 1)
	
	# FACTORY AGENT PART
	
	def factory_agent_handler(self, base, fagent, f_pos, machines):
		print("making prio is", self.ammo_priority)
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
				if len(self.ammo_to_make) == 0 and self.f_normal_specific:
					can_do = True
					for i in range(len(self.picking_scheme.values())):
						if list(base.backline_delivery.materials.values())[i] < list(self.picking_scheme.values())[i]:
							can_do = False
					if not can_do:
						if self.w_state == WarehouseState.PickingMaterial:
							self.ammo_priority = self.specific_ammo
							return
						else:  # maybe change this to wait?
							if f_pos == Position(6):
								self.rdy_machines += [i for i in range(7, 10) if self.should_go_for(machines[Position(i)]) and i not in self.rdy_machines]
								if len(self.rdy_machines) > 0:
									self.f_state = FactoryState.PickingAmmo
									self.f_forward = True
									self.factory_agent_move(self.f_forward)
								else:
									self.ammo_priority = self.normal_ammo_priority.copy()
					else:
						self.ammo_priority = self.specific_ammo
				picked_up = False
				for i in range(len(self.ammo_priority)):
					a_type = self.ammo_priority[i]
					if self.can_f_pick_mat(fagent, a_type, base) and any(machines[Position(i)].current_ammo != a_type for i in range(7, 10)):
						self.factory_agent_pick_material(base.factory.c_mixture_formulas[a_type])
						self.ammo_to_make.append(a_type)
						self.ammo_priority.pop(i)
						if not self.f_normal_specific:
							self.ammo_priority.append(a_type)
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
				self.f_state = FactoryState.PuttingAmmo
				self.f_forward = False
				self.factory_agent_move(self.f_forward)
			elif machines[f_pos].status == MachineStatus.AmmoReady:
				self.factory_agent_pick_ammo()
				self.rdy_machines.remove(f_pos.index)
			else:
				if self.should_go_for(machines[Position(9)]) or (self.should_go_for(machines[Position(8)]) and f_pos != Position(9)) or (self.should_go_for(machines[Position(7)]) and f_pos == Position(6)):
					self.f_forward = True
				else:
					self.f_forward = False
				self.factory_agent_move(self.f_forward)
		
		elif self.f_state == FactoryState.PuttingAmmo:
			if f_pos == Position(6):
				self.factory_agent_put_ammo()
				self.f_forward = True
				self.f_state = FactoryState.Idle
				if self.f_normal_specific and len(self.ammo_priority) == 0:
					self.f_normal_specific = False
					self.ammo_priority = self.normal_ammo_priority.copy()
			elif machines[f_pos].status == MachineStatus.AmmoReady:
				self.factory_agent_pick_ammo()
			else:
				self.f_forward = False
				self.factory_agent_move(self.f_forward)
		
		elif self.f_state == FactoryState.GoingToBLD:
			if f_pos != Position(6):
				if machines[f_pos].status == MachineStatus.AmmoReady:
					self.factory_agent_pick_ammo()
				else:
					self.f_forward = False
					self.factory_agent_move(self.f_forward)
			else:
				self.f_state = FactoryState.Idle
				self.factory_agent_put_ammo()
				if self.f_normal_specific and len(self.ammo_priority) == 0:
					self.f_normal_specific = False
					self.ammo_priority = self.normal_ammo_priority.copy()
	
	# WAREHOUSE AGENT PART
	
	def warehouse_agent_handler(self, base, wagent, w_pos, machines):
		if self.w_state == WarehouseState.Idle:
			if w_pos == Position(0):  # FLD
				if self.total_warehouse_material_count(base) > 5:
					self.w_state = WarehouseState.PickingMaterial
					# self.w_handle_phase(base)
					# if sum(self.base_picking_scheme.values()) == 0:
					self.choose_scheme(base, w_pos)
					self.w_forward = True
					self.warehouse_agent_move(self.w_forward)
				else:
					if base.warehouse.materials_reload_rem_time > 15:
						if self.total_BLD_ammo_count(base) > 0:
							self.w_state = WarehouseState.BringingAmmo
						elif any(machine_near_rdy(machines, i, 10) for i in range(7, 10)):
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
						# self.w_handle_phase(base)
						# if sum(self.base_picking_scheme.values()) == 0:
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
				elif self.total_BLD_ammo_count(base):
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
					# if self.w_normal_specific:
					# 	self.picking_scheme[base.warehouse.materials[w_pos].type] -= 1
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
				elif self.f_state != FactoryState.MakingAmmo and self.f_state != FactoryState.PickingMaterial:
					pass
				elif self.total_BLD_ammo_count(base):
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
		does_satisfy = True
		for pos in range(1, 6):
			mat = base.warehouse.materials[Position(pos)]
			if mat.count < self.base_picking_scheme[mat.type]:
				does_satisfy = False
				break
		return does_satisfy
	
	def is_stable_future(self, num_cycles):
		# we literally play the game in this function to determine whether in the next "num_cycles" the game is stable!
		dmg_dist = [[x / 10 for x in sub] for sub in [[6, 0, 1, 3, 0], [2, 5, 1, 1, 1], [4, 0, 2, 4, 0], [2, 3, 2, 2, 1], [1, 3, 1, 2, 3]]]
		ammo_size = [75, 5, 150, 10, 2]
		
		
		
		pass
