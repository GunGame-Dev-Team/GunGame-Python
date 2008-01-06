#!/usr/bin/env python
'''
(c)2007 by the GunGame Coding Team

    Title:      gg_deathmatch
Version #:      06.01.2008
Description:    This will respawn players after a specified amount of time after
                dying.
                In addition, a fancy effect will be applied to the ragdoll after
                they die.
'''

import es
import playerlib
import gamethread
import repeat
import usermsg

from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_deathmatch Addon for GunGame: Python" 
info.version  = "06.01.08"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_deathmatch" 
info.author   = "Saul, cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007"

# Get some deathmatch settings
addonOptions = {}
addonOptions['enabled'] = int(gungame.getGunGameVar('gg_deathmatch'))
addonOptions['respawn_delay'] = int(gungame.getGunGameVar('gg_dm_respawn_delay'))
addonOptions['ragdoll_effect'] = int(gungame.getGunGameVar('gg_dm_ragdoll_effect'))
addonOptions['respawn_cmd'] = gungame.getGunGameVar('gg_dm_respawn_cmd')
addonOptions['turbo_mode_originally'] = int(gungame.getGunGameVar('gg_turbo'))
addonOptions['knife_elite_originally'] = int(gungame.getGunGameVar('gg_knife_elite'))
addonOptions['map_obj_originally'] = int(gungame.getGunGameVar('gg_map_obj'))

# Globals
respawnPlayers = {}

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_deathmatch', 'GG Deathmatch')
    
    # Enable turbo mode, and disable knife elite
    gungame.setGunGameVar('gg_turbo', '1')
    gungame.setGunGameVar('gg_knife_elite', '0')
    gungame.setGunGameVar('gg_map_obj', '3')
    
    # Get a player list of dead players then spawn them
    for userid in playerlib.getUseridList('#dead'):
        respawn(userid)

def unload():
    # Set turbo mode and knife elite back to what they originally were
    gungame.setGunGameVar('gg_turbo', addonOptions['turbo_mode_originally'])
    gungame.setGunGameVar('gg_knife_elite', addonOptions['knife_elite_originally'])
    gungame.setGunGameVar('gg_map_obj', addonOptions['map_obj_originally'])
    
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_deathmatch')

def gg_variable_changed(event_var):
    # Check required variables to see if they have changed
    if event_var['cvarname'] == 'gg_deathmatch':
        addonOptions['enabled'] = int(gungame.getGunGameVar('gg_deathmatch'))
    
    if event_var['cvarname'] == 'gg_map_obj' and int(event_var['newvalue']) < 3:
        gungame.setGunGameVar('gg_turbo', 3)
        es.msg('#lightgreen', 'WARNING: Map objectives must be removed while gg_deathmatch is enabled!')
    
    if event_var['cvarname'] == 'gg_turbo' and int(event_var['newvalue']) == 0:
        gungame.setGunGameVar('gg_turbo', 1)
        es.msg('#lightgreen', 'WARNING: gg_turbo cannot be unloaded while gg_deathmatch is enabled!')
        
    if event_var['cvarname'] == 'gg_knife_elite' and int(event_var['newvalue']) == 1:
        gungame.setGunGameVar('gg_knife_elite', 0)
        es.msg('#lightgreen', 'WARNING: gg_knife_elite cannot be loaded while gg_deathmatch is enabled!')

def player_class(event_var):
    # Is deathmatch enabled?
    if addonOptions['enabled'] == 0:
        return
    
    # Respawn the player
    respawn(event_var['userid'])

def player_death(event_var):
    # Is deathmatch enabled?
    if addonOptions['enabled'] == 0:
        return
    
    # Respawn the player
    respawn(event_var['userid'])

def RespawnCountdown(userid, repeatInfo):
    # Is the counter 1?
    if respawnPlayers[userid] == 1:
        usermsg.hudhint(userid, 'Respawning in: 1 second.')
    else:
        usermsg.hudhint(userid, "Respawning in: %s seconds." % respawnPlayers[userid])
    
    # Decrement the timer
    respawnPlayers[userid] -= 1

def respawn(userid):
    # Tell the userid they are respawning
    respawnPlayers[userid] = addonOptions['respawn_delay'] 
    repeat.create('RespawnCounter%s' % userid, RespawnCountdown, (userid))
    repeat.start('RespawnCounter%s' % userid, 1, addonOptions['respawn_delay'])
    
    # Respawn the player
    gamethread.delayed(addonOptions['respawn_delay'] + 1, es.server.cmd, "%s %s" % (addonOptions['respawn_cmd'], userid))
    
    # Give the entity dissolver and set its KeyValues
    es.server.cmd('es_xgive %s env_entity_dissolver' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "target cs_ragdoll"' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "magnitude 1"' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "dissolvetype %s"' % (userid, addonOptions['ragdoll_effect']))
    
    # Dissolve the ragdoll then kill the dissolver
    gamethread.delayed(2, es.server.cmd, 'es_xfire %s env_entity_dissolver Dissolve' % userid)
    gamethread.delayed(6, es.server.cmd, 'es_xfire %s env_entity_dissolver Kill' % userid)
    gamethread.delayed(6, es.server.cmd, 'es_xfire %s cs_ragdoll Kill' % userid)