# -*- coding: utf-8 -*-

import functools
import operator
from math import ceil
import itertools
from chillin_client import RealtimeAI
from ks.commands import (Move, PickMaterial, PutMaterial, PickAmmo, PutAmmo,
                         CommandAmmoType, CommandAgentType)
from ks.models import ECell, AmmoType, AgentType, MachineStatus, Position, UnitType
import random
import numpy as np
import collections
import logging


class AI(RealtimeAI):
	def __init__(self, world, counter_games, agent):
		super(AI, self).__init__(world)
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
	
	def get_reward(self, state, next_state):  # total dmg done in one transition
		# return self.world.total_healths[self.my_side] - self.world.total_healths[self.other_side]
		return self.get_total_dmg(state, next_state)
	
	@staticmethod
	def get_total_dmg(state, next_state):
		return sum(state[25:30]) - sum(next_state[25:30])
	
	def get_action(self, method, state=None):  # CANCER CODING, PLEASE DON'T READ AS MUCH AS YOU CAN
		base = self.world.bases[self.my_side]
		action = []
		materials = {}
		while True:
			if method == 'random':
				action = list(random.choice(self.all_actions))
			elif method == 'predict':
				action = list(map(int, self.agent.model.predict(np.array(state).reshape((1, 30)))[0]))
				action = self.all_actions[int(np.argmax(action))]
			if sum(self.ammo_mat_cnt[action[i]] for i in range(len(action))) > 15:
				continue
			hello = {}
			for ammo in action:
				ammo_name = AmmoType(int(ammo))
				if ammo_name in hello:
					hi = [hello.get(ammo_name), base.factory.c_mixture_formulas[ammo_name]]
					hello[ammo_name] = dict(functools.reduce(operator.add, map(collections.Counter, hi)))
				else:
					hello[ammo_name] = base.factory.c_mixture_formulas[ammo_name]
			materials = dict(
				functools.reduce(operator.add, map(collections.Counter, [dct for dct in hello.values()])))
			for ammo, cnt in materials.items():
				if cnt > base.warehouse.materials[Position(ammo.value + 1)].count:
					continue
			break
		return action, materials
	
	def initialize(self):
		print('initialize client ai')
		self.all_actions = sorted(list(set(itertools.product([i for i in range(5)], repeat=3)))) + sorted(
			list(set(itertools.product([i for i in range(5)], repeat=2)))) + sorted(
			list(set(itertools.product([i for i in range(5)], repeat=1))))
		# self.agent.epsilon = 1 - (self.counter_games * self.agent.decay_rate)
		logging.basicConfig(filename='client.log', filemode='a', format='%(message)s')
		self.logger = logging.getLogger()
		self.logger.setLevel(logging.INFO)
		self.logger.info('Game Number ' + str(self.counter_games))
		self.logger.info('  Epsilon is ' + str(self.agent.epsilon))
		
	def decide(self):
		
		base = self.world.bases[self.my_side]
		wagent = base.agents[AgentType.Warehouse]
		fagent = base.agents[AgentType.Factory]
		
		if self.stage == 0:  # deciding on a triple ammo to make
			# first we assume current cycle is finished (NOT THAT WE BOTH FINISHED CURRENT AMMO)
			# fuck that, we decide beforehand
			# then we define the state only using unit count
			# we have 20 * 10 * 6 * 16 * 4 = 76800 states in total
			if self.game_state == 0:  # decision
				state = self.calculate_state()
				self.record.append(state)
				if random.random() < self.agent.epsilon:
					self.curr_action, self.current_ammo_mat = self.get_action('random')
					self.logger.info("    Chosen Random Action: " + str(self.curr_action) + " at cycle " + str(self.current_cycle))
				else:
					self.curr_action, self.current_ammo_mat = self.get_action('predict', state)
					self.logger.info("    Chosen Predicted Action: " + str(self.curr_action) + " at cycle " + str(self.current_cycle))
				self.record.append(self.curr_action)
				self.game_state = 1
				self.stage += 1
			elif self.game_state == 1:  # we have finished the transition
				new_state = self.calculate_state()
				self.record.append(new_state)
				self.record.append(self.get_reward(self.record[0], self.record[2]))
				if self.current_cycle >= self.world.max_cycles or \
						self.world.total_healths[self.my_side] == 0 or \
						self.world.total_healths[self.other_side] == 0:
					self.record.append(1)
				else:
					self.record.append(0)
				
				if self.record[4] == 0:
					self.agent.train_short_memory(np.array(self.record[0]),
					                              np.array(self.record[1]),
					                              np.array(self.record[2]),
					                              np.array([self.record[3]]),
					                              np.array([self.record[4]]))
				
				self.agent.memory.append((np.array(self.record[0]),
				                          np.array(self.record[1]),
				                          np.array(self.record[2]),
				                          np.array([self.record[3]]),
				                          np.array([self.record[4]])))
				self.logger.info('    Record is ' + str(self.record))
				self.record = []
				self.game_state = 0
		
		elif self.stage == 1:  # select materials for bullets and put them in BLD
			self.warehouse_agent_move(forward=True)
			if base.c_area[wagent.position] == ECell.Material:
				material_type = base.warehouse.materials[wagent.position].type
				if material_type in self.current_ammo_mat.keys() and wagent.materials_bag[material_type] < self.current_ammo_mat[material_type]:
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
