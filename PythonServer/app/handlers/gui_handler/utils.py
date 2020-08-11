# -*- coding: utf-8 -*-

# chillin imports
from chillin_server.gui.scene_actions import \
    (ChangeParadoxBlackboard, ChangeAnimatorState, ChangeText, ChangeAudioSource,
     EParadoxBlackboardValueType, EParadoxBlackboardVariableType, EParadoxBlackboardOperationType,
     Asset)


def change_blackboard_int(world, ref, child_ref, duration_cycles, value, var_name = 'value'):
    world.scene.add_action(ChangeParadoxBlackboard(
        ref = ref,
        child_ref = child_ref,
        duration_cycles = duration_cycles,
        var_name = var_name,
        int_value = value,
        var_type = EParadoxBlackboardVariableType.Simple,
        value_type = EParadoxBlackboardValueType.Int,
        op_type = EParadoxBlackboardOperationType.Edit,
    ))


def change_animator_state(world, ref, state_name, child_ref = None, cycle = None):
    world.scene.add_action(ChangeAnimatorState(
        ref = ref,
        child_ref = child_ref,
        cycle = cycle,
        state_name = state_name,
        normalized_time = 0,
    ))


def change_text(world, ref, child_ref, text, cycle = None):
    world.scene.add_action(ChangeText(
        ref = ref,
        child_ref = child_ref,
        cycle = cycle,
        text = text,
    ))


def change_audio(world, ref, child_ref = None, clip = None, play = True, time = 0, cycle = None):
    asset = Asset(bundle_name = 'main', asset_name = clip) if clip != None else None

    world.scene.add_action(ChangeAudioSource(
        ref = ref,
        child_ref = child_ref,
        cycle = cycle,
        audio_clip_asset = asset,
        play = play,
        time = time,
    ))
