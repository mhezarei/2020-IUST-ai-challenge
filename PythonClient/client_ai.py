# -*- coding: utf-8 -*-

import functools
import operator
import time
from math import ceil
from itertools import groupby, product
from chillin_client import RealtimeAI
from ks.commands import (Move, PickMaterial, PutMaterial, PickAmmo, PutAmmo,
                         CommandAmmoType, CommandAgentType)
from ks.models import ECell, AmmoType, AgentType, MachineStatus, Position, UnitType
import random
import numpy as np
import collections
import logging
from keras.layers.core import Dense


class AI(RealtimeAI):
	def __init__(self, world, counter_games, agent):
		super(AI, self).__init__(world)
		random.seed(time.time())
		self.stage = 0
		self.all_actions = []
		self.curr_action = []  # current triple ammos
		self.current_ammo_mat = {}  # current material for current triple ammos
		self.ammo_mat_cnt = {  # number of total materials required for each ammo type
			0: 3,
			1: 4,
			2: 5,
			3: 3,
			4: 6
		}
		self.game_state = 0
		self.record = []
		self.agent = agent
		self.counter_games = counter_games
		self.logger = None
	
	@staticmethod
	def unit_count(base):
		return [ceil(base.units[UnitType.Soldier].health / base.units[UnitType.Soldier].c_individual_health),
		        ceil(base.units[UnitType.Tank].health / base.units[UnitType.Tank].c_individual_health),
		        ceil(base.units[UnitType.HeavyMachineGunner].health / base.units[
			        UnitType.HeavyMachineGunner].c_individual_health),
		        ceil(base.units[UnitType.Mortar].health / base.units[UnitType.Mortar].c_individual_health),
		        ceil(base.units[UnitType.GoldenTank].health / base.units[UnitType.GoldenTank].c_individual_health)]
	
	@staticmethod
	def ammo_count(base):
		return [base.units[UnitType.Soldier].ammo_count,
		        base.units[UnitType.Tank].ammo_count,
		        base.units[UnitType.HeavyMachineGunner].ammo_count,
		        base.units[UnitType.Mortar].ammo_count,
		        base.units[UnitType.GoldenTank].ammo_count]
	
	@staticmethod
	def get_hp(base):
		return [base.units[UnitType.Soldier].health,
		        base.units[UnitType.Tank].health,
		        base.units[UnitType.HeavyMachineGunner].health,
		        base.units[UnitType.Mortar].health,
		        base.units[UnitType.GoldenTank].health]
	
	def calculate_state(self):
		my_base = self.world.bases[self.my_side]
		op_base = self.world.bases[self.other_side]
		state = self.unit_count(my_base) + self.ammo_count(my_base) + self.get_hp(my_base) + self.unit_count(
			op_base) + self.ammo_count(op_base) + self.get_hp(op_base)
		return state
	
	def get_reward(self, state, next_state):
		# return self.world.total_healths[self.my_side] - self.world.total_healths[self.other_side]
		return sum(state[25:30]) - sum(next_state[25:30])
	
	@staticmethod
	def get_all_actions():
		bro = sorted(list(set(product([i for i in range(5)], repeat=3)))) + sorted(
			list(set(product([i for i in range(5)], repeat=2)))) + sorted(
			list(set(product([i for i in range(5)], repeat=1))))
		bro = [sorted(k) for k in bro]
		bro.sort()
		bro = list(k for k, _ in groupby(bro))
		bro.remove([2, 2, 4])
		bro.remove([1, 4, 4])
		bro.remove([2, 4, 4])
		bro.remove([4, 4, 4])
		return bro
	
	def get_action(self, method, state=None):  # CANCER CODING, PLEASE DON'T READ AS MUCH AS YOU CAN
		temp_method = method
		base = self.world.bases[self.my_side]
		action = []
		while True:
			can_do = True
			if temp_method == 'random':
				action = list(random.choice(self.all_actions))
			elif temp_method == 'predict':
				action = self.all_actions[
					int(np.argmax(self.agent.model.predict(np.array(state).reshape((1, 30)), verbose=1)[0]))]
			hello = {}
			for ammo in action:
				ammo_name = AmmoType(int(ammo))
				if ammo_name in hello:
					hi = [hello.get(ammo_name), base.factory.c_mixture_formulas[ammo_name]]
					hello[ammo_name] = dict(functools.reduce(operator.add, map(collections.Counter, hi)))
				else:
					hello[ammo_name] = base.factory.c_mixture_formulas[ammo_name]
			materials = dict(functools.reduce(operator.add, map(collections.Counter, [dct for dct in hello.values()])))
			for ammo, cnt in materials.items():
				ammo_count = base.warehouse.materials[Position(ammo.value + 1)].count
				ammo_cap = base.warehouse.materials[Position(ammo.value + 1)].c_capacity
				# if i have more materials than the current count or cap
				if cnt > ammo_count or cnt > ammo_cap:
					# it's ok to use it when there is 10 cycles for reload to arrive
					if ammo_count < cnt <= ammo_cap and base.warehouse.materials_reload_rem_time < 20:
						break
					temp_method = 'random'
					can_do = False
					break
			if can_do:
				break
			else:
				continue
		return action, materials
	
	def initialize(self):
		print('initialize random ai')
		self.all_actions = self.get_all_actions()
		logging.basicConfig(filename='random.log', filemode='a', format='%(message)s')
		self.logger = logging.getLogger()
		self.logger.setLevel(logging.INFO)
		self.logger.info('Game Number ' + str(self.counter_games))
	
	def decide(self):
		
		if self.current_cycle == 300 and self.world.total_healths[self.my_side] > self.world.total_healths[
			self.other_side]:
			self.logger.info('    I WON!')
		
		base = self.world.bases[self.my_side]
		wagent = base.agents[AgentType.Warehouse]
		fagent = base.agents[AgentType.Factory]
		
		if self.stage == 0:  # deciding on a triple ammo to make
			# first we assume current cycle is finished (NOT THAT WE BOTH FINISHED CURRENT AMMO)
			# fuck that, we decide beforehand
			# then we define the state only using unit count
			# we have 20 * 10 * 6 * 16 * 4 = 76800 states in total
			if self.game_state == 0:  # decision
				self.record = []
				state = self.calculate_state()
				self.record.append(state)
				if self.counter_games <= 50:
					self.curr_action, self.current_ammo_mat = self.get_action('random')
					self.logger.info(
						"    Chosen Random Action: " + str(self.curr_action) + " at cycle " + str(self.current_cycle))
				else:
					if random.random() < self.agent.epsilon:
						self.curr_action, self.current_ammo_mat = self.get_action('random')
						self.logger.info("    Chosen Random Action: " + str(self.curr_action) + " at cycle " + str(
							self.current_cycle))
					else:
						self.curr_action, self.current_ammo_mat = self.get_action('predict', state)
						self.logger.info("    Chosen Predicted Action: " + str(self.curr_action) + " at cycle " + str(
							self.current_cycle))
				self.record.append(self.curr_action)
				self.game_state = 1
				self.stage += 1
			elif self.game_state == 1:  # we have finished the transition
				self.record = self.record[0:2]
				new_state = self.calculate_state()
				self.record.append(new_state)
				self.record.append(self.get_reward(self.record[0], self.record[2]))
				if self.current_cycle >= self.world.max_cycles or \
						self.world.total_healths[self.my_side] == 0 or \
						self.world.total_healths[self.other_side] == 0:
					self.record.append(1)
				else:
					self.record.append(0)
				
				if len(self.record) == 5 and self.record[4] == 0:
					self.agent.memorize(self.record.copy())
				self.logger.info('    Record is ' + str(self.record))
				self.record = []
				self.game_state = 0
		
		elif self.stage == 1:  # select materials for bullets and put them in BLD
			self.warehouse_agent_move(forward=True)
			if base.c_area[wagent.position] == ECell.Material:
				material_type = base.warehouse.materials[wagent.position].type
				if material_type in self.current_ammo_mat.keys() and wagent.materials_bag[material_type] < \
						self.current_ammo_mat[material_type]:
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
					desired_ammo=AmmoType(int(self.curr_action[fagent.position.index - 7])))
				if len(self.curr_action) == 1:
					self.stage = 7
				self.stage += 1
			else:
				self.factory_agent_move(forward=True)
		
		elif self.stage == 4:  # fagent putting in the second machine
			if fagent.position == Position(8) and base.factory.machines[fagent.position].status == MachineStatus.Idle:
				self.factory_agent_put_material(
					desired_ammo=AmmoType(int(self.curr_action[fagent.position.index - 7])))
				if len(self.curr_action) == 2:
					self.stage = 6
				self.stage += 1
			else:
				self.factory_agent_move(forward=True)
		
		elif self.stage == 5:  # fagent putting in the third machine
			if fagent.position == Position(9) and base.factory.machines[fagent.position].status == MachineStatus.Idle:
				self.factory_agent_put_material(
					desired_ammo=AmmoType(int(self.curr_action[fagent.position.index - 7])))
				self.stage += 1
			else:
				self.factory_agent_move(forward=True)
		
		elif self.stage == 6:  # fagent waiting for the third machine to finish and picking ammo
			if fagent.position == Position(9) and base.factory.machines[
				fagent.position].status == MachineStatus.AmmoReady:
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
	
	# Factory Agent Commands
	
	def warehouse_agent_put_ammo(self):
		self.send_command(PutAmmo(agent_type=CommandAgentType.Warehouse))
	
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

