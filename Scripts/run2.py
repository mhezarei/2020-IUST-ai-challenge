###############################################################
###                                                         ###
###     Don't forget to set directories in configs.json     ###
###       * set code_base_directory to the address where    ###
###         your whole game folder is.                      ###
###                                                         ###
###############################################################

import threading
import time
import json
import os
import sys
from chillin_client import GameClient
from PythonRandomClient import random_ai
from PythonClient.ks import models as client_models
from PythonRandomClient.ks import models as random_models
from Classes.DeepQNetwork import DQNAgent

configs = json.loads(open("configs.json", "r").read())
code_base_directory = configs["code_base_directory"]


class RunServer(threading.Thread):
	def run(self):
		print("Running Server...")
		os.system('cd {}PythonServer && python3 main.py'.format(code_base_directory))


class RunClient(threading.Thread):
	def __init__(self, cnt_games, dqn_agent, name):
		super().__init__(name=name)
		self.counter_games = cnt_games
		self.agent = dqn_agent
	
	def run(self):
		print("Running Client...")
		config_path = os.path.join(
			os.path.dirname(os.path.abspath('../PythonClient/main.py')),
			"gamecfg.json"
		)
		if len(sys.argv) > 1:
			config_path = sys.argv[1]
		
		ai = ai.AI(client_models.World(), self.counter_games, self.agent)
		print(ai)
		app = GameClient(config_path)
		app.register_ai(ai)
		app.run()


class RunRandomClient(threading.Thread):
	def __init__(self, cnt_games, dqn_agent, name):
		super().__init__(name=name)
		self.counter_games = cnt_games
		self.agent = dqn_agent
	
	def run(self):
		print("Running Random Client...")
		config_path = os.path.join(
			os.path.dirname(os.path.abspath('../PythonRandomClient/main.py')),
			"gamecfg.json"
		)
		if len(sys.argv) > 1:
			config_path = sys.argv[1]
		
		ai = random_ai.AI(random_models.World(), self.counter_games, self.agent)
		print(ai)
		app = GameClient(config_path)
		app.register_ai(ai)
		app.run()


def get_random_params():
	parameters = {'epsilon_decay_linear': 1 / 50, 'learning_rate': 0.0005, 'first_layer_size': 100,
	              'second_layer_size': 150, 'third_layer_size': 100, 'episodes': 100, 'memory_size': 1800,
	              'weights_path': '../PythonRandomClient/weights/random_weights.hdf5', 'load_weights': False,
	              'save_weights': True}
	return parameters


def get_client_params():
	parameters = {'epsilon_decay_linear': 1 / 50, 'learning_rate': 0.0005, 'first_layer_size': 100,
	              'second_layer_size': 150, 'third_layer_size': 100, 'episodes': 100, 'memory_size': 1800,
	              'weights_path': '../PythonClient/weights/client_weights.hdf5', 'load_weights': False,
	              'save_weights': True}
	return parameters


if __name__ == '__main__':
	
	counter_games = 0
	client_params = get_client_params()
	client_agent = DQNAgent(client_params)
	random_params = get_random_params()
	random_agent = DQNAgent(random_params)
	
	if client_params['load_weights']:
		client_agent.model.load_weights(client_params['weights_path'])
	
	if random_params['load_weights']:
		random_agent.model.load_weights(random_params['weights_path'])
	
	run_server = RunServer(name="RunServer")
	run_random_client = RunRandomClient(counter_games, client_agent, name="RunRandomClient")
	run_client = RunClient(counter_games, client_agent, name="RunClient")
	while counter_games < client_params['episodes']:
		run_server.start()
		time.sleep(1)
		if configs["run_python_client"]:
			run_client.start()
			time.sleep(1)
		if configs["run_python_random_client"]:
			run_random_client.start()
			time.sleep(1)
		
		print(run_server.is_alive(), run_client.is_alive(), run_random_client.is_alive())
		run_server.join()
		run_client.join()
		run_random_client.join()
		
		counter_games += 1
		
		if client_params['save_weights']:
			if os.path.isfile(client_params['weights_path']):
				os.remove(client_params['weights_path'])
			client_agent.model.save_weights(client_params['weights_path'])
		if random_params['save_weights']:
			if os.path.isfile(random_params['weights_path']):
				os.remove(random_params['weights_path'])
			random_agent.model.save_weights(random_params['weights_path'])
		
		run_server = RunServer(name="RunServer")
		run_random_client = RunRandomClient(counter_games, client_agent, name="RunRandomClient")
		run_client = RunClient(counter_games, client_agent, name="RunClient")
