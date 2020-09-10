# -*- coding: utf-8 -*-
import enum
import math

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
		self.max_ammo_choice_cnt = {}
		
		self.w_state = WarehouseState.Idle
		self.picking_scheme = {MaterialType.Powder: 0, MaterialType.Iron: 0, MaterialType.Carbon: 0, MaterialType.Gold: 0, MaterialType.Shell: 0}
		
		self.banned_ammo = []
		
		self.w_forward = True
		self.f_forward = True
		
		self.unit_ammo = {UnitType.Soldier: AmmoType.RifleBullet, UnitType.Tank: AmmoType.TankShell, UnitType.HeavyMachineGunner: AmmoType.HMGBullet,
		                  UnitType.Mortar: AmmoType.MortarShell, UnitType.GoldenTank: AmmoType.GoldenTankShell}
		self.zero_scheme = {MaterialType.Powder: 0, MaterialType.Iron: 0, MaterialType.Carbon: 0, MaterialType.Gold: 0, MaterialType.Shell: 0}
		
		self.w_pos = None
		self.f_pos = None
		
		self.map = ""
	
	def initialize(self):
		print('initialize client ai')
	
	def decide(self):
		base = self.world.bases[self.my_side]
		wagent = base.agents[AgentType.Warehouse]
		fagent = base.agents[AgentType.Factory]
		self.f_pos = fagent.position
		self.w_pos = wagent.position
		machines = base.factory.machines
		
		if self.current_cycle == 0:
			self.find_map(base)
		
		self.check_and_ban_ammo(base)
		
		self.factory_agent_handler(base, fagent, machines)
		
		self.warehouse_agent_handler(base, wagent, machines)
		
		# print(self.w_state)
		# print(self.f_state)
	
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
	
	def find_map(self, base):
		count = math.ceil(base.units[UnitType.Soldier].health / base.units[UnitType.Soldier].c_individual_health)
		ammo_count = base.units[UnitType.Soldier].ammo_count
		if count == 19:
			if ammo_count == 100:
				self.map = "WhoNeedsTank"
			elif ammo_count == 50:
				if self.world.max_cycles == 150:
					self.map = "NoTime"
				elif self.world.max_cycles == 300:
					self.map = "AllIn"
					self.max_ammo_choice_cnt = {AmmoType.RifleBullet: 0, AmmoType.TankShell: 3, AmmoType.HMGBullet: 2, AmmoType.MortarShell: 100, AmmoType.GoldenTankShell: 100}
		elif count == 40:
			self.map = "LastStand"
			self.max_ammo_choice_cnt = {AmmoType.RifleBullet: 100, AmmoType.TankShell: 100, AmmoType.HMGBullet: 1, AmmoType.MortarShell: 100, AmmoType.GoldenTankShell: 0}
		elif count == 6:
			self.map = "Artileryyyy"
		elif count == 50:
			self.map = "Ghosts"
		elif count == 10:
			self.map = "PanzerStorm"

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
			soldier = unit.type == UnitType.Soldier and (unit.health <= 3 * unit.c_individual_health or self.ammo_choice_cnt[a_type] >= self.max_ammo_choice_cnt[a_type])
			tank = unit.type == UnitType.Tank and (unit.health <= unit.c_individual_health or self.ammo_choice_cnt[a_type] >= self.max_ammo_choice_cnt[a_type])
			hmg = unit.type == UnitType.HeavyMachineGunner and (unit.health <= unit.c_individual_health or self.ammo_choice_cnt[a_type] >= self.max_ammo_choice_cnt[a_type])
			mortar = unit.type == UnitType.Mortar and (unit.health <= unit.c_individual_health or self.ammo_choice_cnt[a_type] >= self.max_ammo_choice_cnt[a_type])
			gtank = unit.type == UnitType.GoldenTank and unit.health <= 50
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
	
	def can_make_ammo(self, ammo, base, materials, ammo_seq):
		mix = base.factory.c_mixture_formulas[ammo]
		summ = sum(base.factory.c_mixture_formulas[ammo].values())
		for am in ammo_seq:
			summ += sum(base.factory.c_mixture_formulas[am].values())
		if summ > 15:
			return False
		
		answer = ammo not in self.banned_ammo and self.ammo_choice_cnt[ammo] < self.max_ammo_choice_cnt[ammo]
		if not answer:
			return False
		for mat, cnt in mix.items():
			answer = answer and (cnt <= materials[Position(mat.value + 1)].count or (cnt > materials[Position(mat.value + 1)].count and base.warehouse.materials_reload_rem_time < 10))
		return answer

	def choose_possible_ammo(self):
		if self.map == "AllIn":
			return [AmmoType.GoldenTankShell] + [AmmoType.HMGBullet] * self.max_ammo_choice_cnt[AmmoType.HMGBullet] + [AmmoType.MortarShell, AmmoType.RifleBullet, AmmoType.TankShell]
		elif self.map == "LastStand":
			return [AmmoType.HMGBullet] * self.max_ammo_choice_cnt[AmmoType.HMGBullet] + [AmmoType.TankShell, AmmoType.MortarShell, AmmoType.RifleBullet]
	
	def choose_break_cond(self, length):
		if self.map == "AllIn":
			return (self.w_pos == Position(6) and self.current_cycle >= 0 and length == 2) or \
					(self.w_pos == Position(6) and self.current_cycle < 0 and length == 1) or \
					(self.w_pos == Position(0) and (self.current_cycle < 45 or self.current_cycle > 55) and length == 3) or \
					(self.w_pos == Position(0) and 55 >= self.current_cycle >= 45 and length == 3)
		elif self.map == "LastStand":
			return (self.w_pos == Position(6) and self.current_cycle >= 0 and length == 3) or \
			       (self.w_pos == Position(6) and self.current_cycle < 0 and length == 2) or \
			       (self.w_pos == Position(0) and self.current_cycle >= 0 and length == 3) or \
			       (self.w_pos == Position(0) and self.current_cycle < 0 and length == 2)
		
	def predict_ammo_ban(self, cycles, my_base, op_base):
		dmg_dist = [[x / 10 for x in sub] for sub in [[6, 0, 1, 3, 0], [2, 5, 1, 1, 1], [4, 0, 2, 4, 0], [2, 3, 2, 2, 1], [1, 3, 1, 2, 3]]]
		base_hp = [my_base.units[u_type].c_individual_health for u_type in UnitType]
		base_dmg = [my_base.units[u_type].c_individual_damage for u_type in UnitType]
		max_rem = [my_base.units[u_type].c_reload_duration for u_type in UnitType]
		
		hp = [my_base.units[u_type].health for u_type in UnitType]
		count = [math.ceil(my_base.units[u_type].health / base_hp[i]) for i, u_type in enumerate(UnitType)]
		ammo = [my_base.units[u_type].ammo_count for u_type in UnitType]
		rem = [my_base.units[u_type].reload_rem_time for u_type in UnitType]
		
		hp2 = [op_base.units[u_type].health for u_type in UnitType]
		count2 = [math.ceil(op_base.units[u_type].health / base_hp[i]) for i, u_type in enumerate(UnitType)]
		ammo2 = [op_base.units[u_type].ammo_count for u_type in UnitType]
		rem2 = [op_base.units[u_type].reload_rem_time for u_type in UnitType]
		
		for c in range(cycles):
			taken2 = [0] * 5
			taken = [0] * 5
			for i in range(5):
				count[i] = math.ceil(hp[i] / base_hp[i])
				count2[i] = math.ceil(hp2[i] / base_hp[i])
			
			for i in range(5):
				if rem[i] == max_rem[i] and ammo[i] > 0:
					for j in range(5):
						taken2[j] += math.ceil((min(count[i], ammo[i]) * base_dmg[i]) * dmg_dist[i][j])
					ammo[i] = max(ammo[i] - count[i], 0)
				if rem2[i] == max_rem[i] and ammo2[i] > 0:
					for j in range(5):
						taken[j] += math.ceil((min(count2[i], ammo2[i]) * base_dmg[i]) * dmg_dist[i][j])
					ammo2[i] = max(ammo2[i] - count2[i], 0)
				
				if i == 2:
					continue
				
				rem[i] = rem[i] - 1 if rem[i] >= 2 else max_rem[i]
				rem2[i] = rem2[i] - 1 if rem2[i] >= 2 else max_rem[i]
			
			for i in range(5):
				hp2[i] = max(hp2[i] - taken2[i], 0)
				hp[i] = max(hp[i] - taken[i], 0)
		
		for i, unit in enumerate(UnitType):
			if count[i] == 0 and self.unit_ammo[unit] not in self.banned_ammo:
				print("YES BANNED FROM FUTURE IS", unit)
				self.banned_ammo.append(self.unit_ammo[unit])
	
	def choose_predefined(self):
		temp = []
		if self.map == "LastStand":
			if self.current_cycle < 5:
				temp = [AmmoType.RifleBullet, AmmoType.RifleBullet, AmmoType.RifleBullet]
			if 5 < self.current_cycle < 30:
				temp = [AmmoType.MortarShell, AmmoType.RifleBullet, AmmoType.RifleBullet]
			if 30 < self.current_cycle < 50:
				temp = [AmmoType.MortarShell, AmmoType.RifleBullet, AmmoType.RifleBullet]
		
		if self.map == "AllIn":
			if self.current_cycle < 5:
				temp = [AmmoType.GoldenTankShell, AmmoType.HMGBullet, AmmoType.MortarShell]
			if 5 < self.current_cycle < 30:
				temp = [AmmoType.MortarShell, AmmoType.MortarShell, AmmoType.MortarShell]
			if 30 < self.current_cycle < 55:
				temp = [AmmoType.GoldenTankShell, AmmoType.HMGBullet, AmmoType.MortarShell]
				
		if all(ammo not in self.banned_ammo for ammo in temp):
			return temp
		else:
			return []
	
	def choose_scheme(self, base):
		self.predict_ammo_ban(30, base, self.world.bases[self.other_side])
		
		mixture = base.factory.c_mixture_formulas
		ammo_sequence = []
		adjusted_materials = base.warehouse.materials.copy()
		possible_ammo = self.choose_possible_ammo()
		break_cond = False
		
		while True:
			if all(not self.can_make_ammo(ammo, base, adjusted_materials, ammo_sequence) for ammo in possible_ammo):
				break
			for ammo in possible_ammo:
				if self.can_make_ammo(ammo, base, adjusted_materials, ammo_sequence):
					ammo_sequence.append(ammo)
					adjusted_materials = self.sub_dicts(adjusted_materials, mixture[ammo])
					break_cond = self.choose_break_cond(len(ammo_sequence))
					if break_cond:
						break
			if break_cond:
				break
		
		if len(self.choose_predefined()) > 0:
			ammo_sequence = self.choose_predefined()

		scheme = self.zero_scheme.copy()
		for ammo in ammo_sequence:
			scheme = self.merge_sum_dicts(scheme, mixture[ammo])
			self.ammo_choice_cnt[ammo] += 1

		for i, ammo in enumerate([AmmoType.GoldenTankShell, AmmoType.TankShell, AmmoType.MortarShell, AmmoType.RifleBullet, AmmoType.HMGBullet]):
			if ammo in ammo_sequence:
				ammo_sequence.insert(i, ammo_sequence.pop(ammo_sequence.index(ammo)))
		
		self.picking_scheme = scheme.copy()
		if len(ammo_sequence) > 0:
			self.ammo_queue.append(ammo_sequence.copy())
		print("YO GOT THIS", self.picking_scheme)
	
	def should_go_for(self, machine):
		return machine.status == MachineStatus.AmmoReady or 1 <= machine.construction_rem_time <= 6
	
	# FACTORY AGENT PART
	
	def factory_agent_handler(self, base, fagent, machines):
		if self.f_state == FactoryState.Idle:
			self.f_idle(base, fagent, machines)
		elif self.f_state == FactoryState.MakingAmmo:
			self.f_making_ammo(base, fagent, machines)
		elif self.f_state == FactoryState.PickingAmmo:
			self.f_picking_ammo(fagent, machines)
		elif self.f_state == FactoryState.GoingToBLD:
			self.f_going_fld(fagent, machines)
	
	# WAREHOUSE AGENT PART
	
	def warehouse_agent_handler(self, base, wagent, machines):
		if self.w_state == WarehouseState.Idle:
			self.w_idle(base, machines)
		elif self.w_state == WarehouseState.PickingMaterial:
			self.w_picking_material(base, wagent, machines)
		elif self.w_state == WarehouseState.BringingAmmo:
			self.w_going_fld()
		elif self.w_state == WarehouseState.GoingToBLD:
			self.w_going_bld(base, wagent, machines)
		elif self.w_state == WarehouseState.GoingToFLD:
			self.w_going_fld()
	
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
	
	def should_w_wait_in_BLD(self, machines, base):
		return self.f_state == FactoryState.PickingAmmo or (self.total_f_ammo_count(base) > 0) or any(machines[Position(i)].current_ammo == AmmoType.GoldenTankShell and machines[Position(i)].construction_rem_time < 5 for i in range(7, 10))
	
	def f_idle(self, base, fagent, machines):
		if self.f_pos == Position(6):
			self.rdy_machines += [i for i in range(7, 10) if self.should_go_for(machines[Position(i)]) and i not in self.rdy_machines]
			if len(self.rdy_machines) > 0:
				self.f_state = FactoryState.PickingAmmo
				self.factory_agent_move(True)
			elif any(machines[Position(i)].current_ammo == AmmoType.GoldenTankShell and machines[Position(i)].status == MachineStatus.Working and machines[Position(i)].construction_rem_time < 6 for i
			         in range(7, 10)):
				self.f_state = FactoryState.PickingAmmo
				self.factory_agent_move(True)
			elif any(machines[Position(i)].status == MachineStatus.Idle for i in range(7, 10)) and self.total_BLD_material_count(base) > 0:
				self.f_state = FactoryState.MakingAmmo
				self.f_making_ammo(base, fagent, machines)
		else:
			self.factory_agent_move(False)
	
	def f_making_ammo(self, base, fagent, machines):
		if self.f_pos == Position(6):
			if len(self.ammo_queue) > 0:
				for i, a_type in enumerate(self.ammo_queue[0]):
					if self.can_f_pick_mat(fagent, a_type, base):
						self.factory_agent_pick_material(base.factory.c_mixture_formulas[a_type])
						self.ammo_queue[0].pop(i)
						self.ammo_to_make.append(a_type)
						return
			
			if len(self.ammo_to_make) > 0:
				self.factory_agent_move(True)
				if AmmoType.GoldenTankShell in self.ammo_to_make:
					self.ammo_to_make.remove(AmmoType.GoldenTankShell)
					self.ammo_to_make.append(AmmoType.GoldenTankShell)
				self.ammo_queue.pop(0)
			else:
				self.f_state = FactoryState.Idle
				# self.f_idle(base, fagent, machines)
		elif machines[self.f_pos].status == MachineStatus.AmmoReady:
			if machines[self.f_pos].current_ammo == AmmoType.GoldenTankShell:
				self.f_state = FactoryState.GoingToBLD
			self.factory_agent_pick_ammo()
			if self.f_pos.index in self.rdy_machines:
				self.rdy_machines.remove(self.f_pos.index)
		elif len(self.ammo_to_make) == 0 and machines[self.f_pos].status == MachineStatus.Working and machines[self.f_pos].construction_rem_time <= 5:
			self.f_state = FactoryState.PickingAmmo
			self.f_picking_ammo(fagent, machines)
		elif len(self.ammo_to_make) == 0 or all(machines[Position(i)].status != MachineStatus.Idle for i in range(7, 10)):
			if any(machines[Position(i)].status == MachineStatus.AmmoReady for i in range(self.f_pos.index + 1, 10)):
				self.factory_agent_move(True)
			else:
				self.f_state = FactoryState.GoingToBLD
				self.f_going_fld(fagent, machines)
		elif machines[self.f_pos].status == MachineStatus.Idle and sum(fagent.materials_bag.values()) > 0 and len(self.ammo_to_make) > 0:
			self.factory_agent_put_material(self.ammo_to_make[0])
			self.ammo_to_make.pop(0)
		else:
			if self.f_pos == Position(9):
				self.factory_agent_move(False)
			else:
				self.factory_agent_move(True)
	
	def f_picking_ammo(self, fagent, machines):
		self.rdy_machines += [i for i in range(7, 10) if self.should_go_for(machines[Position(i)]) and i not in self.rdy_machines]
		if self.f_pos == Position(6):
			self.factory_agent_move(True)
		elif len(self.rdy_machines) == 0:
			self.f_state = FactoryState.GoingToBLD
			self.factory_agent_move(False)
		elif machines[self.f_pos].status == MachineStatus.AmmoReady:
			if machines[self.f_pos].current_ammo == AmmoType.GoldenTankShell:
				self.f_state = FactoryState.GoingToBLD
			self.factory_agent_pick_ammo()
			if self.f_pos.index in self.rdy_machines:
				self.rdy_machines.remove(self.f_pos.index)
		elif machines[self.f_pos].status == MachineStatus.Idle and sum(fagent.materials_bag.values()) > 0 and len(self.ammo_to_make) > 0:
			self.factory_agent_put_material(self.ammo_to_make[0])
			self.ammo_to_make.pop(0)
		elif machines[self.f_pos].current_ammo == AmmoType.GoldenTankShell and machines[self.f_pos].status == MachineStatus.Working and machines[self.f_pos].construction_rem_time < 5:
			return
		elif len(self.ammo_to_make) == 0 and machines[self.f_pos].status == MachineStatus.Working and machines[self.f_pos].construction_rem_time < 4 and all(machines[Position(i)].status == MachineStatus.Idle or (machines[Position(i)].status == MachineStatus.Working and machines[Position(i)].construction_rem_time > 7) for i in range(7, 10) if i != self.f_pos.index):
			return
		else:
			if self.should_go_for(machines[Position(9)]) or (self.should_go_for(machines[Position(8)]) and self.f_pos != Position(9)) or (self.should_go_for(machines[Position(7)]) and self.f_pos == Position(6)):
				self.factory_agent_move(True)
			else:
				self.factory_agent_move(False)
			
	def f_going_fld(self, fagent, machines):
		if self.f_pos == Position(6):
			self.f_state = FactoryState.Idle
			self.factory_agent_put_ammo()
		elif machines[self.f_pos].status == MachineStatus.AmmoReady:
			self.factory_agent_pick_ammo()
			if self.f_pos.index in self.rdy_machines:
				self.rdy_machines.remove(self.f_pos.index)
		elif len(self.ammo_to_make) == 0 and (fagent.ammos_bag[AmmoType.GoldenTankShell] == 0 and machines[self.f_pos].status == MachineStatus.Working and machines[self.f_pos].construction_rem_time < 5):
			return
		elif machines[self.f_pos].status == MachineStatus.Idle and sum(fagent.materials_bag.values()) > 0 and len(self.ammo_to_make) > 0:
			self.factory_agent_put_material(self.ammo_to_make[0])
			self.ammo_to_make.pop(0)
		else:
			self.factory_agent_move(False)
	
	def w_idle(self, base, machines):
		if self.w_pos == Position(0):
			if self.total_warehouse_material_count(base) > 5:
				self.w_state = WarehouseState.PickingMaterial
				self.choose_scheme(base)
				self.w_forward = True
				self.warehouse_agent_move(self.w_forward)
			else:
				if self.total_BLD_ammo_count(base) > 0:
					self.w_state = WarehouseState.BringingAmmo
				self.w_forward = True
				self.warehouse_agent_move(self.w_forward)
		elif self.w_pos == Position(6):
			if self.f_state != FactoryState.GoingToBLD and self.f_state != FactoryState.Idle and base.backline_delivery.ammos[AmmoType.GoldenTankShell] > 0:
				self.take_ammo(base)
			elif self.should_w_wait_in_BLD(machines, base):
				return
			elif self.total_BLD_ammo_count(base) > 0 and (self.f_state == FactoryState.MakingAmmo or (self.f_state == FactoryState.Idle and self.total_f_ammo_count(base) == 0)):
				self.take_ammo(base)
			else:
				if self.total_warehouse_material_count(base) > 5:
					self.w_state = WarehouseState.PickingMaterial
					self.choose_scheme(base)
					self.w_forward = False
					self.warehouse_agent_move(self.w_forward)
				elif base.warehouse.materials_reload_rem_time <= 15:
					self.w_state = WarehouseState.GoingToFLD
					self.w_forward = False
					self.warehouse_agent_move(self.w_forward)

	def w_picking_material(self, base, wagent, machines):
		if self.w_pos == Position(6):
			if sum(wagent.materials_bag.values()) > 0:
				self.warehouse_agent_put_material()
			elif self.f_state != FactoryState.GoingToBLD and self.f_state != FactoryState.Idle and base.backline_delivery.ammos[AmmoType.GoldenTankShell] > 0:
				self.take_ammo(base)
			elif self.should_w_wait_in_BLD(machines, base):
				return
			elif self.total_BLD_ammo_count(base) > 0 and (self.f_state == FactoryState.MakingAmmo or (self.f_state == FactoryState.Idle and self.total_f_ammo_count(base) == 0)):
				self.take_ammo(base)
			else:
				self.w_state = WarehouseState.Idle
				self.w_idle(base, machines)
		else:
			mat_type = base.warehouse.materials[self.w_pos].type
			if base.warehouse.materials[self.w_pos].count > 0 and wagent.materials_bag[mat_type] < self.picking_scheme[mat_type] and self.can_w_pick_mat(wagent):
				self.warehouse_agent_pick_material()
			elif self.w_pos == Position(1) and not self.w_forward:
				self.w_state = WarehouseState.GoingToBLD
				self.w_forward = True
				self.warehouse_agent_move(self.w_forward)
			else:
				self.warehouse_agent_move(self.w_forward)
	
	def w_going_bld(self, base, wagent, machines):
		if self.w_pos == Position(6):
			if sum(wagent.materials_bag.values()) > 0:
				self.warehouse_agent_put_material()
			elif self.f_state != FactoryState.GoingToBLD and self.f_state != FactoryState.Idle and base.backline_delivery.ammos[AmmoType.GoldenTankShell] > 0:
				self.take_ammo(base)
			elif self.should_w_wait_in_BLD(machines, base):
				return
			elif self.total_BLD_ammo_count(base) > 0 and (self.f_state == FactoryState.MakingAmmo or (self.f_state == FactoryState.Idle and self.total_f_ammo_count(base) == 0)):
				self.take_ammo(base)
			else:
				self.w_state = WarehouseState.Idle
				# self.w_idle(base, machines)
		else:
			self.w_forward = True
			self.warehouse_agent_move(self.w_forward)
	
	def w_going_fld(self):
		if self.w_pos == Position(0):
			self.warehouse_agent_put_ammo()
			self.w_state = WarehouseState.Idle
		else:
			self.w_forward = False
			self.warehouse_agent_move(self.w_forward)
