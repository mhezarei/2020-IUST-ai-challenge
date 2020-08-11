# -*- coding: utf-8 -*-

# chillin imports
from chillin_server.gui.scene_actions import Asset, Vector3

# project imports
from ....ks.models import UnitType


class Forest:

    ASSET = Asset(bundle_name = 'main', asset_name = 'Forest')

    MAX_UNITS = {
        UnitType.Soldier: 19,
        UnitType.Tank: 9,
        UnitType.HeavyMachineGunner: 5,
        UnitType.Mortar: 15,
        UnitType.GoldenTank: 3,
    }

    FRONTLINE_DELIVERY_START = Vector3(x = 57.5, y = 3.25, z = 0)
    FRONTLINE_DELIVERY_ARRIVE = Vector3(x = 15.5625, y = 1.875, z = -1)
    FRONTLINE_DELIVERY_END = Vector3(x = 57.5, y = 1.875, z = -1)

    WAREHOUSE_DELIVERY_START = Vector3(x = 57.5, y = 0, z = 0)
    WAREHOUSE_DELIVERY_ARRIVE = Vector3(x = 0, y = -0.3, z = -1)
    WAREHOUSE_DELIVERY_END = Vector3(x = 57.5, y = -0.3, z = -1)
