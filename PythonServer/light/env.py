# -*- coding: utf-8 -*-

# python imports
import os
import math
import pygame
from time import sleep

# project imports
from app.handlers.map_handler import MapHandler
from app.ks.models import ECell, MaterialType, AmmoType, AgentType, UnitType


class Env(object):

    def __init__(self, sides, map_path):
        self.sides = sides
        self.config = dict(map_path=map_path)
        self.map_handler = MapHandler(sides)


    def reset(self):
        self.world = self.map_handler.load_map(self.config)
        self.world.current_cycle = 0


    def step(self, actions):
        commands = actions

        events = []
        events.extend(self.world.apply_commands(commands))
        events.extend(self.world.tick())

        done = self.world.check_end_game(self.world.current_cycle)
        self.world.current_cycle += 1

        return done, events


    def reset_gui(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = "10, 35"
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption('Logistics')
        self._screen_width, self._screen_height = 1400, 770
        self._screen = pygame.display.set_mode((self._screen_width, self._screen_height))


    def render(self):
        w = self.world
        screen = self._screen
        font = pygame.font.SysFont('Arial', 13)
        WHITE = (255, 255, 255)
        GRAY = (170, 170, 170)
        BLUE = (0, 200, 200)
        YELLOW = (200, 200, 0)
        width = self._screen_width
        height = self._screen_height
        offset = 5
        cell_size_x = (width - 2 * offset) // len(w.bases['Rebellion'].c_area)
        cell_size_y = cell_size_x + 30

        screen.fill((0, 0, 0))

        for side, base in w.bases.items():
            fx = lambda x: x
            fy = lambda y: y if side == 'Rebellion' else height - y - 125

            for position, cell in base.c_area.items():
                i = position.index
                x = fx(offset + i * cell_size_x)
                y = fy(offset)
                pygame.draw.rect(screen, GRAY, (x, y, cell_size_x, cell_size_y), 1)

                for agent in base.agents.values():
                    if agent.position != position:
                        continue
                    _x = fx(x + 2)
                    if agent.type == AgentType.Factory:
                        _x += cell_size_x // 2
                    color = BLUE if agent.type == AgentType.Warehouse else YELLOW
                    screen.blit(font.render(agent.type.name[0] + 'Agent', True, color), (_x, y))
                    i = 0
                    for mt in MaterialType:
                        i += 15
                        text = f"{mt.name[0]}: {agent.materials_bag.get(mt, 0)}"
                        screen.blit(font.render(text, True, color), (_x, y + i))
                    i = 0
                    for at in AmmoType:
                        i += 15
                        text = f"{at.name[0]}: {agent.ammos_bag.get(at, 0)}"
                        screen.blit(font.render(text, True, WHITE), (_x + cell_size_x//4, y + i))

                y = fy(offset + cell_size_y)
                pygame.draw.rect(screen, GRAY, (x, y, cell_size_x, cell_size_y), 1)

                text = cell.name
                info = None
                info2 = None

                if cell == ECell.Material:
                    material = base.warehouse.materials[position]
                    text = material.type.name
                    info = dict(count=material.count)

                elif cell == ECell.Machine:
                    machine = base.factory.machines[position]
                    info = dict(
                        status = machine.status.name,
                        ca = machine.current_ammo.name if machine.current_ammo else None,
                        crt = machine.construction_rem_time
                    )

                elif cell == ECell.BacklineDelivery:
                    bd = base.backline_delivery
                    info = {}
                    for mt in MaterialType:
                        info[mt.name[:3]] = bd.materials.get(mt, 0)
                    info2 = {}
                    for at in AmmoType:
                        info2[at.name[:3]] = bd.ammos.get(at, 0)

                screen.blit(font.render(text, True, WHITE), (x + 2, y))
                if info:
                    i = 0
                    for k, v in info.items():
                        i += 15
                        text = f"{k}: {v}"
                        screen.blit(font.render(text, True, WHITE), (x + 2, y + i))
                if info2:
                    i = 0
                    for k, v in info2.items():
                        i += 15
                        text = f"{k}: {v}"
                        screen.blit(font.render(text, True, WHITE), (x + cell_size_x//2, y + i))

            x = fx(offset + 2)
            y = fy(offset + 2 * cell_size_y + 10)
            for j, fd in enumerate(base.frontline_deliveries):
                text = f"FD[{j}]:"
                screen.blit(font.render(text, True, WHITE), (x + j*cell_size_x, y))
                i = 15
                text = f"drt: {fd.delivery_rem_time}"
                screen.blit(font.render(text, True, WHITE), (x + j*cell_size_x, y + i))
                for at in AmmoType:
                    i += 15
                    text = f"{at.name[:3]}: {fd.ammos.get(at, 0)}"
                    screen.blit(font.render(text, True, WHITE), (x + j*cell_size_x, y + i))

            x = fx(width - offset - len(UnitType) * cell_size_x)
            text = f"warehouse_reload_rt: {w.bases[side].warehouse.materials_reload_rem_time}"
            screen.blit(font.render(text, True, WHITE), (x - int(1.5 * cell_size_x), y + cell_size_y//3 - 5))

            x = fx(width - offset - len(UnitType) * cell_size_x)
            text = f"total_health: {w.total_healths[side]}"
            screen.blit(font.render(text, True, WHITE), (x - int(1.5 * cell_size_x), y + cell_size_y//3 + 15))

            if side == 'Rebellion':
                text = f"current_cycle: {w.current_cycle}"
                screen.blit(font.render(text, True, WHITE), (x - int(1.5 * cell_size_x), y + cell_size_y - 25))
                text = f"max_cycles: {w.max_cycles}"
                screen.blit(font.render(text, True, WHITE), (x - int(1.5 * cell_size_x), y + cell_size_y - 5))

            for j, unit in enumerate(base.units.values()):
                typename = unit.type.name
                if unit.type == UnitType.HeavyMachineGunner:
                    typename = 'HMG'
                info = dict(
                    type = typename,
                    health = unit.health,
                    ind_hlth = unit.c_individual_health,
                    ind_dmg = unit.c_individual_damage,
                    count = int(math.ceil(unit.health / unit.c_individual_health)),
                    ammo_count = unit.ammo_count,
                    rrt = unit.reload_rem_time
                )
                i = 0
                for k, v in info.items():
                    text = f"{k}: {v}"
                    screen.blit(font.render(text, True, WHITE), (x + j*cell_size_x, y + i))
                    i += 15

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit(0)

        sleep(0.1)
        pygame.display.update()
