# -*- coding: utf-8 -*-

# python imports
import math

# project imports
from ..ks.models import Unit


def num_alives(self):
    return int(math.ceil(self.health / self.c_individual_health))


Unit.num_alives = num_alives