# # -*- coding: utf-8 -*-
#
# import functools
# import operator
# import time
# from math import ceil
# from itertools import groupby, product
# from chillin_client import RealtimeAI
# from ks.commands import (Move, PickMaterial, PutMaterial, PickAmmo, PutAmmo,
#                          CommandAmmoType, CommandAgentType)
# from ks.models import ECell, AmmoType, AgentType, MachineStatus, Position, UnitType
# import random
# import numpy as np
# import collections
# import logging
#
#
# class AI(RealtimeAI):
# 	def __init__(self, world, counter_games, agent):
# 		super(AI, self).__init__(world)
# 		random.seed(time.time())
# 		self.stage = 0
# 		self.all_actions = []
# 		self.curr_action = []  # current triple ammos
# 		self.current_ammo_mat = {}  # current material for current triple ammos
# 		self.ammo_mat_cnt = {  # number of total materials required for each ammo type
# 			0: 3,
# 			1: 4,
# 			2: 5,
# 			3: 3,
# 			4: 6
# 		}
# 		self.game_state = 0
# 		self.record = []
# 		self.agent = agent
# 		self.counter_games = counter_games
# 		self.logger = None
# 		self.records = []
# 		self.pending_record = 0
# 		self.pending_reward = 0
# 		self.pending = False
# 		self.should_decide = True
#
# 	@staticmethod
# 	def unit_count(base):
# 		return [ceil(base.units[UnitType.Soldier].health / base.units[UnitType.Soldier].c_individual_health),
# 		        ceil(base.units[UnitType.Tank].health / base.units[UnitType.Tank].c_individual_health),
# 		        ceil(base.units[UnitType.HeavyMachineGunner].health / base.units[
# 			        UnitType.HeavyMachineGunner].c_individual_health),
# 		        ceil(base.units[UnitType.Mortar].health / base.units[UnitType.Mortar].c_individual_health),
# 		        ceil(base.units[UnitType.GoldenTank].health / base.units[UnitType.GoldenTank].c_individual_health)]
#
# 	@staticmethod
# 	def ammo_count(base):
# 		return [base.units[UnitType.Soldier].ammo_count,
# 		        base.units[UnitType.Tank].ammo_count,
# 		        base.units[UnitType.HeavyMachineGunner].ammo_count,
# 		        base.units[UnitType.Mortar].ammo_count,
# 		        base.units[UnitType.GoldenTank].ammo_count]
#
# 	@staticmethod
# 	def get_hp(base):
# 		return [base.units[UnitType.Soldier].health,
# 		        base.units[UnitType.Tank].health,
# 		        base.units[UnitType.HeavyMachineGunner].health,
# 		        base.units[UnitType.Mortar].health,
# 		        base.units[UnitType.GoldenTank].health]
#
# 	def get_state(self):
# 		my_base = self.world.bases[self.my_side]
# 		op_base = self.world.bases[self.other_side]
# 		state = self.unit_count(my_base) + self.ammo_count(my_base) + self.get_hp(my_base) + self.unit_count(
# 			op_base) + self.ammo_count(op_base) + self.get_hp(op_base)
# 		return state
#
# 	def get_reward(self, state, next_state):
# 		# return self.world.total_healths[self.my_side] - self.world.total_healths[self.other_side]
# 		return sum(state[25:30]) - sum(next_state[25:30])
#
# 	@staticmethod
# 	def get_all_actions():
# 		bro = sorted(list(set(product([i for i in range(5)], repeat=3)))) + sorted(
# 			list(set(product([i for i in range(5)], repeat=2)))) + sorted(
# 			list(set(product([i for i in range(5)], repeat=1))))
# 		bro = [sorted(k) for k in bro]
# 		bro.sort()
# 		bro = list(k for k, _ in groupby(bro))
# 		bro.remove([2, 2, 4])
# 		bro.remove([1, 4, 4])
# 		bro.remove([2, 4, 4])
# 		bro.remove([4, 4, 4])
# 		return bro
#
# 	def get_action(self, method, state=None):  # CANCER CODING, PLEASE DON'T READ AS MUCH AS YOU CAN
# 		temp_method = method
# 		base = self.world.bases[self.my_side]
# 		action = []
# 		while True:
# 			can_do = True
# 			if temp_method == 'random':
# 				action = list(random.choice(self.all_actions))
# 			elif temp_method == 'predict':
# 				pred = self.agent.model.predict(np.array(state).reshape((1, 30)), verbose=1)[0]
# 				action = self.all_actions[int(np.argmax(pred))]
# 			action = [4, 1, 3]
# 			hello = {}
# 			for ammo in action:
# 				ammo_name = AmmoType(int(ammo))
# 				if ammo_name in hello:
# 					hi = [hello.get(ammo_name), base.factory.c_mixture_formulas[ammo_name]]
# 					hello[ammo_name] = dict(functools.reduce(operator.add, map(collections.Counter, hi)))
# 				else:
# 					hello[ammo_name] = base.factory.c_mixture_formulas[ammo_name]
# 			materials = dict(functools.reduce(operator.add, map(collections.Counter, [dct for dct in hello.values()])))
# 			for ammo, cnt in materials.items():
# 				ammo_count = base.warehouse.materials[Position(ammo.value + 1)].count
# 				ammo_cap = base.warehouse.materials[Position(ammo.value + 1)].c_capacity
# 				# if i have more materials than the current count or cap
# 				if cnt > ammo_count or cnt > ammo_cap:
# 					# it's ok to use it when there is 10 cycles for reload to arrive
# 					if ammo_count < cnt <= ammo_cap and base.warehouse.materials_reload_rem_time < 20:
# 						break
# 					temp_method = 'random'
# 					can_do = False
# 					break
# 			if can_do:
# 				break
# 			else:
# 				continue
# 		return action, materials
#
# 	def end_game(self):
# 		return self.current_cycle == self.world.max_cycles
#
# 	def win_condition(self):
# 		return self.end_game() and self.world.total_healths[self.my_side] > self.world.total_healths[self.other_side]
#
# 	def is_stable(self):
# 		base = self.world.bases[self.my_side]
# 		first = all([base.units[u_type].ammo_count == 0 or base.units[u_type].health == 0 for u_type in UnitType]) and len(base.frontline_deliveries) == 0
# 		second = len(base.frontline_deliveries) > 0 and base.frontline_deliveries[0].delivery_rem_time == 1
# 		return ((first and not second) or (not first and second)) and not self.should_decide
#
# 	def get_base_state(self):
# 		return [11, 9, 4, 12, 3, 0, 0, 0, 0, 0, 1570, 4380, 1520, 3520, 2960, 11, 9, 4, 12, 3, 0, 0, 0, 0, 0, 1570, 4380, 1520, 3520, 2960]
#
# 	def get_base_hp(self):
# 		return sum(self.get_base_state()[10:15])
#
# 	def adjust_all_actions(self):
# 		base = self.world.bases[self.my_side]
# 		for i in range(4):
# 			unit = base.units[UnitType(i)]
#
# 	def initialize(self):
# 		print('initialize client ai')
# 		self.all_actions = self.get_all_actions()
# 		logging.basicConfig(filename='client.log', filemode='a', format='%(message)s')
# 		self.logger = logging.getLogger()
# 		self.logger.setLevel(logging.INFO)
# 		self.logger.info('Game Number ' + str(self.counter_games))
#
# 	def decide(self):
#
# 		base = self.world.bases[self.my_side]
# 		wagent = base.agents[AgentType.Warehouse]
# 		fagent = base.agents[AgentType.Factory]
#
# 		if self.end_game():
# 			print(self.records)
#
# 		if self.win_condition():
# 			self.logger.info('    I WON!')
#
# 		# NEW PART
# 		if self.is_stable():
# 			print("this is it " + str(self.current_cycle))
# 			print(self.get_state())
# 			if len(self.records) < self.pending_record + 1:
# 				print("DANGER DANGER DANGER")
# 				print(self.records)
# 			next_state = self.get_state()
# 			self.records[self.pending_record].append(next_state)
# 			self.records[self.pending_record].append(self.world.total_healths[self.other_side] - self.pending_reward)
# 			print("SUCCESSFUL")
# 			print(self.records)
# 			print(self.world.total_healths[self.other_side] - self.pending_reward)
# 			self.pending_record += 1
# 			self.pending = False
# 			self.should_decide = True
# 		# END OF NEW PART
#
# 		# self.adjust_all_actions()
#
# 		if self.stage == 0:  # deciding on a triple ammo to make
# 			# first we assume current cycle is finished (NOT THAT WE BOTH FINISHED CURRENT AMMO)
# 			# fuck that, we decide beforehand
# 			# then we define the state only using unit count
# 			# we have 20 * 10 * 6 * 16 * 4 = 76800 states in total
# 			if self.game_state == 0 :  # decisionش
# 				self.record = []
# 				if self.current_cycle == 0:
# 					self.record.append(self.get_base_state())
# 				else:
# 					self.record.append(self.get_state())
# 				if self.counter_games <= 50:
# 					self.curr_action, self.current_ammo_mat = self.get_action('random')
# 					self.logger.info(
# 						"    Chosen Random Action: " + str(self.curr_action) + " at cycle " + str(self.current_cycle))
# 				# else:
# 				# 	if random.random() < self.agent.epsilon:
# 				# 		self.curr_action, self.current_ammo_mat = self.get_action('random')
# 				# 		self.logger.info("    Chosen Random Action: " + str(self.curr_action) + " at cycle " + str(
# 				# 			self.current_cycle))
# 				# 	else:
# 				# 		self.curr_action, self.current_ammo_mat = self.get_action('predict', state)
# 				# 		self.logger.info("    Chosen Predicted Action: " + str(self.curr_action) + " at cycle " + str(
# 				# 			self.current_cycle))
# 				self.record.append(self.curr_action)
#
# 				# NEW PART
# 				self.records.append(self.record)
# 				if self.current_cycle == 0:
# 					self.pending_reward = self.get_base_hp()
# 				else:
# 					self.pending_reward = self.world.total_healths[self.other_side]
# 				print(self.pending_reward)
# 				print("yo")
# 				self.pending = True
# 				self.should_decide = False
# 				# END OF NEW PART
#
# 				# self.game_state = 1
# 				self.stage += 1
# 			# elif self.game_state == 1:  # we have finished the transition
# 			# 	self.record = self.record[0:2]
# 			# 	new_state = self.calculate_state()
# 			# 	self.record.append(new_state)
# 			# 	self.record.append(self.get_reward(self.record[0], self.record[2]))
# 			# 	if self.current_cycle >= self.world.max_cycles or self.world.total_healths[self.my_side] == 0 or \
# 			# 			self.world.total_healths[self.other_side] == 0:
# 			# 		self.record.append(1)
# 			# 	else:
# 			# 		self.record.append(0)
# 			#
# 			# 	if len(self.record) == 5 and self.record[4] == 0:
# 			# 		self.agent.memorize(self.record.copy())
# 			# 	self.logger.info('    Record is ' + str(self.record))
# 			# 	self.record = []
# 			# 	self.game_state = 0
#
# 		elif self.stage == 1:  # select materials for bullets and put them in BLD
# 			self.warehouse_agent_move(forward=True)
# 			if base.c_area[wagent.position] == ECell.Material:
# 				material_type = base.warehouse.materials[wagent.position].type
# 				if material_type in self.current_ammo_mat.keys() and wagent.materials_bag[material_type] < \
# 						self.current_ammo_mat[material_type]:
# 					self.warehouse_agent_pick_material()
# 			elif base.c_area[wagent.position] == ECell.BacklineDelivery:
# 				self.warehouse_agent_put_material()
# 				self.stage += 1
#
# 		elif self.stage == 2:  # fagent picking material up
# 			if fagent.position == Position(6):
# 				self.factory_agent_pick_material(materials=self.current_ammo_mat)
# 				self.stage += 1
# 			else:
# 				self.factory_agent_move(forward=False)
#
# 		elif self.stage == 3:  # fagent putting in the first machine
# 			if fagent.position == Position(7) and base.factory.machines[fagent.position].status == MachineStatus.Idle:
# 				self.factory_agent_put_material(
# 					desired_ammo=AmmoType(int(self.curr_action[fagent.position.index - 7])))
# 				if len(self.curr_action) == 1:
# 					self.stage = 7
# 				self.stage += 1
# 			else:
# 				self.factory_agent_move(forward=True)
#
# 		elif self.stage == 4:  # fagent putting in the second machine
# 			if fagent.position == Position(8) and base.factory.machines[fagent.position].status == MachineStatus.Idle:
# 				self.factory_agent_put_material(
# 					desired_ammo=AmmoType(int(self.curr_action[fagent.position.index - 7])))
# 				if len(self.curr_action) == 2:
# 					self.stage = 6
# 				self.stage += 1
# 			else:
# 				self.factory_agent_move(forward=True)
#
# 		elif self.stage == 5:  # fagent putting in the third machine
# 			if fagent.position == Position(9) and base.factory.machines[fagent.position].status == MachineStatus.Idle:
# 				self.factory_agent_put_material(
# 					desired_ammo=AmmoType(int(self.curr_action[fagent.position.index - 7])))
# 				self.stage += 1
# 			else:
# 				self.factory_agent_move(forward=True)
#
# 		elif self.stage == 6:  # fagent waiting for the third machine to finish and picking ammo
# 			if fagent.position == Position(9) and base.factory.machines[
# 				fagent.position].status == MachineStatus.AmmoReady:
# 				self.factory_agent_pick_ammo()
# 				self.stage += 1
#
# 		elif self.stage == 7:  # fagent waiting for the second machine to finish and picking ammo
# 			if fagent.position == Position(8):
# 				if base.factory.machines[fagent.position].status == MachineStatus.AmmoReady:
# 					self.factory_agent_pick_ammo()
# 					self.stage += 1
# 			else:
# 				self.factory_agent_move(forward=False)
#
# 		elif self.stage == 8:  # fagent waiting for the first machine to finish and picking ammo
# 			if fagent.position == Position(7):
# 				if base.factory.machines[fagent.position].status == MachineStatus.AmmoReady:
# 					self.factory_agent_pick_ammo()
# 					self.stage += 1
# 			else:
# 				self.factory_agent_move(forward=False)
#
# 		elif self.stage == 9:  # fagent putting ammo in BLD
# 			if fagent.position == Position(6):
# 				self.factory_agent_put_ammo()
# 				self.stage += 1
# 			else:
# 				self.factory_agent_move(forward=False)
#
# 		elif self.stage == 10:  # wagent picking ammo
# 			ammos = {}
# 			for ammo, cnt in base.backline_delivery.ammos.items():
# 				if cnt > 0:
# 					ammos[ammo] = cnt
# 			self.warehouse_agent_pick_ammo(ammos=ammos)
# 			self.stage += 1
#
# 		elif self.stage == 11:  # wagent putting ammo in FLD
# 			if wagent.position == Position(0):
# 				self.warehouse_agent_put_ammo()
# 				self.stage = 0
# 			else:
# 				self.warehouse_agent_move(forward=False)
#
# 	# Warehouse Agent Commands
#
# 	def warehouse_agent_move(self, forward):
# 		self.send_command(Move(agent_type=CommandAgentType.Warehouse, forward=forward))
#
# 	def warehouse_agent_pick_material(self):
# 		self.send_command(PickMaterial(agent_type=CommandAgentType.Warehouse, materials={}))
#
# 	def warehouse_agent_put_material(self):
# 		self.send_command(PutMaterial(agent_type=CommandAgentType.Warehouse, desired_ammo=CommandAmmoType.RifleBullet))
#
# 	def warehouse_agent_pick_ammo(self, ammos):
# 		self.send_command(PickAmmo(agent_type=CommandAgentType.Warehouse, ammos=ammos))
#
# 	# Factory Agent Commands
#
# 	def warehouse_agent_put_ammo(self):
# 		self.send_command(PutAmmo(agent_type=CommandAgentType.Warehouse))
#
# 	def factory_agent_move(self, forward):
# 		self.send_command(Move(agent_type=CommandAgentType.Factory, forward=forward))
#
# 	def factory_agent_pick_material(self, materials):
# 		self.send_command(PickMaterial(agent_type=CommandAgentType.Factory, materials=materials))
#
# 	def factory_agent_put_material(self, desired_ammo):
# 		self.send_command(PutMaterial(agent_type=CommandAgentType.Factory, desired_ammo=desired_ammo))
#
# 	def factory_agent_pick_ammo(self):
# 		self.send_command(PickAmmo(agent_type=CommandAgentType.Factory, ammos={}))
#
# 	def factory_agent_put_ammo(self):
# 		self.send_command(PutAmmo(agent_type=CommandAgentType.Factory))
