''' (c) 2008 by the GunGame Coding Team

    Title: gg_deathmatch
    Version: 1.0.316
    Description: Deathmatch addon for GunGame:Python
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python imports
import os.path
import string
import random

# Eventscripts imports
import es
import playerlib
import popuplib
import gamethread
import repeat
import usermsg
import keyvalues

# Gungame import
import gungamelib
from gungamelib import ArgumentError

# ==============================================================================
#   ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_deathmatch (for GunGame: Python)'
info.version  = '1.0.316'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_deathmatch'
info.author   = 'GunGame Development Team'

# ==============================================================================
#   GLOBALS
# ==============================================================================
# Variables
dict_variables = {}
dict_variables['delay'] = gungamelib.getVariable('gg_dm_respawn_delay')
dict_variables['cmd'] = gungamelib.getVariable('gg_dm_respawn_cmd')

# Globals
respawnCounters = {}
spawnPoints = {}
list_randomSpawnIndex = []
respawnAllowed = True

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_deathmatch = gungamelib.registerAddon('gg_deathmatch')
    gg_deathmatch.addDependency('gg_turbo', 1)
    gg_deathmatch.addDependency('gg_dead_strip', 1)
    gg_deathmatch.addDependency('gg_dissolver', 1)
    gg_deathmatch.addDependency('gg_map_obj', 0)
    gg_deathmatch.addDependency('gg_knife_elite', 0)
    gg_deathmatch.addDependency('gg_elimination', 0)
    
    # Menu settings
    gg_deathmatch.createMenu(menuCallback)
    gg_deathmatch.setDisplayName('GG Deathmatch')
    gg_deathmatch.setDescription('Deathmatch addon for GunGame:Python')
    gg_deathmatch.menu.addoption('add', 'Add spawnpoint')
    gg_deathmatch.menu.addoption('remove', 'Remove spawnpoint')
    gg_deathmatch.menu.addoption('remove_all', 'Remove all spawnpoints')
    gg_deathmatch.menu.addoption('show', 'Show all spawnpoints')
    
    # Commands
    gg_deathmatch.registerCommand('dm_add', cmd_dm_add, '<players userid to from>')
    gg_deathmatch.registerCommand('dm_remove', cmd_dm_remove, '<index>')
    gg_deathmatch.registerCommand('dm_remove_all', cmd_dm_remove_all)
    gg_deathmatch.registerCommand('dm_show', cmd_dm_show)
    gg_deathmatch.registerCommand('dm_print', cmd_dm_print)
    gg_deathmatch.registerCommand('dm_convert', cmd_dm_convert)
    
    # Do we have EST?
    if not gungamelib.hasEST():
        gungamelib.echo('gg_deathmatch', 0, 0, 'ESTWarning')
    
    # Has map loaded?
    if gungamelib.inMap():
        # Get spawn points, map loaded
        getSpawnPoints(gungamelib.getMapName())
    
    # Get a player list of dead players then spawn them
    for userid in playerlib.getUseridList('#dead'):
        respawn(userid)
    
    # Set freezetime and roundtime
    es.server.cmd('mp_freezetime 0')
    es.server.cmd('mp_roundtime 900')

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_deathmatch')


def es_map_start(event_var):
    global respawnAllowed
    
    # Get spawnpoints and allow respawns
    getSpawnPoints(event_var['mapname'])
    respawnAllowed = False

def player_team(event_var):
    # Don't allow it if people are disconnecting
    if event_var['disconnect'] != '0':
        return
    
    # Don't allow spectators
    if event_var['team'] == '1':
        return
    
    # Get the userid
    userid = int(event_var['userid'])
    
    # Respawn the player
    respawn(userid)
    
    # Tell them they will respawn soon
    gungamelib.msg('gg_deathmatch', userid, 'ConnectRespawnIn')

def player_death(event_var):
    global respawnAllowed
    
    # Remove their defuser
    gamethread.delayed(0.5, es.remove, ('item_defuser'))
    
    # Respawn the player if the round hasn't ended
    if respawnAllowed:
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
    
    # Skip if we dont have spawnpoints
    if not spawnPoints:
        return
    
    # Sort out the random spawn indexes
    if not list_randomSpawnIndex:
        # Get the spawnpoints
        for i in range(0, len(spawnPoints)):
            list_randomSpawnIndex.append(i)
        
        # Shuffle shuffle
        random.shuffle(list_randomSpawnIndex)
    
    # Get the last spawnpoint
    spawnindex = list_randomSpawnIndex.pop()
    
    # Teleport the player
    gungamelib.getPlayer(userid).teleportPlayer(spawnPoints[spawnindex][0],
                                                spawnPoints[spawnindex][1],
                                                spawnPoints[spawnindex][2],
                                                0,
                                                spawnPoints[spawnindex][4])

def round_end(event_var):
    global respawnAllowed
    
    # Don't allow respawn
    respawnAllowed = False
    
    # Stop everyones respawn counters
    for userid in es.getUseridList():
        if repeat.status('RespawnCounter%s' % userid): repeat.delete('RespawnCounter%s' % userid)

def round_start(event_var):
    global respawnAllowed
    
    # Allow respawn
    respawnAllowed = True
    
    # Stop everyones respawn counters
    for userid in es.getUseridList():
        if repeat.status('RespawnCounter%s' % userid): repeat.delete('RespawnCounter%s' % userid)

def player_disconnect(event_var):
    # Get userid
    userid = event_var['userid']
    
    # Remove the counter
    if repeat.status('RespawnCounter%s' % userid): repeat.delete('RespawnCounter%s' % userid)

# ==============================================================================
#   COMMANDS
# ==============================================================================
def cmd_dm_add(userid, location):
    global spawnPoints
    
    # Does the userid exist?
    if not gungamelib.clientInServer(location):
        gungamelib.echo('gg_deathmatch', userid, 0, 'CannotCreateSpawnpoint', {'userid': location})
        return
    
    # Is a map loaded?
    if gungamelib.inMap():
        # Get player location and viewing angles
        playerlibPlayer = playerlib.getPlayer(location)
        playerLoc = es.getplayerlocation(location)
        playerViewAngle = playerlibPlayer.get('viewangle')
        
        # Add spawn point
        addSpawnPoint(playerLoc[0], playerLoc[1], playerLoc[2], playerViewAngle[1])
        
        # Show a sprite at the new spawnpoint location
        es.server.cmd('est_effect 11 %d 0 sprites/greenglow1.vmt %s %s %f 5 1 255' % (userid, playerLoc[0], playerLoc[1], float(playerLoc[2]) + 50))
        
        # Tell the user where the spawnpoint is, and the index
        gungamelib.msg('gg_deathmatch', userid, 'AddedSpawnpoint', {'index': len(spawnPoints) - 1})

def cmd_dm_remove_all(userid):
    mapName = gungamelib.getMapName()
    
    # Check if a map is loaded
    if gungamelib.inMap():
        # Clear the spawnpoint file
        spawnFile = open(gungamelib.getGameDir('cfg/gungame/spawnpoints/%s.txt' % mapName), 'w').close()
        
        # Get spawnpoints
        getSpawnPoints(mapName)
        
        # Tell them the spawnpoints are removed
        gungamelib.msg('gg_deathmatch', userid, 'RemovedAllSpawnpoints')

def cmd_dm_print(userid):
    # Get map name
    mapName = gungamelib.getMapName()
    
    gungamelib.msg('gungame', userid, 'CheckYourConsole')
    
    # Do we have spawnpoints?
    if not spawnPoints:
        gungamelib.msg('gg_deathmatch', userid, 'NoSpawnpointsToShow')
        return
    
    # Send message
    gungamelib.echo('gg_deathmatch', userid, 0, 'SpawnpointsFor', {'map': mapName})
    
    # Loop through the spawnpoints
    for index in spawnPoints:
        # Get list
        spawnLoc = spawnPoints[index]
        
        # Print to console
        gungamelib.echo('gg_deathmatch', userid, 0, 'SpawnpointInfo', {'index': index, 'x': spawnLoc[0], 'y': spawnLoc[1], 'z': spawnLoc[2]})
    
    # Send end message
    gungamelib.echo('gg_deathmatch', userid, 0, 'SpawnpointsEnd')

def cmd_dm_remove(userid, index):
    # Delete the spawn point
    removeSpawnPoint(int(index))
    
    # Print to console
    gungamelib.msg('gg_deathmatch', userid, 'RemovedSpawnpoint', {'index': index})

def cmd_dm_show(userid):
    # Do we have spawnpoints?
    if not spawnPoints:
        gungamelib.msg('gg_deathmatch', userid, 'NoSpawnpointsToShow')
        return
    
    # Loop through spawn points
    for index in spawnPoints:
        # Get list
        spriteLoc = spawnPoints[index]
        
        # Create sprite
        es.server.cmd('est_effect 11 %s 0 sprites/greenglow1.vmt %f %f %f 5 1 255' % (userid, spriteLoc[0], spriteLoc[1], float(spriteLoc[2]) + 50))

# ==============================================================================
#   MENU COMMANDS
# ==============================================================================
def menuCallback(userid, choice, popupid):
    if choice == 'add':
        sendAddMenu(userid)
    elif choice == 'remove':
        sendRemoveMenu(userid)
    elif choice == 'remove_all':
        sendRemoveAllMenu(userid)
    elif choice == 'show':
        sendShowMenu(userid)

def sendAddMenu(userid):
    # Create menu
    menu = popuplib.easymenu('gg_deathmatch_add', None, selectAddMenu)
    menu.settitle('GG Deathmatch: Add a spawnpoint')
    menu.setdescription('%s\n * Add a spawnpoint at which location' % menu.c_beginsep)
    
    # Add them to the menu
    menu.addoption(userid, '<Current Location>')
    
    # All all players to the menu
    for _userid in filter(lambda x: x != userid, playerlib.getUseridList('#all')):
        menu.addoption(_userid, '%s - %s' % (_userid, es.getplayername(_userid)))
    
    # Send menu
    menu.send(userid)

def selectAddMenu(userid, choice, popupid):
    # Get view angles etc.
    viewAngle = playerlib.getPlayer(choice).get('viewangle')[1]
    x, y, z = es.getplayerlocation(choice)
    cmd_dm_add(userid, choice)
    # Add spawnpoint
    addSpawnPoint(x, y, z, viewAngle)
    gungamelib.msg('gg_deathmatch', userid, 'AddedSpawnpoint', {'index': len(spawnPoints)-1})
    
    # Log
    gungamelib.msg('gg_deathmatch', '#all', 'PlayerExecuted', {'userid': userid, 'name': es.getplayername(userid), 'steamid': es.getplayersteamid(userid), 'info': 'added spawnpoint at %s\'s location.' % es.getplayername(choice)})
    
    # Return to main menu
    popuplib.send('gg_deathmatch', userid)


def sendRemoveMenu(userid):
    # Create menu
    menu = popuplib.easymenu('gg_deathmatch_remove', None, selectRemoveMenu)
    menu.settitle('GG Deathmatch: Remove a spawnpoint')
    menu.setdescription('%s\n * Remove a spawnpoint by index' % menu.c_beginsep)
    
    # All all players to the menu
    for index in spawnPoints:
        # Get location
        x, y, z, unknown, roll, yaw = spawnPoints[index]
        
        # Add option
        menu.addoption(index, '%s - X:%s Y:%s Z:%s' % (index, x, y, z))
    
    # Send menu
    menu.send(userid)

def selectRemoveMenu(userid, choice, popupid):
    # Get their position
    position = es.getplayerlocation(userid)
    
    # Teleport them
    gungamelib.getPlayer(userid).teleportPlayer(spawnPoints[choice][0],
                                                spawnPoints[choice][1],
                                                spawnPoints[choice][2],
                                                0,
                                                spawnPoints[choice][4])
    
    # Create menu
    menu = popuplib.easymenu('gg_deathmatch_remove_confirm', None, selectRemoveConfirmMenu)
    menu.settitle('GG Deathmatch: Remove this spawnpoint?')
    menu.setdescription('%s\n * Do you want to remove this spawnpoint?' % menu.c_beginsep)
    
    # Add options
    menu.addoption((choice, position), 'Yes, delete spawnpoint "%s".' % choice)
    menu.addoption((-1, position), 'No, return me to the previous menu.')
    
    # Send menu
    menu.send(userid)

def selectRemoveConfirmMenu(userid, choice, popupid):
    if choice[0] == -1:
        # Teleport them back
        gungamelib.getPlayer(userid).teleportPlayer(choice[1][0],
                                                    choice[1][1],
                                                    choice[1][2],
                                                    0,
                                                    0)
        
        # Send them the previous menu
        popuplib.send('gg_deathmatch_remove', userid)
    else:
        # Teleport them back
        gungamelib.getPlayer(userid).teleportPlayer(choice[1][0],
                                                    choice[1][1],
                                                    choice[1][2],
                                                    0,
                                                    0)
        
        # Remove the spawnpoint
        gungamelib.msg('gg_deathmatch', '#all', 'PlayerExecuted', {'userid': userid, 'name': es.getplayername(userid), 'steamid': es.getplayersteamid(userid), 'info': 'removed spawnpoint %s' % choice[0]})
        gungamelib.msg('gg_deathmatch', userid, 'RemovedSpawnpoint', {'index': choice[0]})
        removeSpawnPoint(choice[0])
        
        # Send menu
        popuplib.send('gg_deathmatch', userid)


def sendRemoveAllMenu(userid):
    # Create menu
    menu = popuplib.easymenu('gg_deathmatch_remove_all_confirm', None, selectRemoveAllMenu)
    menu.settitle('GG Deathmatch: Remove all spawnpoints?')
    menu.setdescription('%s\n * Confirmation menu' % menu.c_beginsep)
    
    # Add options
    menu.addoption(1, 'Yes, remove all spawnpoints.')
    menu.addoption(0, 'No, return me to the main menu.')
    
    # Send
    menu.send(userid)

def selectRemoveAllMenu(userid, choice, popupid):
    if choice == 1:
        # Log
        gungamelib.msg('gg_deathmatch', '#all', 'PlayerExecuted', {'userid': userid, 'name': es.getplayername(userid), 'steamid': es.getplayersteamid(userid), 'info': 'removed all spawnpoints'})
        
        # Delete all spawnpoints
        es.server.cmd('dm_del_all')
        
        # Send them the main menu
        popuplib.send('gg_deathmatch', userid)
    else:
        popuplib.send('gg_deathmatch', userid)

def sendShowMenu(userid):
    # Create menu
    menu = popuplib.easymenu('gg_deathmatch_show', None, selectShowMenu)
    menu.settitle('GG Deathmatch: Show spawnpoints')
    menu.setdescription('%s\n * Select a player to show spawnpoints to' % menu.c_beginsep)
    
    # Add them to the menu
    menu.addoption(userid, '<Me>')
    
    # All all players to the menu
    for _userid in filter(lambda x: x != userid, playerlib.getUseridList('#all')):
        menu.addoption(_userid, '%s - %s' % (_userid, es.getplayername(_userid)))
    
    # Send menu
    menu.send(userid)

def selectShowMenu(userid, choice, popupid):
    # Log
    es.server.cmd('dm_show %s' % choice)
    
    # Return them
    popuplib.send('gg_deathmatch', userid)

# ==============================================================================
#   SPAWNPOINT HELPERS
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
    
    mapName = gungamelib.getMapName()
    
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
        spawnPointFile.write('%f %f %f 0.000000 %f 0.000000\n' % (spawnLoc[0], spawnLoc[1], spawnLoc[2], spawnLoc[4]))
    
    # Flush and close the file
    spawnPointFile.flush()
    spawnPointFile.close()

    # Get spawnpoints again
    getSpawnPoints(gungamelib.getMapName())

# ==============================================================================
#   RESPAWN CODE
# ==============================================================================
def RespawnCountdown(userid, repeatInfo):
    # Is it in warmup?
    if not int(gungamelib.getGlobal('isWarmup')) and not int(gungamelib.getGlobal('voteActive')):
        # Send respawn message
        if respawnCounters[userid] > 1:
            gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_Plural', {'time': respawnCounters[userid]})
        
        # Is the counter at 1?
        elif respawnCounters[userid] == 1:
            gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_Singular')
    
    # Respawn the player
    if respawnCounters[userid] == 0:
        es.server.cmd('%s %s' % (str(dict_variables['cmd']), userid))
    
    # Decrement the timer
    respawnCounters[userid] -= 1

def respawn(userid):
    # Add a respawn counter for them
    respawnCounters[userid] = int(dict_variables['delay'])
    
    # Is there a respawn counter already running?
    if repeat.status('RespawnCounter%s' % userid):
        repeat.delete('RespawnCounter%s' % userid)
    
    # Create and start the spawn counter
    repeat.create('RespawnCounter%s' % userid, RespawnCountdown, (userid))
    repeat.start('RespawnCounter%s' % userid, 1, int(dict_variables['delay']) + 1)

# ==============================================================================
#   CONVERTION HELPERS
# ==============================================================================
def cmd_dm_convert(userid):
    # Tell them to check their console
    gungamelib.msg('gungame', userid, 'CheckYourConsole')
    
    # Loop through the files in the legacy folder
    for f in os.listdir(gungamelib.getGameDir('cfg/gungame/spawnpoints/legacy')):
        name, ext = os.path.splitext(f)
        
        if name.startswith('es_') and name.endswith('_db') and ext == '.txt':            
            # Announce we are parsing it
            gungamelib.echo('gg_deathmatch', userid, 0, 'ConvertingFile', {'file': f})
            
            # Parse it
            points = parseLegacySpawnpoint(gungamelib.getGameDir('cfg/gungame/spawnpoints/legacy/%s' % f))
            
            # Are there any points?
            if len(points) == 0:
                gungamelib.echo('gg_deathmatch', userid, 0, 'CannotConvert_Skipping')
                continue
            
            # Now write it to a file
            newFileName = name[3:-3]
            newFile = open(gungamelib.getGameDir('cfg/gungame/spawnpoints/%s.txt' % newFileName), 'w')
            
            # Loop through the points
            for point in points:
                newFile.write('%s %s %s 0.000000 0.000000 0.000000\n' % (points[point][0], points[point][1], points[point][2]))
            
            # Close the file and flush
            newFile.close()
    
    # Announce that all files have been converted
    gungamelib.echo('gg_deathmatch', userid, 0, 'ConvertingCompleted')

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