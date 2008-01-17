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
spawnPoints = 0

def load():
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
            
    # create commands
    if not es.exists('command','dm_add'):
        es.regcmd('dm_add','gungame/included_addons/gg_deathmatch/addSpawnPoint','Adds a spawnpoint to the current map.')
    if not es.exists('command','dm_del_all'):
        es.regcmd('dm_del_all','gungame/included_addons/gg_deathmatch/delAllSpawnPoints','Deletes all spawnpoint on the current map.')
    if not es.exists('command','dm_show'):
        es.regcmd('dm_show','gungame/included_addons/gg_deathmatch/showSpawnPoints','Shows all spawnpoint on the current map.')

    
    # Has map loaded?
    currentMap = str(es.ServerVar('eventscripts_currentmap'))
    if currentMap != '0':
        # Get spawn points, map loaded
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
        
    # watch for changes in deathmatch variables
    if dict_deathmatchVars.has_key(event_var['cvarname']):
        dict_deathmatchVars[event_var['cvarname']] = int(event_var['newvalue'])
        
    # Check if gg_knife_elite is running
    if event_var['cvarname'] == 'gg_knife_elite' and int(event_var['newvalue']) == 1:
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
        usermsg.hudhint(userid, 'Respawning in: 1 second.')
    else:
        usermsg.hudhint(userid, "Respawning in: %s seconds." % respawnCounters[userid])
    
    # Decrement the timer
    respawnCounters[userid] -= 1

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
    es.server.cmd('es_xgive %s env_entity_dissolver' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "target cs_ragdoll"' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "magnitude 1"' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "dissolvetype %s"' % (userid, dict_deathmatchVars['ragdoll_effect']))
    
    # Dissolve the ragdoll then kill the dissolver
    gamethread.delayed(2, es.server.cmd, 'es_xfire %s env_entity_dissolver Dissolve' % userid)
    gamethread.delayed(6, es.server.cmd, 'es_xfire %s env_entity_dissolver Kill' % userid)
    
def addSpawnPoint():
    #dm_add <userid>
    if int(es.getargc()) == 2:
        # check if userid is valid
        userid = int(es.getargv(1))
        if es.exists('userid', userid):
            #check if a map is loaded
            currentMap = str(es.ServerVar('eventscripts_currentmap'))
            if currentMap != '0':
                # get player location and viewing angles
                playerlibPlayer = playerlib.getPlayer(userid)
                playerLocation = es.getplayerlocation(userid)
                playerViewAngle = playerlibPlayer.get('viewangle')
                
                # write spawnpoints to file      
                spawnFile = open(os.getcwd() + '/cstrike/cfg/gungame/spawnpoints/' + currentMap + '.txt', 'a')
                spawnFile.write('%s %s %s %f %f\n' %(playerLocation[0], playerLocation[1], playerLocation[2], playerViewAngle[0], playerViewAngle[1]))
                spawnFile.close()
                
                # show a sprite at new spawnpoint location
                es.server.cmd('est_effect 11 %d 0 sprites/greenglow1.vmt %s %s %f 5 1 255' %(userid, playerLocation[0], playerLocation[1], float(playerLocation[2]) + 50))
                es.msg('#green', '[GG Deathmatch] Spawnpoint added')
        else:
            es.dbgmsg(0, '[GG Deathmatch] %d is not a valid userid' %userid)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def delAllSpawnPoints():
    #dm_del_all <userid>
    if int(es.getargc()) == 1:
        #check if a map is loaded
        currentMap = str(es.ServerVar('eventscripts_currentmap'))
        if currentMap != '0':
            # clear spawnpoint file
            spawnFile = open(os.getcwd() + '/cstrike/cfg/gungame/spawnpoints/' + currentMap + '.txt', 'w')
            spawnFile.close()
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def showSpawnPoints():
    #dm_del_all <userid>
    if int(es.getargc()) == 1:
        #check if a map is loaded
        currentMap = str(es.ServerVar('eventscripts_currentmap'))
        if currentMap != '0':
            userid = es.getuserid()
            IndexNumber = 0
            es.dbgmsg(0, '**** Spawnpoints Index ****')
            spawnFile = open(os.getcwd() + '/cstrike/cfg/gungame/spawnpoints/' + currentMap + '.txt', 'r')
            spawnFileLines = spawnFile.readlines()
            for line in spawnFileLines:
                line = line.strip()
                spriteLocation = line.split(' ')
                es.server.cmd('est_effect 11 %s 0 sprites/greenglow1.vmt %s %s %f 5 1 255' %(userid, spriteLocation[0], spriteLocation[1], float(spriteLocation[2]) + 50))
                IndexNumber += 1
                es.dbgmsg(0, '%d: %s %s %s %s %s' %(IndexNumber, spriteLocation[0], spriteLocation[1], spriteLocation[2], spriteLocation[3], spriteLocation[4]))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'