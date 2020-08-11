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
from first import AI
from ks.models import World
from DeepQNetwork import DQNAgent

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
			os.path.dirname(os.path.abspath(__file__)),
			"gamecfg.json"
		)
		if len(sys.argv) > 1:
			config_path = sys.argv[1]
		
		ai = AI(World(), self.counter_games, self.agent)
		app = GameClient(config_path)
		app.register_ai(ai)
		app.run()


class RunRandomClient(threading.Thread):
	def run(self):
		print("Running Random Client...")
		os.system('cd {}PythonRandomClient && python3 main.py'.format(code_base_directory))


def define_params():
	parameters = {'epsilon_decay_linear': 1 / 50, 'learning_rate': 0.0005, 'first_layer_size': 100,
	              'second_layer_size': 150, 'third_layer_size': 100, 'episodes': 100, 'memory_size': 1800,
	              'weights_path': 'weights/weights.hdf5', 'load_weights': False,
	              'save_weights': True}
	return parameters


if __name__ == '__main__':
	
	counter_games = 0
	params = define_params()
	agent = DQNAgent(params)
	
	if params['load_weights']:
		agent.model.load_weights(params['weights_path'])
	
	run_server = RunServer(name="RunServer")
	run_random_client = RunRandomClient(name="RunRandomClient")
	run_client = RunClient(counter_games, agent, name="RunClient")
	while counter_games < params['episodes']:
		run_server.start()
		time.sleep(1)
		if configs["run_python_client"]:
			run_client.start()
			time.sleep(1)
		if configs["run_python_random_client"]:
			run_random_client.start()
			time.sleep(1)
		
		print("HI " + str(run_server.is_alive()) + str(run_client.is_alive()) + str(run_random_client.is_alive()))
		
		run_server.join()
		run_client.join()
		run_random_client.join()
		
		print("finished " + str(counter_games))
		counter_games += 1
		print("HI " + str(run_server.is_alive()) + str(run_client.is_alive()) + str(run_random_client.is_alive()))
		if params['save_weights']:
			agent.model.save_weights(params['weights_path'])
		run_server = RunServer(name="RunServer")
		run_random_client = RunRandomClient(name="RunRandomClient")
		run_client = RunClient(counter_games, agent, name="RunClient")
