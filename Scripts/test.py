# for i in range(1, 149):
# 	adding = str(i)
# 	while len(adding) < 2:
# 		adding = '0' + adding
# 	# print(adding)
# 	print("http://dl.upupfilm.ir/Animation%20TV/tv/%5BFilmGozar.com%5D%20Hunter%20x%20Hunter%20%282011%29/1080p/Hunter%20X%20Hunter%20%282011%29%20-%20" + adding + "%20%5B1080p%5D-%5BFilmGozar.com%5D.mkv")

import os
from collections import deque
from itertools import *
import math
# import time
# import numpy as np
#
# start_time = time.time()
#
# # bro = list(set(product([i for i in range(20)], [i for i in range(10)], [i for i in range(6)], [i for i in range(16)],
# #                        [i for i in range(4)])))
# # broo = list(set(product(bro, [i for i in range(10000)])))
# # print(len(bro), len(broo))
#
# bro = list(set(product([i for i in range(5)], repeat=3)))
# print(bro)
# print(sorted(bro))
# assert len(bro) == len(sorted(bro))
#
# print("--- %s seconds ---" % (time.time() - start_time))

import threading

dic = {0: 3, 1: 4, 2: 5, 3: 3, 4: 6}

bro = sorted(list(set(product([i for i in range(5)], repeat=5)))) + sorted(
	list(set(product([i for i in range(5)], repeat=4)))) + sorted(
	list(set(product([i for i in range(5)], repeat=3)))) + sorted(
	list(set(product([i for i in range(5)], repeat=2)))) + sorted(
	list(set(product([i for i in range(5)], repeat=1))))
bro = [sorted(k) for k in bro]
bro.sort()
bro = list(k for k, _ in groupby(bro))

mat_count = []
for comb in bro:
	cnt = 0
	for i in comb:
		cnt += dic[i]
	mat_count.append(cnt)

# fixed = [bro[i] for i in range(len(bro)) if mat_count[i] <= 15]
fixed = [bro[i] for i in range(len(bro)) if
         1 <= bro[i].count(4) <= 2 and mat_count[i] <= 30]
print(len(fixed), fixed)
# print(len(bro), bro)
# print(len(mat_count), mat_count)

temp = [[6, 0, 1, 3, 0], [2, 5, 1, 1, 1], [4, 0, 2, 4, 0], [2, 3, 2, 2, 1],
        [1, 3, 1, 2, 3]]
dist = [[x / 10 for x in sub] for sub in temp]

ammo_size = [75, 5, 150, 10, 2]
hps = []
hps2 = []
acts = []
acts2 = []
ammos = []
ammos2 = []

qwer = 0
for act in fixed:
	hp = [1570, 4380, 1520, 3520, 2960]
	base_hp = [150, 500, 400, 300, 1000]
	count = [0 for i in range(5)]
	ammo = [act.count(i) * ammo_size[i] for i in range(5)]
	base_dmg = [20, 100, 20, 80, 2000]
	rem = [3, 15, 0, 7, 25]
	max_rem = [3, 15, 0, 7, 25]
	taken = [0 for i in range(5)]
	did_dmg = [False for i in range(5)]

	hp2 = [1570, 4380, 1520, 3520, 2960]
	base_hp2 = [150, 500, 400, 300, 1000]
	count2 = [0 for i in range(5)]
	ammo2 = [0 for i in range(5)]
	base_dmg2 = [20, 100, 20, 80, 2000]
	rem2 = [3, 15, 0, 7, 25]
	max_rem2 = [3, 15, 0, 7, 25]
	taken2 = [0 for i in range(5)]
	did_dmg2 = [False for i in range(5)]

	while True:
		taken2 = [0 for i in range(5)]
		# print(hp, hp2)
		for i in range(5):
			count[i] = math.ceil(hp[i] / base_hp[i])
			count2[i] = math.ceil(hp2[i] / base_hp2[i])

		for i in range(5):
			if rem[i] == max_rem[i] and ammo[i] > 0:
				for j in range(5):
					taken2[j] += math.ceil(
						(min(count[i], ammo[i]) * base_dmg[i]) * dist[i][j])
				ammo[i] = max(ammo[i] - count[i], 0)
				did_dmg[i] = True

			if i == 2:
				continue

			if did_dmg[i]:
				rem[i] -= 1
				if rem[i] == 0:
					rem[i] = max_rem[i]
					did_dmg[i] = False

		for i in range(5):
			hp2[i] = max(hp2[i] - taken2[i], 0)

		if all(ammo[i] == 0 or count[i] == 0 for i in range(5)):
			hps.append(sum(hp))
			hps2.append(sum(hp2))
			acts.append(act)
			ammos.append(ammo)
			ammos2.append(ammo2)
			break

