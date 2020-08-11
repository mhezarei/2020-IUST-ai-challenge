[CommandMaterialType]
_def = enum <byte>
    {
        Powder,
        Iron,
        Carbon,
        Gold,
        Shell
    }


[CommandAmmoType]
_def = enum <byte>
    {
        RifleBullet,
        TankShell,
        HMGBullet,
        MortarShell,
        GoldenTankShell
    }


[CommandAgentType]
_def = enum <byte>
    {
        Warehouse,
        Factory
    }


##############################################################

[BaseCommand]
_def = class
agent_type = CommandAgentType


[Move]
_def = class(BaseCommand)
forward = boolean


[PickMaterial]
_def = class(BaseCommand)
materials = map<CommandMaterialType, int>


[PutMaterial]
_def = class(BaseCommand)
desired_ammo = CommandAmmoType


[PickAmmo]
_def = class(BaseCommand)
ammos = map<CommandAmmoType, int>


[PutAmmo]
_def = class(BaseCommand)
