# -*- coding: utf-8 -*-

# python imports
from copy import deepcopy

# project imports
from .env import Env
from .rebellion_ai import RebellionAI
from .regular_ai import RegularAI


class Manager:
    
    def __init__(self):
        self.sides = ['Rebellion', 'Regular']
        self.ais = {
            'Rebellion': RebellionAI(*self.sides),
            'Regular': RegularAI(*self.sides[::-1])
        }


    def run(self):
        maps = ["maps/Test.json"]

        for map_path in maps:
            env = Env(sides=self.sides, map_path=map_path)
            for _ in range(1):
                self.run_episode(env)
                print("total_healths:", env.world.total_healths)


    def run_episode(self, env):
        env.reset()
        env.reset_gui()
        env.render()
        for ai in self.ais.values():
            ai.reset_episode(env.world)

        while True:
            actions = {}
            for side, ai in self.ais.items():
                ai.decide(env.world)
                actions[side] = ai.get_actions()

            world = deepcopy(env.world)
            done, events = env.step(actions)
            env.render()
            next_world = env.world
            for ai in self.ais.values():
                ai.update(world, next_world, events)

            if done:
                break
