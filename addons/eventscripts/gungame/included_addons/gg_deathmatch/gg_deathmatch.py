#!/usr/bin/env python
'''
================================================================================
    All content copyright (c) 2008, GunGame Coding Team
================================================================================
    Name: gg_deathmatch
    Main Author: Saul Rennison
    Version: 1.0.2 (08.01.2008)
================================================================================
    This will respawn players after a specified amount of time after dying.
    In addition, a fancy effect will be applied to the ragdoll after they die.
================================================================================
'''

# System imports
import os.path
import string
import random

# Eventscripts imports
import es
import playerlib
import gamethread
import repeat
import usermsg

# Gungame import
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_deathmatch (for GunGame: Python)"
info.version  = "1.0.2 (08.01.2008)"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_deathmatch" 
info.author   = "Saul (cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2008)"

# Get some addon options
addonOptions = {}
addonOptions['enabled'] = int(gungame.getGunGameVar('gg_deathmatch'))
addonOptions['respawn_delay'] = int(gungame.getGunGameVar('gg_dm_respawn_delay'))
addonOptions['ragdoll_effect'] = int(gungame.getGunGameVar('gg_dm_ragdoll_effect'))
addonOptions['respawn_cmd'] = gungame.getGunGameVar('gg_dm_respawn_cmd')
addonOptions['turbo_mode_originally'] = int(gungame.getGunGameVar('gg_turbo'))
addonOptions['knife_elite_originally'] = int(gungame.getGunGameVar('gg_knife_elite'))
addonOptions['map_obj_originally'] = int(gungame.getGunGameVar('gg_map_obj'))

# Globals
respawnCounters = {}
lastSpawnPoint = {}
spawnPoints = 0

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_deathmatch', 'GG Deathmatch')
    
    # Enable turbo mode, and disable knife elite
    gungame.setGunGameVar('gg_turbo', '1')
    gungame.setGunGameVar('gg_knife_elite', '0')
    gungame.setGunGameVar('gg_map_obj', '3')
    
    # Has map loaded?
    currentMap = str(es.ServerVar('eventscripts_currentmap'))
    if currentMap != '0':
        # Get spawn points, map loaded
        getSpawnPoints(currentMap)
    
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

def es_map_start(event_var):
    getSpawnPoints(event_var['mapname'])

def getSpawnPoints(mapName):
    # Reset the spawn points dict and check if there is a spawnpoint file
    global spawnPoints
    spawnPoints = {}
    spawnFile = getGameDir('cfg\\gungame\\spawnpoints\\%s.txt' % mapName)
    spawnPointsExist = os.path.isfile(spawnFile)
    
    # Does the spawn file exist
    if not spawnPointsExist:
        spawnPoints = 0
        return
    
    # Load the file
    spawnPointFile = open(spawnFile, 'r')
    fileLines = spawnPointFile.readlines()
    i = 0
    
    # Loop through the lines
    for line in fileLines:
        # Strip the line
        line = line.strip()
        
        # Split the line
        values = line.split(' ')
        
        # Get each value and put it into the spawnPoints dictionary
        spawnPoints[i] = values
        
        # Increment the amount of lines
        i += 1

def getGameDir(dir):
    # Get the gungame addon path
    addonPath = es.getAddonPath('gungame')
    
    # Split using the path seperator
    parts = addonPath.split('\\')
    
    # Pop the last 2 items in the list
    parts.pop()
    parts.pop()
    
    # Append cfg then join
    parts.append(dir)
    
    return string.join(parts, '\\')
    
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

def player_team(event_var):
    # Is deathmatch enabled?
    if addonOptions['enabled'] == 0:
        return
    
    # Respawn the player
    gamethread.delayed(5, es.server.cmd, ('%s %s' % (addonOptions['respawn_cmd'], event_var['userid'])))

def player_death(event_var):
    # Is deathmatch enabled?
    if addonOptions['enabled'] == 0:
        return
    
    # Remove their defuser
    gamethread.delayed(0.5, es.remove, ('item_defuser'))
    
    # Respawn the player
    respawn(event_var['userid'])

def RespawnCountdown(userid, repeatInfo):
    # Is warmup round?
    if gungame.getRegisteredAddons().has_key('gungame\\included_addons\\gg_warmup_round'):
        return
    
    # Is the counter 1?
    if respawnCounters[userid] == 1:
        usermsg.hudhint(userid, 'Respawning in: 1 second.')
    else:
        usermsg.hudhint(userid, "Respawning in: %s seconds." % respawnCounters[userid])
    
    # Decrement the timer
    respawnCounters[userid] -= 1

def respawn(userid):
    # Tell the userid they are respawning
    respawnCounters[userid] = addonOptions['respawn_delay'] 
    repeat.create('RespawnCounter%s' % userid, RespawnCountdown, (userid))
    repeat.start('RespawnCounter%s' % userid, 1, addonOptions['respawn_delay'])
    
    # Respawn the player
    gamethread.delayed(addonOptions['respawn_delay'] + 1, es.server.cmd, "%s %s" % (addonOptions['respawn_cmd'], userid))
    
    # Do we have a spawn point file?
    if spawnPoints != 0:
        # Get a random spawn index
        spawnindex = random.randint(0, len(spawnPoints))
        
        try:
            if lastSpawnPoint[userid] == spawnindex:
                # Get another random spawn index
                spawnindex = random.randint(0, len(spawnPoints))
        except KeyError:
            pass
        
        # Set the spawnindex as the last spawn point
        lastSpawnPoint[userid] = spawnindex
        
        # Teleport the player
        gamethread.delayed(addonOptions['respawn_delay'] + 1, gungame.teleportPlayer, (int(userid), spawnPoints[spawnindex][0], spawnPoints[spawnindex][1], spawnPoints[spawnindex][2], 0, spawnPoints[spawnindex][4]))
    
    # Give the entity dissolver and set its KeyValues
    es.server.cmd('es_xgive %s env_entity_dissolver' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "target cs_ragdoll"' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "magnitude 1"' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "dissolvetype %s"' % (userid, addonOptions['ragdoll_effect']))
    
    # Dissolve the ragdoll then kill the dissolver
    gamethread.delayed(2, es.server.cmd, 'es_xfire %s env_entity_dissolver Dissolve' % userid)
    gamethread.delayed(6, es.server.cmd, 'es_xfire %s env_entity_dissolver Kill' % userid)