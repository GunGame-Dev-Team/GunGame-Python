#!/usr/bin/env python

'''
(c)2007 by the GunGame Coding Team

    Title:      gg_deathmatch
Version #:      12.31.2007
Description:    This will respawn players after "x" amount of time after dying.
                Also, a fancy effect will be added to the ragdoll after they
                died.
'''

import es
import playerlib
import gamethread
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_deathmatch Addon for GunGame: Python" 
info.version  = "06.01.08"
info.url      = "" 
info.basename = "gungame/included_addons/gg_deathmatch" 
info.author   = "Saul, cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007"

# Get some deathmatch settings
addonOptions = {}
addonOptions['enabled'] = int(gungame.getGunGameVar('gg_deathmatch'))
addonOptions['respawn_delay'] = float(gungame.getGunGameVar('gg_dm_respawn_delay'))
addonOptions['ragdoll_effect'] = int(gungame.getGunGameVar('gg_dm_ragdoll_effect'))
addonOptions['respawn_cmd'] = gungame.getGunGameVar('gg_dm_respawn_cmd')
addonOptions['turbo_mode_originally'] = int(gungame.getGunGameVar('gg_turbo'))
addonOptions['knife_elite_originally'] = int(gungame.getGunGameVar('gg_knife_elite'))

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_deathmatch', 'GG Deathmatch')
    
    # Enable turbo mode, and disable knife elite
    gungame.setGunGameVar('gg_turbo', '1')
    gungame.setGunGameVar('gg_knife_elite', '0')

def unload():
    # Set turbo mode and knife elite back to what they originally were
    gungame.setGunGameVar('gg_turbo', addonOptions['turbo_mode_originally'])
    gungame.setGunGameVar('gg_knife_elite', addonOptions['knife_elite_originally'])
    
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_deathmatch')

def gg_variable_changed(event_var):
    # Check required variables to see if they have changed
    if event_var['cvarname'] == 'gg_deathmatch':
        addonOptions['enabled'] = int(gungame.getGunGameVar('gg_deathmatch'))
        
    if event_var['cvarname'] == 'gg_turbo' and int(event_var['newvalue']) == 0:
        gungame.setGunGameVar('gg_turbo', 1)
        es.msg('#lightgreen', 'WARNING: gg_turbo cannot be unloaded while gg_deathmatch is enabled!')
        
    if event_var['cvarname'] == 'gg_knife_elite' and int(event_var['newvalue']) == 1:
        gungame.setGunGameVar('gg_knife_elite', 0)
        es.msg('#lightgreen', 'WARNING: gg_knife_elite cannot be loaded while gg_deathmatch is enabled!')

def player_death(event_var):
    # Is deathmatch enabled?
    if int(addonOptions['enabled']) == 0:
        return
    
    # Give the entity dissolver and set its KeyValues
    es.server.cmd('es_xgive %s env_entity_dissolver' % event_var['userid'])
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "target cs_ragdoll"' % event_var['userid'])
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "magnitude 1"' % event_var['userid'])
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "dissolvetype %s"' % (event_var['userid'], addonOptions['ragdoll_effect'] + 1))
    
    # Respawn the player
    gamethread.delayed(addonOptions['respawn_delay'], es.server.cmd, "%s %s" % (addonOptions['respawn_cmd'], event_var['userid']))
    
    # Dissolve the ragdoll then kill the dissolver
    gamethread.delayed(2, es.server.cmd, "es_xfire %s env_entity_dissolver Dissolve" % event_var['userid'])
    gamethread.delayed(4, es.server.cmd, "es_xfire %s env_entity_dissolver Kill" % event_var['userid'])