# -*- coding: utf-8 -*-

# python imports
import random

# chillin imports
from chillin_server.gui.reference_manager import default_reference_manager as drm
from chillin_server.gui.tools import GuiTools
from chillin_server.gui.scene_actions import \
    (InstantiateBundleAsset, ChangeTransform, CreateBasicObject, ChangeLight, ChangeCamera, ChangeSlider, ChangeAudioSource,
     EndCycle, EBasicObjectType, Vector2, Vector3, Vector4, Asset, ELightShadowType, ECameraClearFlag, EDefaultParent)

# project imports
from ....ks.models import World, Position, ECell, FrontlineDelivery, Material, BacklineDelivery, Machine
from ..locations import LOCATIONS
from ....ks.models import Position
from ....gui_events import GuiEventType
from ..constants import LEFT_SIDE, RIGHT_SIDE
from ..utils import change_blackboard_int, change_text, change_audio


def _init_objects(self):
    sides = self.bases.keys()

    # Create the location base asset
    self.location.ref = drm.new()
    self.scene.add_action(InstantiateBundleAsset(
        ref = self.location.ref,
        asset = self.location.ASSET,
    ))

    # Init the sides' objects
    for side in sides:
        base = self.bases[side]

        # Support
        # Init cells
        for pos, cell_type in self.bases[side].c_area.items():
            if cell_type == ECell.Empty:
                cell_type.gui_init(self, side, pos)
            elif cell_type == ECell.FrontlineDelivery:
                FrontlineDelivery.gui_init_cell(self, side, pos)
            elif cell_type == ECell.Material:
                base.warehouse.materials[pos].gui_init(self, side)
            elif cell_type == ECell.BacklineDelivery:
                base.backline_delivery.gui_init(self, side, pos)
            elif cell_type == ECell.Machine:
                base.factory.machines[pos].gui_init(self, side)

        # Init agents
        for agent in base.agents.values():
            agent.gui_init(self, side)

        # Frontline
        # Init units
        for unit in base.units.values():
            unit.gui_init(self, side)

    # Create the top status
    self._top_status_ref = drm.new()
    self.scene.add_action(InstantiateBundleAsset(
        ref = self._top_status_ref,
        asset = Asset(bundle_name='main', asset_name='TopStatus'),
        default_parent = EDefaultParent.RootCanvas,
    ))
    change_text(self, self._top_status_ref, 'Cycle/MaxCycle', str(self.max_cycles))
    for side in sides:
        change_text(self, self._top_status_ref, '{}TeamName'.format(side), self._team_nicknames[side])
    self._update_top_status(0)


def _init_light(self):
    main_light = drm.new()
    self.scene.add_action(CreateBasicObject(
        ref = main_light,
        type = EBasicObjectType.Light,
    ))
    self.scene.add_action(ChangeTransform(
        ref = main_light,
        rotation = Vector3(x = 50, y = 0, z = 0),
    ))
    self.scene.add_action(ChangeLight(
        ref = main_light,
        intensity = 1,
        shadow_type = ELightShadowType.Disabled,
    ))


def _init_camera(self, min_zoom, max_zoom, max_x):
    self.scene.add_action(ChangeCamera(
        ref = drm.get('MainCamera'),
        is_orthographic = True,
        clear_flag = ECameraClearFlag.SolidColor,
        background_color = Vector4(x = 24/255, y = 8/255, z = 0/255, w = 1),
        orthographic_size = 11,
        min_position = Vector3(x = -max_x, y = -10, z = -10),
        max_position = Vector3(x = max_x, y = 10, z = -10),
        min_rotation = Vector2(x = 0, y = 0),
        max_rotation = Vector2(x = 0, y = 0),
        min_zoom = min_zoom,
        max_zoom = max_zoom,
    ))
    self.scene.add_action(ChangeTransform(
        ref=drm.get('MainCamera'),
        position=Vector3(x=0, y=3, z=-10),
        rotation=Vector3(x=0, y=0, z=0),
    ))


def _init_sounds(self):
    # Background music
    BACKGROUND_MUSICS = [
        ('Background0Start', 'Background0Repeat', GuiTools.time_to_cycle(40.867 - 0.001)),
    ]

    bg_music_start, bg_music_repeat, bg_music_start_duration = random.choice(BACKGROUND_MUSICS)
    background_music_ref = drm.new()
    self.scene.add_action(InstantiateBundleAsset(
        ref = background_music_ref,
        asset = Asset(bundle_name = 'main', asset_name = 'BackgroundMusic'),
    ))
    change_audio(self, background_music_ref, clip = bg_music_start)
    change_audio(self, background_music_ref, clip = bg_music_repeat, cycle = bg_music_start_duration)

    # Countdown
    countdown_ref = drm.new()
    self.scene.add_action(InstantiateBundleAsset(
        ref = countdown_ref,
        asset = Asset(bundle_name = 'main', asset_name = 'Countdown'),
    ))
    change_audio(self, countdown_ref, play = True)
    change_audio(self, countdown_ref, play = False, cycle = 4)
    self.scene.add_action(EndCycle())
    self.scene.add_action(EndCycle())


