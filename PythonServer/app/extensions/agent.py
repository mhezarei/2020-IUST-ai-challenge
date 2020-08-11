# -*- coding: utf-8 -*-

# project imports
from ..ks.models import Agent


def move(self, *args, **kwargs):
    raise NotImplementedError


def pick_material(self, *args, **kwargs):
    raise NotImplementedError


def put_material(self, *args, **kwargs):
    raise NotImplementedError


def pick_ammo(self, *args, **kwargs):
    raise NotImplementedError


def put_ammo(self, *args, **kwargs):
    raise NotImplementedError


Agent.move = move
Agent.pick_material = pick_material
Agent.put_material = put_material
Agent.pick_ammo = pick_ammo
Agent.put_ammo = put_ammo
