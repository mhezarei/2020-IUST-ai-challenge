[ECell]
_def = enum <byte>
    {
        Empty,
        FrontlineDelivery,
        Material,
        BacklineDelivery,
        Machine
    }


[MachineStatus]
_def = enum <byte>
    {
        Idle,
        Working,
        AmmoReady
    }


[MaterialType]
_def = enum <byte>
    {
        Powder,
        Iron,
        Carbon,
        Gold,
        Shell
    }


[AmmoType]
_def = enum <byte>
    {
        RifleBullet,
        TankShell,
        HMGBullet,
        MortarShell,
        GoldenTankShell
    }


[UnitType]
_def = enum <byte>
    {
        Soldier,
        Tank,
        HeavyMachineGunner,
        Mortar,
        GoldenTank
    }


[AgentType]
_def = enum <byte>
    {
        Warehouse,
        Factory
    }


##############################################################

[Position]
_def = class
index = int


[Material]
_def = class
type = MaterialType
position = Position
count = int
c_capacity = int


[Machine]
_def = class
position = Position
status = MachineStatus
current_ammo = AmmoType
construction_rem_time = int


##############################################################

[FrontlineDelivery]
_def = class
ammos = map<AmmoType, int>
delivery_rem_time = int
c_delivery_duration = int


[Warehouse]
_def = class
materials = map<Position, Material>
materials_reload_rem_time = int
c_materials_reload_duration = int


[BacklineDelivery]
_def = class
materials = map<MaterialType, int>
ammos = map<AmmoType, int>


[Factory]
_def = class
machines = map<Position, Machine>
c_mixture_formulas = map<AmmoType, map<MaterialType, int>>
c_construction_durations = map<AmmoType, int>
c_ammo_box_sizes = map<AmmoType, int>


##############################################################

[Agent]
_def = class
type = AgentType
position = Position
materials_bag = map<MaterialType, int>
c_materials_bag_capacity = int
ammos_bag = map<AmmoType, int>
c_ammos_bag_capacity = int


[Unit]
_def = class
type = UnitType
health = int
c_individual_health = int
c_individual_damage = int
c_damage_distribution = map<UnitType, float>
ammo_count = int
reload_rem_time = int
c_reload_duration = int


[Base]
_def = class
c_area = map<Position, ECell>
agents = map<AgentType, Agent>
frontline_deliveries = list<FrontlineDelivery>
warehouse = Warehouse
backline_delivery = BacklineDelivery
factory = Factory
units = map<UnitType, Unit>


##############################################################

[World]
_def = class
max_cycles = int
bases = map<string, Base>
total_healths = map<string, int>
