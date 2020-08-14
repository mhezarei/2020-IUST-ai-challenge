#! /usr/bin/env pythonGameClient
# -*- coding: utf-8 -*-

# python imports
import os
import sys

# chillin imports
from chillin_client import GameClient

sys.path.insert(1, '/home/mh/PycharmProjects/2020-IUST-ai-challenge/DQN')
# project imports
from custom_ai import AI
from ks.models import World
from DeepQNetwork import DQNAgent


def get_random_params():
	parameters = {'epsilon_decay_linear': 1 / 50, 'learning_rate': 0.0005, 'first_layer_size': 100,
	              'second_layer_size': 150, 'third_layer_size': 100, 'episodes': 100, 'memory_size': 1800,
	              'weights_path': '../PythonRandomClient/weights/random_weights.hdf5', 'load_weights': False,
	              'save_weights': True}
	return parameters


counter_games = 0
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

if random_params['load_weights']:
	random_agent.model.load_weights(random_params['weights_path'])

ai = AI(World(), counter_games, random_agent)
app = GameClient(config_path)
app.register_ai(ai)
app.run()

if random_params['save_weights']:
	if os.path.isfile(random_params['weights_path']):
		os.remove(random_params['weights_path'])
	random_agent.model.save_weights(random_params['weights_path'])
