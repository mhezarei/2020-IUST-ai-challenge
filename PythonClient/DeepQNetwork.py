from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers.core import Dense
from keras.callbacks import CSVLogger
import numpy as np
import collections


class DQNAgent(object):
	def __init__(self, params):
		self.reward = 0
		self.gamma = 0.99
		self.short_memory = np.array([])
		self.agent_target = 1
		self.agent_predict = 0
		self.learning_rate = params['learning_rate']
		self.decay_rate = params['epsilon_decay_linear']
		self.epsilon = 1
		self.actual = []
		self.first_layer = params['first_layer_size']
		self.second_layer = params['second_layer_size']
		self.third_layer = params['third_layer_size']
		self.memory = collections.deque(maxlen=params['memory_size'])
		self.weights_path = params['weights_path']
		self.load_weights = params['load_weights']
		self.save_weight = params['save_weights']
		self.model = self.network()

	def network(self):
		model = Sequential()
		model.add(Dense(units=self.first_layer, activation='relu', input_dim=30))
		model.add(Dense(units=self.second_layer, activation='relu'))
		model.add(Dense(units=self.third_layer, activation='relu'))
		model.add(Dense(units=155, activation='softmax'))
		opt = Adam(self.learning_rate)
		model.compile(loss='mse', optimizer=opt)
		return model

	def remember(self, state, action, next_state, reward, done):
		self.memory.append((state, action, next_state, reward, done))

	def train_short_memory(self, state, action, next_state, reward, done):
		target = reward
		if not done:
			target = reward + self.gamma * np.amax(self.model.predict(next_state.reshape((1, 30)))[0])
		target_f = self.model.predict(state.reshape((1, 30)))
		target_f[0][np.argmax(action)] = target
		csv_logger = CSVLogger('loss_log.csv', append=True, separator=';')
		self.model.fit(state.reshape((1, 30)), target_f, epochs=1, verbose=2, callbacks=[csv_logger])