diff = [hps[i] - hps2[i] for i in range(len(hps))]
print(len(hps2))
print(len(acts))
print(len(diff))
yo1 = [x for _, x in sorted(zip(diff, hps2), reverse=True)]
yo2 = [x for _, x in sorted(zip(diff, acts), reverse=True)]
yo3 = [x for _, x in sorted(zip(diff, hps), reverse=True)]
print([i for i in range(5, 0, -1)])
for act in fixed:
	num_wins = 0
	total_diff = 0
	for i in range(len(diff)):
		if yo2[i] == act:
			print(yo1[i], yo2[i], yo3[i], sorted(diff, reverse=True)[i])
			num_wins += 1
			total_diff += sorted(diff, reverse=True)[i]
	if num_wins > 0:
		print('#################### num wins = ' + str(
			num_wins) + ' total diff = ' + str(
			total_diff) + ' avg diff = ' + str(total_diff / num_wins))

# qwer = 0
# for act in fixed:
# 	for act2 in fixed:
# 		hp = [1570, 4380, 1520, 3520, 2960]
# 		base_hp = [150, 500, 400, 300, 1000]
# 		count = [0 for i in range(5)]
# 		ammo = [act.count(i) * ammo_size[i] for i in range(5)]
# 		base_dmg = [20, 100, 20, 80, 2000]
# 		rem = [3, 15, 0, 7, 25]
# 		max_rem = [3, 15, 0, 7, 25]
# 		taken = [0 for i in range(5)]
# 		did_dmg = [False for i in range(5)]
#
# 		hp2 = [1570, 4380, 1520, 3520, 2960]
# 		base_hp2 = [150, 500, 400, 300, 1000]
# 		count2 = [0 for i in range(5)]
# 		ammo2 = [act2.count(i) * ammo_size[i] for i in range(5)]
# 		base_dmg2 = [20, 100, 20, 80, 2000]
# 		rem2 = [3, 15, 0, 7, 25]
# 		max_rem2 = [3, 15, 0, 7, 25]
# 		taken2 = [0 for i in range(5)]
# 		did_dmg2 = [False for i in range(5)]
#
# 		while True:
# 			taken2 = [0 for i in range(5)]
# 			taken = [0 for i in range(5)]
# 			# print(hp, hp2)
# 			for i in range(5):
# 				count[i] = math.ceil(hp[i] / base_hp[i])
# 				count2[i] = math.ceil(hp2[i] / base_hp2[i])
#
# 			for i in range(5):
# 				if rem[i] == max_rem[i] and ammo[i] > 0:
# 					for j in range(5):
# 						taken2[j] += math.ceil((min(count[i], ammo[i]) * base_dmg[i]) * dist[i][j])
# 					ammo[i] = max(ammo[i] - count[i], 0)
# 					did_dmg[i] = True
# 				if rem2[i] == max_rem2[i] and ammo2[i] > 0:
# 					for j in range(5):
# 						taken[j] += math.ceil((min(count2[i], ammo2[i]) * base_dmg2[i]) * dist[i][j])
# 					ammo2[i] = max(ammo2[i] - count2[i], 0)
# 					did_dmg2[i] = True
#
# 				if i == 2:
# 					continue
#
# 				if did_dmg[i]:
# 					rem[i] -= 1
# 					if rem[i] == 0:
# 						rem[i] = max_rem[i]
# 						did_dmg[i] = False
#
# 				if did_dmg2[i]:
# 					rem2[i] -= 1
# 					if rem2[i] == 0:
# 						rem2[i] = max_rem2[i]
# 						did_dmg2[i] = False
#
# 			for i in range(5):
# 				hp2[i] = max(hp2[i] - taken2[i], 0)
# 				hp[i] = max(hp[i] - taken[i], 0)
#
# 			if all(ammo[i] == 0 or count[i] == 0 for i in range(5)) and all(ammo2[i] == 0 or count2[i] == 0 for i in range(5)):
# 				break
#
# 		if sum(hp2) > sum(hp):
# 			hps.append(sum(hp))
# 			hps2.append(sum(hp2))
# 			acts.append(act)
# 			ammos.append(ammo)
# 			acts2.append(act2)
# 			ammos2.append(ammo2)
#
# diff = [hps2[i] - hps[i] for i in range(len(hps))]
# print(len(acts2))
# print(len(hps2))
# print(len(acts))
# print(len(diff))
# yo = [x for _, x in sorted(zip(diff, acts2), reverse=True)]
# yo1 = [x for _, x in sorted(zip(diff, hps2), reverse=True)]
# yo2 = [x for _, x in sorted(zip(diff, acts), reverse=True)]
# yo3 = [x for _, x in sorted(zip(diff, hps), reverse=True)]
#
# for act in fixed:
# 	num_wins = 0
# 	total_diff = 0
# 	for i in range(len(diff)):
# 		if yo[i] == act:
# 			print(yo[i], yo1[i], yo2[i], yo3[i], sorted(diff, reverse=True)[i])
# 			num_wins += 1
# 			total_diff += sorted(diff, reverse=True)[i]
# 	if num_wins > 0:
# 		print('#################### num wins = ' + str(num_wins) + ' total diff = ' + str(total_diff) + ' avg diff = ' + str(total_diff / num_wins))

A = {1: 2, 2: 4, 3: 62, 4: 21, 5: 211}
B = {2: 5, 3: 3, 4: 1}
print({key: A[key] - B.get(key, 0) for key in A.keys()})
