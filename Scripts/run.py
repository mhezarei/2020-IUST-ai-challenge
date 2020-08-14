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

configs = json.loads(open("configs.json", "r").read())
code_base_directory = configs["code_base_directory"]
counter_games = 0


class RunServer(threading.Thread):
	def run(self):
		print("Running Server...")
		os.system('cd {}PythonServer && python3 main.py'.format(code_base_directory))


class RunClient(threading.Thread):
	def run(self):
		print("Running Client...")
		os.system(('cd {}PythonClient && python3 main.py ' + str(counter_games)).format(code_base_directory))


class RunRandomClient(threading.Thread):
	def run(self):
		print("Running Random Client...")
		os.system(('cd {}PythonRandomClient && python3 main.py ' + str(counter_games)).format(code_base_directory))


if __name__ == '__main__':
	
	os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
	
	run_server = RunServer(name="RunServer")
	run_random_client = RunRandomClient(name="RunRandomClient")
	run_client = RunClient(name="RunClient")
	while counter_games < 100:
		run_server.start()
		time.sleep(1)
		if configs["run_python_client"]:
			run_client.start()
			time.sleep(1)
		if configs["run_python_random_client"]:
			run_random_client.start()
			time.sleep(1)
		
		run_server.join()
		run_client.join()
		run_random_client.join()

		counter_games += 1

		run_server = RunServer(name="RunServer")
		run_random_client = RunRandomClient(name="RunRandomClient")
		run_client = RunClient(name="RunClient")