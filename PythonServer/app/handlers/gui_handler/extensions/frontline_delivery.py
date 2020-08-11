# -*- coding: utf-8 -*-

# project imports
from ....ks.models import FrontlineDelivery, ECell, UnitType
from ..utils import change_animator_state, change_audio
from ..courier import Courier


def gui_init_cell(world, side, position):
    if not hasattr(FrontlineDelivery, '_gui_cell_ref'):
        FrontlineDelivery._gui_cell_ref = {}

    FrontlineDelivery._gui_cell_ref[side], _ = ECell.FrontlineDelivery.gui_init(world, side, position)


def gui_put_ammo(self, world, gui_event):
    change_animator_state(world, FrontlineDelivery._gui_cell_ref[gui_event.side], 'CellDoorClose')
    change_animator_state(world, FrontlineDelivery._gui_cell_ref[gui_event.side], 'Idle', cycle = 1)

    # init courier
    self._courier = Courier(
        world,
        gui_event.side,
        self.c_delivery_duration,
        'FrontlineDeliveryPivot',
        world.location.FRONTLINE_DELIVERY_START,
        world.location.FRONTLINE_DELIVERY_ARRIVE,
        world.location.FRONTLINE_DELIVERY_END,
        True,
        self.c_delivery_duration / 2,
        self.ammos,
    )


def gui_ammo_delivered(self, world, gui_event):
    # GuiEvent(GuiEventType.AmmoDelivered, side=side, frontline_delivery=self)
    for ammo_type in self.ammos.keys():
        world.bases[gui_event.side].units[UnitType(ammo_type.value)].gui_ammo_delivered(world, gui_event)

    change_audio(
        world,
        world.location.ref,
        child_ref = 'Support/{}/FrontlineDeliveryPivot'.format(gui_event.side),
        play = True,
    )
    change_audio(
        world,
        world.location.ref,
        child_ref = 'Support/{}/FrontlineDeliveryPivot'.format(gui_event.side),
        play = False,
        cycle = 2,
    )


def gui_update_rem_cycles(self, world):
    self._courier.gui_update_rem_cycles(world, self.delivery_rem_time)


FrontlineDelivery.gui_init_cell = gui_init_cell
FrontlineDelivery.gui_put_ammo = gui_put_ammo
FrontlineDelivery.gui_ammo_delivered = gui_ammo_delivered
FrontlineDelivery.gui_update_rem_cycles = gui_update_rem_cycles