def gui_init(self, scene, team_nicknames):
    self.scene = scene
    self._team_nicknames = team_nicknames
    self.location = LOCATIONS['Forest']

    # Calculate the cells' start offset
    c_area_width = len(self.bases[LEFT_SIDE].c_area.keys())
    cell_start_offsets = { Position(c_area_width - 1): 0 }
    for i in range(c_area_width - 2, -1, -1):
        pos = Position(i)
        prev_cell_type = self.bases[LEFT_SIDE].c_area[pos + 1]
        cell_start_offsets[pos] = cell_start_offsets[pos + 1] + prev_cell_type.get_gui_width()
    Position.set_gui_offsets(cell_start_offsets)

    min_zoom = 2
    max_zoom = 11
    screen_ratio = 3 / 2
    max_x = Position(index=0).get_gui_offset() + 4.5 - min_zoom * screen_ratio
    screen_end_x = max_x + max_zoom * screen_ratio

    # Update some location values
    self.location.FRONTLINE_DELIVERY_START.x = screen_end_x + 1
    self.location.FRONTLINE_DELIVERY_END.x = screen_end_x + 1

    self.location.WAREHOUSE_DELIVERY_START.x = screen_end_x + 1
    self.location.WAREHOUSE_DELIVERY_ARRIVE.x = Position(index=0).get_gui_offset() + 3.5
    self.location.WAREHOUSE_DELIVERY_END.x = screen_end_x + 1

    # Inits
    self._init_objects()
    self._init_light()
    self._init_camera(min_zoom, max_zoom, max_x)
    self._init_sounds()

    # This must be after init_sounds
    # Create first courier for warehouse
    for side in self.bases.keys():
        self.bases[side].warehouse.gui_create_courier(self, side)

    self.scene.add_action(EndCycle())


def gui_update(self, current_cycle, events):
    sides = self.bases.keys()

    # Manage events
    for event in events:
        if event.type == GuiEventType.Move:
            event.agent.gui_move(self, event)

        elif event.type == GuiEventType.PickMaterial:
            event.agent.gui_pick_material(self, event)

        elif event.type == GuiEventType.PutMaterial:
            event.agent.gui_put_material(self, event)

        elif event.type == GuiEventType.PickAmmo:
            event.agent.gui_pick_ammo(self, event)

        elif event.type == GuiEventType.PutAmmo:
            event.agent.gui_put_ammo(self, event)

        elif event.type == GuiEventType.WarehouseReload:
            self.bases[event.side].warehouse.gui_reload(self, event)

        elif event.type == GuiEventType.MachineAmmoReady:
            event.machine.gui_ammo_ready(self, event)

        elif event.type == GuiEventType.AmmoDelivered:
            event.frontline_delivery.gui_ammo_delivered(self, event)

        elif event.type == GuiEventType.UnitReloading:
            event.unit.gui_reloading(self, event)

        elif event.type == GuiEventType.UnitFired:
            event.unit.gui_fired(self, event)

        elif event.type == GuiEventType.UnitDamaged:
            event.unit.gui_damaged(self, event)

    for side in sides:
        base = self.bases[side]

        # Update machine timers
        for machine in base.factory.machines.values():
            machine.gui_update_timer(self)

        # Update agents status text
        for agent in base.agents.values():
            agent.gui_update_status(self)

        # Update units animator
        for unit in base.units.values():
            unit.gui_update_animator(self)

        # Update frontline deliveries
        for fdelivery in base.frontline_deliveries:
            fdelivery.gui_update_rem_cycles(self)

        # Update warehouse courier
        base.warehouse.gui_update_courier_rem_cycles(self)

    self._update_top_status(current_cycle)

    self.scene.add_action(EndCycle())


def _update_top_status(self, current_cycle):
    duration_cycles = 0.5

    change_text(self, self._top_status_ref, 'Cycle/Counter', str(current_cycle))

    for side in self.bases.keys():
        change_blackboard_int(self, self._top_status_ref, 'TotalHealth/{}Health'.format(side), duration_cycles, self.total_healths[side])

    sum_total_healths = sum(self.total_healths.values())
    self.scene.add_action(ChangeSlider(
        ref = self._top_status_ref,
        child_ref = 'TotalHealth',
        duration_cycles = duration_cycles,
        value = (self.total_healths[RIGHT_SIDE] / sum_total_healths) if sum_total_healths > 0 else 0.5,
    ))


World._init_objects = _init_objects
World._init_light = _init_light
World._init_camera = _init_camera
World._init_sounds = _init_sounds
World.gui_init = gui_init
World.gui_update = gui_update
World._update_top_status = _update_top_status
