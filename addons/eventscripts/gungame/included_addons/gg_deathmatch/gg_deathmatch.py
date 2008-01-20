#!/usr/bin/env python
'''
================================================================================
    All content copyright (c) 2008, GunGame Coding Team
================================================================================
    Name: gg_deathmatch
    Main Author: Saul Rennison
    Version: 1.0.58 (16.01.2008)
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
info.version  = "1.0.58 (16.01.2008)"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_deathmatch"
info.author   = "Saul (cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2008)"

# Get some deathmatch vars
dict_deathmatchVars = {}
dict_deathmatchVars['respawn_delay'] = int(gungame.getGunGameVar('gg_dm_respawn_delay'))
dict_deathmatchVars['ragdoll_effect'] = int(gungame.getGunGameVar('gg_dm_ragdoll_effect'))
dict_deathmatchVars['respawn_cmd'] = gungame.getGunGameVar('gg_dm_respawn_cmd')

# Get some gungame vars to restore later
dict_gungameVars = {}
dict_gungameVars['turbo_mode_originally'] = int(gungame.getGunGameVar('gg_turbo'))
dict_gungameVars['dead_strip_originally'] = int(gungame.getGunGameVar('gg_dead_strip'))
dict_gungameVars['knife_elite_originally'] = int(gungame.getGunGameVar('gg_knife_elite'))
dict_gungameVars['map_obj_originally'] = int(gungame.getGunGameVar('gg_map_obj'))

# Globals
respawnCounters = {}
lastSpawnPoint = {}
spawnPoints = {}
mapName = 0

def load():
    global mapName
    
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_deathmatch', 'GG Deathmatch')
    
    # Register Dependencies
    gungame.registerDependency('gungame/included_addons/gg_turbo', 'gungame/included_addons/gg_deathmatch')
    gungame.registerDependency('gungame/included_addons/gg_dead_strip', 'gungame/included_addons/gg_deathmatch')
    
    # Enable turbo mode, and remove all objectives
    gungame.setGunGameVar('gg_turbo', '1')
    gungame.setGunGameVar('gg_dead_strip', '1')
    gungame.setGunGameVar('gg_map_obj', '0')
    
    # Check if gg_knife_elite is running
    if gungame.getGunGameVar('gg_knife_elite') == '1':
        # Check if gg_knife_elite is a dependency of any other addons
        if not gungame.checkDependency('gungame/included_addons/gg_knife_elite'):
            # Unload gg_knife_elite
            gungame.setGunGameVar('gg_knife_elite', '0')
        else:
            # gg_knife_elite has depencies, show message and unload gg_deathmatch
            es.dbgmsg(0, '***WARNING***')
            es.dbgmsg(0, '* gg_deathmatch cannot unload gg_knife_elite')
            es.dbgmsg(0, '* gg_knife_elite is a dependency of the following addons:')
            for addon in gungame.getAddonDependencyList('gungame/included_addons/gg_knife_elite'):
                es.dbgmsg(0, '* ' + addon)
            es.dbgmsg(0, '* gg_deathmatch will be unloaded')
            es.dbgmsg(0, '*************')
            
            gungame.setGunGameVar('gg_deathmatch', '0')
            
    # Create commands
    if not es.exists('command','dm_add'):
        es.regcmd('dm_add','gungame/included_addons/gg_deathmatch/cmd_addSpawnPoint', 'Adds a spawnpoint at <userid>\'s location on the current map.')
    if not es.exists('command','dm_del_all'):
        es.regcmd('dm_del_all','gungame/included_addons/gg_deathmatch/cmd_delAllSpawnPoints', 'Deletes all spawnpoints on the current map.')
    if not es.exists('command','dm_show'):
        es.regcmd('dm_show','gungame/included_addons/gg_deathmatch/cmd_showSpawnPoints', 'Shows all spawnpoints with a glow on the current map.')
    if not es.exists('command','dm_print'):
        es.regcmd('dm_print','gungame/included_addons/gg_deathmatch/cmd_printSpawnPoints', 'Displays spawnpoints for this map (including indexes) in the callers console.')
    if not es.exists('command','dm_remove'):
        es.regcmd('dm_print','gungame/included_addons/gg_deathmatch/cmd_delSpawnPoint', 'Removes a single spawnpoint.')
    
    # Has map loaded?
    currentMap = str(es.ServerVar('eventscripts_currentmap'))
    if currentMap != '0':
        # Get spawn points, map loaded
        mapName = currentMap
        getSpawnPoints(currentMap)
    
    # Get a player list of dead players then spawn them
    for userid in playerlib.getUseridList('#dead'):
        respawn(userid)

def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_deathmatch')
    
    # UnRegister Dependencies
    gungame.unregisterDependency('gungame/included_addons/gg_turbo', 'gungame/included_addons/gg_deathmatch')
    gungame.unregisterDependency('gungame/included_addons/gg_dead_strip', 'gungame/included_addons/gg_deathmatch')
    
    # Set turbo mode and knife elite back to what they originally were
    if not dict_gungameVars['turbo_mode_originally']:
        if not gungame.checkDependency('gungame/included_addons/gg_turbo'):
            gungame.setGunGameVar('gg_turbo', 0)
    if not dict_gungameVars['dead_strip_originally']:
        if not gungame.checkDependency('gungame/included_addons/gg_dead_strip'):
            gungame.setGunGameVar('gg_dead_strip', 0)
    
    # Return vars
    gungame.setGunGameVar('gg_knife_elite', dict_gungameVars['knife_elite_originally'])
    gungame.setGunGameVar('gg_map_obj', dict_gungameVars['map_obj_originally'])

def gg_variable_changed(event_var):
    # Check required variables to see if they have changed
    if event_var['cvarname'] == 'gg_map_obj' and int(event_var['newvalue']) > 0:
        gungame.setGunGameVar('gg_map_obj', 0)
        es.msg('#lightgreen', 'WARNING: Map objectives must be removed while gg_deathmatch is enabled!')
    
    if event_var['cvarname'] == 'gg_turbo' and int(event_var['newvalue']) == 0:
        gungame.setGunGameVar('gg_turbo', 1)
        es.msg('#lightgreen', 'WARNING: gg_turbo cannot be unloaded while gg_deathmatch is enabled!')
    
    if event_var['cvarname'] == 'gg_dead_strip' and int(event_var['newvalue']) == 0:
        gungame.setGunGameVar('gg_dead_strip', 1)
        es.msg('#lightgreen', 'WARNING: gg_dead_strip cannot be unloaded while gg_deathmatch is enabled!')
        
    # Watch for changes in deathmatch variables
    if dict_deathmatchVars.has_key(event_var['cvarname']):
        dict_deathmatchVars[event_var['cvarname']] = int(event_var['newvalue'])
        
    # Check if gg_knife_elite is running
    if event_var['cvarname'] == 'gg_knife_elite' and int(event_var['newvalue']) == 1:
        # Check if gg_knife_elite is a dependency of any other addons
        if not gungame.checkDependency('gungame/included_addons/gg_knife_elite'):
            # Unload gg_knife_elite
            gungame.setGunGameVar('gg_knife_elite', '0')
        else:
            # gg_knife_elite has dependencies, show message and unload gg_deathmatch
            es.dbgmsg(0, '***WARNING***')
            es.dbgmsg(0, '* gg_deathmatch cannot unload gg_knife_elite')
            es.dbgmsg(0, '* gg_knife_elite is a dependency of the following addons:')
            
            # Show dependencies
            for addon in gungame.getAddonDependencyList('gungame/included_addons/gg_knife_elite'):
                es.dbgmsg(0, '* ' + addon)
            es.dbgmsg(0, '* gg_deathmatch will be unloaded')
            es.dbgmsg(0, '*************')
            gungame.setGunGameVar('gg_deathmatch', '0')

def es_map_start(event_var):
    global mapName
    
    mapName = event_var['mapname']
    getSpawnPoints(event_var['mapname'])

def getSpawnPoints(_mapName):
    global spawnPoints
    global spawnFile
    global spawnPointsExist
    
    # Open the file and clear the spawn point dictionary
    spawnPoints = {}
    spawnFile = getGameDir('cfg\\gungame\\spawnpoints\\%s.txt' % _mapName)
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

def addSpawnPoint(posX, posY, posZ, eyeYaw):
    global mapName
    global spawnFile
    
    # Do we have a spawn point file?
    if not spawnPointsExist:
        # Create spawnpoint file
        spawnFile = getGameDir('cfg\\gungame\\spawnpoints\\%s.txt' % mapName)
        spawnPointFile = open(spawnFile, 'w').close()
        
        # Rehash spawnpoints
        getSpawnPoints(mapName)
        
    
    # Open the spawnpoint file
    spawnPointFile = open(spawnFile, 'a')
    
    # Prep the vars
    posX = float(posX)
    posY = float(posY)
    posZ = float(posZ)
    eyeYaw = float(eyeYaw)
    
    # Write to file, flush and close
    spawnPointFile.write('%f %f %f 0.000000 %f 0.000000\n' % (posX, posY, posZ, eyeYaw))
    spawnPointFile.flush()
    spawnPointFile.close()
    
    # Get spawnpoints again
    getSpawnPoints(mapName)
    
def removeSpawnPoint(index):
    # Do we have a spawn point file?
    if not spawnPointsExist:
        return False
    
    # Remove spawn point from dictionary
    del spawnPoints[int(index)]

    # Load the file
    spawnPointFile = open(spawnFile, 'w')
    
    # Loop through the spawnpoints
    for index in spawnPoints:
        # Get list
        spawnLoc = spawnPoints[index]
        
        # Write to file
        spawnPointFile.write('%f %f %f 0.000000 %f 0.000000\n' % (spawnPoint[0], spawnPoint[1], spawnPoint[2], spawnPoint[4]))
        
    # Flush and close the file
    spawnPointFile.flush()
    spawnPointFile.close()

    # Get spawnpoints again
    getSpawnPoints(mapName)

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

def player_team(event_var):
    # Respawn the player
    gamethread.delayed(5, es.server.cmd, ('%s %s' % (dict_deathmatchVars['respawn_cmd'], event_var['userid'])))

def player_death(event_var):
    # Remove their defuser
    gamethread.delayed(0.5, es.remove, ('item_defuser'))
    
    # Respawn the player
    respawn(event_var['userid'])

def RespawnCountdown(userid, repeatInfo):
    # Is it in warmup?
    if int(gungame.getGlobal('isWarmup')) or int(gungame.getGlobal('voteActive')):
        return
    
    # Is the counter 1?
    if respawnCounters[userid] == 1:
        gungame.Message(userid).hudhint('gg_deathmatch:RespawnCountdown_Singular')
    else:
        gungame.Message(userid).hudhint('gg_deathmatch:RespawnCountdown_Plural', {'time': respawnCounters[userid]})
    
    # Decrement the timer
    respawnCounters[userid] -= 1

def player_spawn(ev):
    gungame.Message(int(ev['userid'])).msg('gg_deathmatch:YouSpawned')

def respawn(userid):
    # Tell the userid they are respawning
    respawnCounters[userid] = dict_deathmatchVars['respawn_delay']
    repeat.create('RespawnCounter%s' % userid, RespawnCountdown, (userid))
    repeat.start('RespawnCounter%s' % userid, 1, dict_deathmatchVars['respawn_delay'])
    
    # Respawn the player
    gamethread.delayed(dict_deathmatchVars['respawn_delay'] + 1, es.server.cmd, "%s %s" % (dict_deathmatchVars['respawn_cmd'], userid))
    
    # Do we have a spawn point file?
    if spawnPoints != 0:
        # Get a random spawn index
        spawnindex = random.randint(0, len(spawnPoints) - 1)
        
        try:
            if lastSpawnPoint[userid] == spawnindex:
                # Get another random spawn index
                spawnindex = random.randint(0, len(spawnPoints) - 1)
        except KeyError:
            pass
        
        # Set the spawnindex as the last spawn point
        lastSpawnPoint[userid] = spawnindex
        
        # Teleport the player
        gamethread.delayed(dict_deathmatchVars['respawn_delay'] + 1, gungame.teleportPlayer, (int(userid), spawnPoints[spawnindex][0], spawnPoints[spawnindex][1], spawnPoints[spawnindex][2], 0, spawnPoints[spawnindex][4]))
    
    # Give the entity dissolver and set its KeyValues
    es.server.cmd('es_xfire %s env_entity_dissolver Kill' % userid)
    es.server.cmd('es_xgive %s env_entity_dissolver' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "target cs_ragdoll"' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "magnitude 1"' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "dissolvetype %s"' % (userid, dict_deathmatchVars['ragdoll_effect']))
    
    # Dissolve the ragdoll then kill the dissolver
    gamethread.delayed(2, es.server.cmd, 'es_xfire %s env_entity_dissolver Dissolve' % userid)
    
def cmd_addSpawnPoint():
    global spawnPoints
    
    # Do we have enough arguments?
    if int(es.getargc()) != 2:
        # Raise argument error
        raise ArgumentError, str(int(es.getargc()) - 1) + ' arguments provided. Expected: 1'
    
    # Get executor userid and 1st argument
    userid = int(es.getargv(1))
    
    # Does the userid exist?
    if not es.exists('userid', userid):
        gungame.Message(0).echo('CannotCreateSpawnpoint', {'userid': userid})
        return
    
    # Is a map loaded?
    if mapName != 0:
        # Get player location and viewing angles
        playerlibPlayer = playerlib.getPlayer(userid)
        playerLoc = es.getplayerlocation(userid)
        playerViewAngle = playerlibPlayer.get('viewangle')
        
        # Add spawn point
        addSpawnPoint(playerLoc[0], playerLoc[1], playerLoc[2], playerViewAngle[0])
        
        # Show a sprite at the new spawnpoint location
        es.server.cmd('est_effect 11 %d 0 sprites/greenglow1.vmt %s %s %f 5 1 255' % (userid, playerLoc[0], playerLoc[1], float(playerLoc[2]) + 50))
        
        # Tell the user where the spawnpoint is, and the index
        gungame.Message(userid).tell('gg_deathmatch:AddedSpawnpoint', {'index': len(spawnPoints) - 1})

def cmd_delAllSpawnPoints():
    # Enough arguments?
    if int(es.getargc()) != 1:
        # Raise argument error
        raise ArgumentError, str(int(es.getargc()) - 1) + ' arguments provided. Expected: 0'
    
    # Check if a map is loaded
    if mapName != 0:
        # Clear the spawnpoint file
        spawnFile = open(getGameDir('cfg\\gungame\\spawnpoints\\%s.txt' % mapName), 'w').close()
        
        # Get spawnpoints
        getSpawnPoints(mapName)

def cmd_printSpawnPoints():
    # Enough arguments?
    if int(es.getargc()) != 1:
        # Raise argument error
        raise ArgumentError, str(int(es.getargc()) - 1) + ' arguments provided. Expected: 0'
    
    # Send message
    gungame.Message(0).echo('gg_deathmatch:SpawnpointsFor', {'map': mapName})
    
    # Loop through the spawnpoints
    for index in spawnPoints:
        # Get list
        spawnLoc = spawnPoints[index]
        
        # Print to console
        gungame.Message(0).echo('gg_deathmatch:SpawnpointInfo', {'index': index, 'x': spawnLoc[0], 'y': spawnLoc[1], 'z': spawnLoc[2]})
    
    # Send end message
    gungame.Message(0).echo('gg_deathmatch:SpawnpointsEnd')

def cmd_delSpawnPoint():
    # Enough arguments?
    if int(es.getargc()) == 2:
        # Raise argument error
        raise ArgumentError, str(int(es.getargc()) - 1) + ' arguments provided. Expected: 1'
    
    # Delete the spawn point
    removeSpawnPoint(int(es.getargv(1)))
    
    # Print to console
    gungame.Message(0).echo('RemovedSpawnpoint', {'index': es.getargv(1)})

def cmd_showSpawnPoints():
    # Do we have enough arguments?
    if int(es.getargc()) != 2:
        # Raise argument error
        raise ArgumentError, str(int(es.getargc()) - 1) + ' arguments provided. Expected: 1'
    
    # Set vars
    userid = es.getargv(1)
    
    # Loop through spawn points
    for index in spawnPoints:
        # Get list
        spriteLoc = spawnPoints[index]
        
        # Create sprite
        es.server.cmd('est_effect 11 %s 0 sprites/greenglow1.vmt %s %s %f 5 1 255' % (userid, spriteLoc[0], spriteLoc[1], float(spriteLoc[3]) + 50))