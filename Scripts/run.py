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
counter_games = 1


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
	
	os.system('cd {}PythonClient && truncate -s 0 client.log'.format(code_base_directory))
	os.system('cd {}PythonRandomClient && truncate -s 0 random.log'.format(code_base_directory))
	
	run_server = RunServer(name="RunServer")
	run_client = RunClient(name="RunClient")
	run_random_client = RunRandomClient(name="RunRandomClient")
	while counter_games <= 1:
		run_server.start()
		time.sleep(0.5)
		if configs["run_python_client"]:
			run_client.start()
			time.sleep(0.5)
		if configs["run_python_random_client"]:
			run_random_client.start()
			time.sleep(0.5)
		
		run_server.join()
		run_client.join()
		run_random_client.join()

		counter_games += 1

		run_server = RunServer(name="RunServer")
		run_client = RunClient(name="RunClient")
		run_random_client = RunRandomClient(name="RunRandomClient")
