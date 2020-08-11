from itertools import *
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

###############################################################
###                                                         ###
###     Don't forget to set directories in configs.json     ###
###       * set code_base_directory to the address where    ###
###         your whole game folder is.                      ###
###                                                         ###
###############################################################

import threading


print((sorted(list(set(product([i for i in range(5)], repeat=3)))) + sorted(
			list(set(product([i for i in range(5)], repeat=2)))) + sorted(
			list(set(product([i for i in range(5)], repeat=1))))))
