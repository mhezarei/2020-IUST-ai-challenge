# -*- coding: utf-8 -*-

# project imports
from ..ks.models import World, Base


class LogicHandler:

    def __init__ (self, world, sides):
        self._sides = sides
        self.world = world


    def initialize(self):
        self.clear_commands()


    def store_command(self, side_name, command):
        ### This method should be removed after adding 'import' feature to the koala-serializer ###
        def convert_command(command):
            from ..ks.models import MaterialType, AmmoType, AgentType
            command.agent_type = AgentType(command.agent_type.value)

            materials = command.__dict__.get('materials')
            if materials:
                for material_type in list(materials.keys()):
                    materials[MaterialType(material_type.value)] = materials.pop(material_type)

            ammos = command.__dict__.get('ammos')
            if ammos:
                for ammo_type in list(ammos.keys()):
                    ammos[AmmoType(ammo_type.value)] = ammos.pop(ammo_type)

            if 'desired_ammo' in command.__dict__:
                command.__dict__['desired_ammo'] = AmmoType(command.__dict__['desired_ammo'].value)

        convert_command(command)
        self._last_cycle_commands[side_name][command.agent_type] = command


    def clear_commands(self):
        self._last_cycle_commands = {side: {} for side in self._sides}


    def process(self, current_cycle):
        gui_events = []
        gui_events.extend(self.world.apply_commands(self._last_cycle_commands))
        gui_events.extend(self.world.tick())
        return gui_events


    def get_client_world(self, side_name):
        enemy_side = [s for s in self._sides if s != side_name][0]

        world = World(
            max_cycles = self.world.max_cycles,
            bases = {
                side_name: self.world.bases[side_name],
                enemy_side: Base(
                    units = self.world.bases[enemy_side].units,
                    frontline_deliveries = self.world.bases[enemy_side].frontline_deliveries,
                ),
            },
            total_healths = self.world.total_healths,
        )

        return world


    def check_end_game(self, current_cycle):
        end_game = self.world.check_end_game(current_cycle)

        if end_game:
            winner = self.world.get_winner()
            details = {
                'Remaining Healths': {
                    side: str(health) for side, health in self.world.total_healths.items()
                }
            }
            return end_game, winner, details

        return end_game, None, None
