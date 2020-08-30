import random
from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense
from keras.callbacks import CSVLogger
import numpy as np
import collections


class DQNAgent(object):
	def __init__(self, params):
		self.gamma = 0.99
		self.learning_rate = params['learning_rate']
		self.decay_rate = params['epsilon_decay_linear']
		self.epsilon = 0.25
		self.first_layer = params['first_layer_size']
		self.second_layer = params['second_layer_size']
		self.third_layer = params['third_layer_size']
		self.memory = collections.deque(maxlen=params['memory_size'])
		self.batch_size = params['batch_size']
		self.weights_path = params['weights_path']
		self.load_weights = params['load_weights']
		self.save_weight = params['save_weights']
		self.model = self.network()
	
	def network(self):
		model = Sequential()
		model.add(Dense(units=self.first_layer, activation='relu', input_dim=30))
		model.add(Dense(units=self.second_layer, activation='relu'))
		model.add(Dense(units=self.third_layer, activation='relu'))
		model.add(Dense(units=51, activation='softmax'))
		opt = Adam(self.learning_rate)
		model.compile(loss='mse', optimizer=opt)
		return model
	
	def memorize(self, record):
		self.memory.append((np.array(record[0]), np.array(record[1]), np.array(record[2]), np.array([record[3]]),
		                    np.array([record[4]])))
	
	def replay_new(self):
		if len(self.memory) > self.batch_size:
			mini_batch = random.sample(self.memory, self.batch_size)
		else:
			mini_batch = self.memory
		for state, action, next_state, reward, done in mini_batch:
			# print(state, action, next_state, reward, done)
			self.train_short_memory(state, action, next_state, reward, done)
		print("Replay Successful!")
	
	def train_short_memory(self, state, action, next_state, reward, done):
		target = reward
		if done[0] == 0:
			target = reward + self.gamma * np.amax(self.model.predict(next_state.reshape((1, 30)))[0])
		target_f = self.model.predict(state.reshape((1, 30)))
		target_f[0][np.argmax(action)] = target
		csv_logger = CSVLogger('loss_log.csv', append=True, separator=';')
		self.model.fit(state.reshape((1, 30)), target_f, epochs=1, verbose=2, callbacks=[csv_logger])
