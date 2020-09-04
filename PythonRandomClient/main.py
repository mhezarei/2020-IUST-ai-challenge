#! /usr/bin/env pythonGameClient
# -*- coding: utf-8 -*-

# python imports
import os
import sys
import pickle

# chillin imports
from chillin_client import GameClient

sys.path.insert(1, '../DQN')

# project imports
from random_new import AI
from ks.models import World
from DeepQNetwork import DQNAgent


def get_random_params():
	parameters = {'epsilon_decay_linear': 1 / 75, 'learning_rate': 0.0005, 'first_layer_size': 150,
	              'second_layer_size': 150, 'third_layer_size': 150, 'episodes': 400, 'memory_size': 3000,
	              'batch_size': 50, 'weights_path': './weights/random_weights.hdf5', 'load_weights': False,
	              'save_weights': False, 'mem_path': './mem/random.mem', 'save_mem': False, 'load_mem': False}
	return parameters


counter_games = 1
config_path = os.path.join(
	os.path.dirname(os.path.abspath(__file__)),
	"gamecfg.json"
)
# if len(sys.argv) > 1:
#     config_path = sys.argv[1]
if len(sys.argv) > 1:
	counter_games = int(sys.argv[1])

random_params = get_random_params()
random_agent = DQNAgent(random_params)

# if random_params['load_weights'] and os.path.isfile(random_params['weights_path']):
# 	random_agent.model.load_weights(random_params['weights_path'])
#
# if random_params['load_mem'] and os.path.isfile(random_params['mem_path']):
# 	print("yes")
# 	with open(random_params['mem_path'], 'rb') as mem:
# 		random_agent.memory = pickle.load(mem)

# ai = AI(World(), counter_games, random_agent)
ai = AI(World())
app = GameClient(config_path)
app.register_ai(ai)
app.run()

# if counter_games >= 20:
# 	random_agent.replay_new()
#
# if random_params['save_weights']:
# 	random_agent.model.save_weights(random_params['weights_path'])
#
# if random_params['save_mem']:
# 	with open(random_params['mem_path'], 'wb') as mem:
# 		pickle.dump(random_agent.memory, mem)
#
# print(len(random_agent.memory))
