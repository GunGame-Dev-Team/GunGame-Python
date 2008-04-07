''' (c) 2008 by the GunGame Coding Team

    Title: gg_deathmatch
    Version: 1.0.258
    Description: Deathmatch addon for GunGame:Python
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
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
import keyvalues

# Gungame import
import gungamelib
from gungamelib import ArgumentError

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_deathmatch (for GunGame: Python)"
info.version  = '1.0.258'
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_deathmatch"
info.author   = "GunGame Development Team"

# ==============================================================================
#  GLOBALS
# ==============================================================================
# Variables
dict_variables = {}
dict_variables['delay'] = gungamelib.getVariable('gg_dm_respawn_delay')
dict_variables['cmd'] = gungamelib.getVariable('gg_dm_respawn_cmd')

# Globals
respawnCounters = {}
spawnPoints = {}
list_randomSpawnIndex = []

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_deathmatch = gungamelib.registerAddon('gg_deathmatch')
    gg_deathmatch.addDependency('gg_turbo', '1')
    gg_deathmatch.addDependency('gg_dead_strip', '1')
    gg_deathmatch.addDependency('gg_dissolver', '1')
    gg_deathmatch.addDependency('gg_map_obj', '0')
    gg_deathmatch.addDependency('gg_knife_elite', '0')
    gg_deathmatch.addDependency('gg_elimination', '0')
    
    # Menu settings
    gg_deathmatch.createMenu(menuCallback)
    gg_deathmatch.setDisplayName('GG Deathmatch')
    gg_deathmatch.setDescription('Deathmatch addon for GunGame:Python')
    gg_deathmatch.menu.addoption('spawn', 'Spawnpoint Management')
    
    # Do we have EST?
    if not gungamelib.hasEST():
        gungamelib.echo('gg_deathmatch', 0, 0, 'ESTWarning')
    
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
        es.regcmd('dm_remove','gungame/included_addons/gg_deathmatch/cmd_delSpawnPoint', 'Removes a single spawnpoint.')
    if not es.exists('command','dm_convert'):
        es.regcmd('dm_convert','gungame/included_addons/gg_deathmatch/cmd_convert', 'Converts legacy GGv3 spawnpoints into CSS:DM format.')
    
    # Has map loaded?
    if gungamelib.inLevel():
        # Get spawn points, map loaded
        getSpawnPoints(gungamelib.getLevelName())
    
    # Get a player list of dead players then spawn them
    for userid in playerlib.getUseridList('#dead'):
        respawn(userid)

    # Set freezetime
    es.server.cmd('mp_freezetime 0')
    es.server.cmd('mp_roundtime 900')

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_deathmatch')


def es_map_start(event_var):
    getSpawnPoints(event_var['mapname'])

def player_team(event_var):
    # Respawn the player
    if event_var['disconnect'] != '0':
        return
    
    # Get the userid
    userid = event_var['userid']
    
    # Respawn the player
    gamethread.delayed(5, es.server.cmd, ('%s %s' % (str(dict_variables['cmd']), userid)))
    
    # Tell them they will respawn soon
    gungamelib.msg('gg_deathmatch', userid, 'ConnectRespawnIn')

def player_death(event_var):
    # Remove their defuser
    gamethread.delayed(0.5, es.remove, ('item_defuser'))
    
    # Respawn the player
    respawn(event_var['userid'])

def player_spawn(event_var):
    global spawnPoints
    
    # Set vars
    userid = int(event_var['userid'])
    
    # Is a spectator?
    if gungamelib.isSpectator(userid) or gungamelib.isDead(userid):
        return
    
    # No-block for a second, to stop sticking inside other players
    collisionBefore = es.getplayerprop(userid, 'CBaseEntity.m_CollisionGroup')
    es.setplayerprop(userid, 'CBaseEntity.m_CollisionGroup', 17)
    gamethread.delayed(1.5, es.setplayerprop, (userid, 'CBaseEntity.m_CollisionGroup', collisionBefore))
    
    # Do we have a spawn point file?
    if spawnPoints:
        # Get a random spawn index
        if not list_randomSpawnIndex:
            for i in range(0, len(spawnPoints) - 1):
                list_randomSpawnIndex.append(i)
            random.shuffle(list_randomSpawnIndex)
        
        spawnindex = list_randomSpawnIndex.pop(0)
        
        # Teleport the player
        gungamelib.getPlayer(userid).teleportPlayer(spawnPoints[spawnindex][0],
                                                    spawnPoints[spawnindex][1],
                                                    spawnPoints[spawnindex][2],
                                                    0,
                                                    spawnPoints[spawnindex][4])

def round_start(event_var):
    # Loop through the players
    for userid in es.getUseridList():
        # Does a respawn countdown exist?
        if repeat.status('RespawnCounter%s' % userid):
            # Delete the respawn counter
            repeat.delete('RespawnCounter%s' % userid)

def player_disconnect(event_var):
    # Get userid
    userid = event_var['userid']
    
    # Remove the counter
    if repeat.status('RespawnCounter%s' % userid):
        repeat.delete('RespawnCounter%s' % userid)

# ==============================================================================
#  MENU COMMANDS
# ==============================================================================
def menuCallback(userid, choice, popupName):
    # TO-DO
    pass

# ==============================================================================
#  SPAWNPOINT HELPERS
# ==============================================================================
def getSpawnPoints(_mapName):
    global spawnPoints
    global spawnFile
    global spawnPointsExist
    
    # Open the file and clear the spawn point dictionary
    spawnPoints = {}
    spawnFile = gungamelib.getGameDir('cfg\\gungame\\spawnpoints\\%s.txt' % _mapName)
    spawnPointsExist = os.path.isfile(spawnFile)
    
    # Does the spawn file exist
    if not spawnPointsExist:
        gungamelib.echo('gg_deathmatch', 0, 0, 'NoSpawnpoints', {'map': _mapName})
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
    global spawnFile
    
    mapName = gungamelib.getLevelName()
    
    # Do we have a spawn point file?
    if not spawnPointsExist:
        # Create spawnpoint file
        spawnFile = gungamelib.getGameDir('cfg\\gungame\\spawnpoints\\%s.txt' % mapName)
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
    getSpawnPoints(gungamelib.getLevelName())

# ==============================================================================
#  RESPAWN CODE
# ==============================================================================
def RespawnCountdown(userid, repeatInfo):
    # Is it in warmup?
    if not int(gungamelib.getGlobal('isWarmup')) and not int(gungamelib.getGlobal('voteActive')):
        if respawnCounters[userid] > 1:
            gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_Plural', {'time': respawnCounters[userid]})
        # Is the counter 1?
        elif respawnCounters[userid] == 1:
            gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_Singular')
            
    # Respawn the player
    if respawnCounters[userid] == 0:
        es.server.cmd('%s %s' % (str(dict_variables['cmd']), userid))
        
    # Decrement the timer
    respawnCounters[userid] -= 1

def respawn(userid):
    # Tell the userid they are respawning
    respawnCounters[userid] = int(dict_variables['delay'])
    repeat.create('RespawnCounter%s' % userid, RespawnCountdown, (userid))
    repeat.start('RespawnCounter%s' % userid, 1, int(dict_variables['delay']) + 1)

# ==============================================================================
#  CONVERTION HELPERS
# ==============================================================================
def cmd_convert():
    # Do we have enough arguments?
    if int(es.getargc()) != 1:
        # Raise argument error
        raise ArgumentError, str(int(es.getargc()) - 1) + ' arguments provided. Expected: 0'
    
    # Loop through the files in the legacy folder
    for f in os.listdir(gungamelib.getGameDir('cfg\\gungame\\spawnpoints\\legacy')):
        name, ext = os.path.splitext(f)
        
        if name.startswith('es_') and name.endswith('_db') and ext == '.txt':            
            # Announce we are parsing it
            gungamelib.echo('gg_deathmatch', 0, 0, 'ConvertingFile', {'file': f})
            
            # Parse it
            points = parseLegacySpawnpoint(gungamelib.getGameDir('cfg\\gungame\\spawnpoints\\legacy\\') + f)
            
            # Now write it to a file
            newFileName = name[3:][:-3]
            newFile = open(gungamelib.getGameDir('cfg\\gungame\\spawnpoints\\%s.txt') % newFileName, 'w')
            
            # Are there any points?
            if len(points) == 0:
                gungamelib.echo('gg_deathmatch', 0, 0, 'CannotConvert_Skipping')
                continue
            
            # Loop through the points
            for point in points:
                newFile.write('%s %s %s 0.000000 0.000000 0.000000\n' % (points[point][0], points[point][1], points[point][2]))
                
            # Close the file and flush
            newFile.close()
            
    # Announce that all files have been converted
    gungamelib.echo('gg_deathmatch', 0, 0, 'ConvertingCompleted')

def parseLegacySpawnpoint(file):
    # Create vars
    points = {}

    # Load the keygroup file
    kv = keyvalues.KeyValues(name=file.strip('es_').strip('_db.txt'))
    kv.load(file)
    
    # Get the total points
    try:
        totalVals = kv['total']['total']
    except KeyError:
        gungamelib.echo('gg_deathmatch', 0, 0, 'CannotConvert_NoTotal')
        return {}
    
    # Loop through the values
    i = 0
    while i < totalVals:
        # Increment
        i += 1
        
        # Try to get the points
        try:
            toSplit = kv['points'][str(i)]
        except KeyError:
            gungamelib.echo('gg_deathmatch', 0, 0, 'CannotConvert_InvalidTotal')
            return {}
        
        # Split it
        points[i] = toSplit.split(',')
    
    # Return
    return points

# ==============================================================================
#  CONSOLE FUNCTIONS
# ==============================================================================
def cmd_addSpawnPoint():
    global spawnPoints
    
    # Do we have enough arguments?
    if int(es.getargc()) != 2:
        gungamelib.echo('gg_deathmatch', 0, 0, 'InvalidSyntax', {'cmd': 'dm_show', 'syntax': '<userid>'})
        return
    
    # Get executor userid and 1st argument
    userid = int(es.getargv(1))
    
    # Does the userid exist?
    if not gungamelib.clientInServer(userid):
        gungamelib.echo('gg_deathmatch', 0, 0, 'CannotCreateSpawnpoint', {'userid': userid})
        return
    
    # Is a map loaded?
    if gungamelib.inLevel():
        # Get player location and viewing angles
        playerlibPlayer = playerlib.getPlayer(userid)
        playerLoc = es.getplayerlocation(userid)
        playerViewAngle = playerlibPlayer.get('viewangle')
        
        # Add spawn point
        addSpawnPoint(playerLoc[0], playerLoc[1], playerLoc[2], playerViewAngle[1])
        
        # Show a sprite at the new spawnpoint location
        es.server.cmd('est_effect 11 %d 0 sprites/greenglow1.vmt %s %s %f 5 1 255' % (userid, playerLoc[0], playerLoc[1], float(playerLoc[2]) + 50))
        
        # Tell the user where the spawnpoint is, and the index
        gungamelib.msg('gg_deathmatch', userid, 'AddedSpawnpoint', {'index': len(spawnPoints) - 1})

def cmd_delAllSpawnPoints():
    mapName = gungamelib.getLevelName()
    
    # Enough arguments?
    if int(es.getargc()) != 1:
        gungamelib.echo('gg_deathmatch', 0, 0, 'InvalidSyntax', {'cmd': 'dm_del_all', 'syntax': ''})
        return
    
    # Check if a map is loaded
    if gungamelib.inLevel():
        # Clear the spawnpoint file
        spawnFile = open(gungamelib.getGameDir('cfg\\gungame\\spawnpoints\\%s.txt' % mapName), 'w').close()
        
        # Get spawnpoints
        getSpawnPoints(mapName)

def cmd_printSpawnPoints():
    mapName = gungamelib.getLevelName()
    
    # Enough arguments?
    if int(es.getargc()) != 1:
        gungamelib.echo('gg_deathmatch', 0, 0, 'InvalidSyntax', {'cmd': 'dm_print', 'syntax': ''})
        return
    
    # Do we have spawnpoints?
    if spawnPoints == 0:
        gungamelib.echo('gg_deathmatch', 0, 0, 'NoSpawnpointsToShow')
    
    # Send message
    gungamelib.echo('gg_deathmatch', 0, 0, 'SpawnpointsFor', {'map': mapName})
    
    # Loop through the spawnpoints
    for index in spawnPoints:
        # Get list
        spawnLoc = spawnPoints[index]
        
        # Print to console
        gungamelib.echo('gg_deathmatch', 0, 0, 'SpawnpointInfo', {'index': index, 'x': spawnLoc[0], 'y': spawnLoc[1], 'z': spawnLoc[2]})
    
    # Send end message
    gungamelib.echo('gg_deathmatch', 0, 0, 'SpawnpointsEnd')

def cmd_delSpawnPoint():
    # Enough arguments?
    if int(es.getargc()) != 2:
        gungamelib.echo('gg_deathmatch', 0, 0, 'InvalidSyntax', {'cmd': 'dm_del', 'syntax': '<index>'})
        return
    
    # Delete the spawn point
    removeSpawnPoint(int(es.getargv(1)))
    
    # Print to console
    gungamelib.echo('gg_deathmatch', 0, 0, 'RemovedSpawnpoint', {'index': es.getargv(1)})

def cmd_showSpawnPoints():
    # Do we have enough arguments?
    if int(es.getargc()) != 2:
        gungamelib.echo('gg_deathmatch', 0, 0, 'InvalidSyntax', {'cmd': 'dm_show', 'syntax': '<userid>'})
        return
    
    # Set vars
    userid = es.getargv(1)
    
    # Do we have spawnpoints?
    if spawnPoints == 0:
        gungamelib.echo('gg_deathmatch', 0, 0, 'NoSpawnpointsToShow')
    
    # Loop through spawn points
    for index in spawnPoints:
        # Get list
        spriteLoc = spawnPoints[index]
        
        # Create sprite
        es.server.cmd('est_effect 11 %s 0 sprites/greenglow1.vmt %s %s %f 5 1 255' % (userid, spriteLoc[0], spriteLoc[1], float(spriteLoc[3]) + 50))