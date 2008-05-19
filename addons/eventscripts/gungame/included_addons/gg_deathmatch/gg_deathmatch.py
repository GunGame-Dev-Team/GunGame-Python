''' (c) 2008 by the GunGame Coding Team

    Title: gg_deathmatch
    Version: 1.0.321
    Description: Team-deathmatch mod for GunGame.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts Imports
import es
import playerlib
import gamethread
import popuplib
import testrepeat as repeat

# Python Imports
import os
import random

# GunGame Imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_deathmatch (for GunGame: Python)'
info.version  = '1.0.321'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_deathmatch'
info.author   = 'GunGame Development Team'
    
# ==============================================================================
#  GLOBALS
# ==============================================================================
model = 'player/ct_gign.mdl'
spawnPoints = None

# ==============================================================================
#   ERROR CLASSES
# ==============================================================================
class SpawnPointError(Exception):
    pass

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    global spawnPoints
    
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
    
    # Get the spawn points for the map
    if gungamelib.inMap():
        spawnPoints = SpawnPointManager()
    
    # Respawn all dead players
    for userid in playerlib.getUseridList('#dead'):
        repeat.start('respawnPlayer%s' % userid, 1, gungamelib.getVariable('gg_dm_respawn_delay'))
    
    # Set freezetime and roundtime
    es.server.cmd('mp_freezetime 0')
    es.server.cmd('mp_roundtime 900')
    
def unload():
    global spawnPoints
    
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_deathmatch')
    
    # Delete all player respawns
    for userid in es.getUseridList():
        repeat.delete('respawnPlayer%s' % userid)
    
    # Un-show the spawnpoints
    if spawnPoints.getShow():
        spawnPoints.show(0)


def es_map_start(event_var):
    global spawnPoints
    
    # Don't allow respawn
    gungamelib.setGlobal('respawn_allowed', 0)
    
    # Reset spawnpoints
    spawnPoints = SpawnPointManager()
    
def player_team(event_var):
    if event_var['disconnect'] != '0':
        return
    
    # Get the userid
    userid = event_var['userid']
    
    # If the player does not have a respawn repeat, create one
    respawnPlayer = repeat.find('respawnPlayer%s' % userid)
    if not respawnPlayer:
        repeat.create('respawnPlayer%s' % userid, respawnCountDown, (userid))
    
    # Don't allow spectators or players that are unassigned to respawn
    if int(event_var['team']) < 2:
        if repeat.status('respawnPlayer%s' % userid) != 1:
            repeat.stop('respawnPlayer%s' % userid)
            
            if gungamelib.canShowHints():
                gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_CancelTeam')
        
        return
    
    # Respawn the player
    repeat.start('respawnPlayer%s' % userid, 1, gungamelib.getVariable('gg_dm_respawn_delay'))
    
def player_spawn(event_var):
    global spawnPoints
    
    # Get the userid
    userid = int(event_var['userid'])
    
    # Is a spectator?
    if gungamelib.isSpectator(userid) or gungamelib.isDead(userid):
        return
    
    # No-block for a second, to stop sticking inside other players
    collisionBefore = es.getplayerprop(userid, 'CBaseEntity.m_CollisionGroup')
    es.setplayerprop(userid, 'CBaseEntity.m_CollisionGroup', 17)
    gamethread.delayed(1.5, es.setplayerprop, (userid, 'CBaseEntity.m_CollisionGroup', collisionBefore))
    
    # Do not continue if we have no spawn points
    if not spawnPoints.hasPoints():
        return
    
    # Teleport the player
    s = spawnPoints.getRandomPoint()
    gungamelib.getPlayer(userid).teleportPlayer(s[0], s[1], s[2], 0, s[4])
    
def player_death(event_var):
    # Get the userid
    userid = event_var['userid']
    
    # Remove defuser
    if playerlib.getPlayer(userid).get('defuser'):
        gamethread.delayed(0.5, es.remove, ('item_defuser'))
    
    # Respawn the player if the round hasn't ended
    if gungamelib.getGlobal('respawn_allowed'):
        repeat.start('respawnPlayer%s' % userid, 1, gungamelib.getVariable('gg_dm_respawn_delay'))

def player_disconnect(event_var):
    # Get userid
    userid = event_var['userid']
    
    # Delete the player-specific repeat
    if repeat.find('respawnPlayer%s' % userid):
        repeat.delete('respawnPlayer%s' % userid)
    
def round_start(event_var):
    global spawnPoints
    
    # Reset spawnpoints
    if spawnPoints.getShow():
        spawnPoints.__resetProps()
    
    # Allow respawn
    gungamelib.setGlobal('respawn_allowed', 1)
    
def round_end(event_var):
    # Don't allow respawn
    gungamelib.setGlobal('respawn_allowed', 0)
    
    # DEVS: Is this code necassary? It is already handled in the respawn counter
    #       code...
    #
    #for userid in es.getUseridList():
    #    playerRespawn = repeat.find('respawnPlayer%s' % userid)
    #    
    #    if not playerRespawn:
    #        continue
    #    
    #    if playerRespawn.status() != 1:
    #        gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_RoundEnd')
    
def respawnCountDown(userid):
    # Make sure that the repeat exists
    respawnRepeat = repeat.find('respawnPlayer%s' %userid)
    if not respawnRepeat:
        return
    
    # Not dead?
    if not gungamelib.isDead(userid):
        respawnRepeat.stop()
        return
    
    # Round finished?
    if gungamelib.getGlobal('respawn_allowed') == 0:
        # Tell them the round has ended
        if gungamelib.canShowHints():
            gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_RoundEnded')
        
        respawnRepeat.stop()
        return
    
    # Allow to show HUDHints?
    if gungamelib.canShowHints():
        # More than 1 remaining?
        if respawnRepeat['remaining'] > 1:
            gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_Plural', {'time': respawnRepeat['remaining']})
        
        # Is the counter 1?
        elif respawnRepeat['remaining'] == 1:
            gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_Singular')
    
    # Respawn the player
    if respawnRepeat['remaining'] == 0:
        es.server.cmd('%s %s' % (gungamelib.getVariable('gg_dm_respawn_cmd'), userid))

# ==============================================================================
#   COMMANDS
# ==============================================================================
def cmd_dm_add(userid, location):
    global spawnPoints
    
    # In map?
    if not gungamelib.inMap():
        return
    
    # Does the userid exist?
    if not gungamelib.clientInServer(location):
        gungamelib.echo('gg_deathmatch', userid, 0, 'CannotCreateSpawnpoint', {'userid': location})
        return
    
    # Get player info
    playerlibPlayer = playerlib.getPlayer(location)
    playerLoc = es.getplayerlocation(location)
    playerViewAngle = playerlibPlayer.get('viewangle')
    
    # Create spawnpoint
    spawnPoints.add(playerLoc[0], playerLoc[1], playerLoc[2], playerViewAngle[1])
    
    gungamelib.msg('gg_deathmatch', userid, 'AddedSpawnpoint', {'index': spawnPoints.getTotalPoints()-1})

def cmd_dm_remove_all(userid):
    global spawnPoints
    
    # In map?
    if not gungamelib.inMap():
        return
    
    # Do we have spawnpoints?
    if not spawnPoints.hasPoints():
        gungamelib.msg('gg_deathmatch', userid, 'OperationFailed:NoSpawnpoints')
        return
    
    # Remove spawnpoints
    spawnPoints.deleteAll()
    
    gungamelib.msg('gg_deathmatch', userid, 'RemovedAllSpawnpoints')

def cmd_dm_print(userid):
    global spawnPoints
    
    # In map?
    if not gungamelib.inMap():
        return
    
    # Do we have spawnpoints?
    if not spawnPoints.hasPoints():
        gungamelib.msg('gg_deathmatch', userid, 'OperationFailed:NoSpawnpoints')
        return
    
    # Send message
    gungamelib.echo('gg_deathmatch', userid, 0, 'SpawnpointsFor', {'map': gungamelib.getMapName()})
    
    # Loop through the spawnpoints
    for index in spawnPoints:
        # Get list
        spawnLoc = spawnPoints[index]
        
        # Print to console
        gungamelib.echo('gg_deathmatch', userid, 0, 'SpawnpointInfo', {'index': index, 'x': spawnLoc[0], 'y': spawnLoc[1], 'z': spawnLoc[2]})
    
    # Send end message
    gungamelib.echo('gg_deathmatch', userid, 0, 'SpawnpointsEnd')

def cmd_dm_remove(userid, index):
    global spawnPoints
    
    # In map?
    if not gungamelib.inMap():
        return
    
    # Do we have spawnpoints?
    if not spawnPoints.hasPoints():
        gungamelib.msg('gg_deathmatch', userid, 'OperationFailed:NoSpawnpoints')
        return
    
    # Invalid index?
    if int(index) > spawnPoints.getTotalPoints():
        gungamelib.msg('gg_deathmatch', userid, 'InvalidIndex')
        return
    
    spawnPoints.delete(int(index))
    
    # Print to console
    gungamelib.msg('gg_deathmatch', userid, 'RemovedSpawnpoint', {'index': index})

def cmd_dm_show(userid, toggle=None):
    global spawnPoints
    
    # In map?
    if not gungamelib.inMap():
        return
    
    # Do we have spawnpoints?
    if not spawnPoints.hasPoints():
        gungamelib.msg('gg_deathmatch', userid, 'OperationFailed:NoSpawnpoints')
        return
    
    spawnPoints.show(toggle)


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
    # Add spawnpoint
    es.sexec(userid, 'gg_dm_add %s' % choice)
    
    # Return to main menu
    popuplib.send('gg_deathmatch', userid)


def sendRemoveMenu(userid):
    global spawnPoints
    
    # Create menu
    menu = popuplib.easymenu('gg_deathmatch_remove', None, selectRemoveMenu)
    menu.settitle('GG Deathmatch: Remove a spawnpoint')
    menu.setdescription('%s\n * Remove a spawnpoint by index' % menu.c_beginsep)
    
    # All all players to the menu
    for index in spawnPoints.dict_spawnPoints:
        # Get location
        x, y, z, unused, roll, yaw = spawnPoints.dict_spawnPoints[index]
        
        # Add option
        menu.addoption(index, '%s - X: %s Y: %s Z: %s' % (index, round(x), round(y), round(z)))
    
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
        
        # Remove spawnpoint
        es.sexec(userid, 'gg_dm_remove %s' % choice[0])
        
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
        # Delete spawnpoint
        es.sexec(userid, 'gg_dm_remove_all')
        
        # Send them the main menu
        popuplib.send('gg_deathmatch', userid)
    else:
        popuplib.send('gg_deathmatch', userid)

def sendShowMenu(userid):
    # Create menu
    menu = popuplib.easymenu('gg_deathmatch_show', None, selectShowMenu)
    menu.settitle('GG Deathmatch: Show spawnpoints')
    menu.setdescription('%s\n * Select a state' % menu.c_beginsep)
    
    # Add options
    menu.addoption(0, 'Hide spawnpoint models')
    menu.addoption(1, 'Show spawnpoint models')
    menu.addoption(None, 'Toggle from current state')
    
    # Send menu
    menu.send(userid)

def selectShowMenu(userid, choice, popupid):
    # Execute command
    es.sexec(userid, 'gg_dm_show %s' % (choice if choice else ''))
    
    # Return them
    popuplib.send('gg_deathmatch', userid)

# ==============================================================================
#   CONVERSION HELPERS
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

# ==============================================================================
#   SPAWN POINT CLASS
# ==============================================================================
class SpawnPointManager(object):
    '''Manages all spawnpoints. This class is only usable when in a map, if this
    class is initializes when not in map, SpawnPointError will be raised.'''
    
    dict_spawnPoints = {}
    list_randomSpawnPointManager = []
    list_spawnEntityIndexes = []
    list_spawnPointIndexes = []
    dict_propIndex = {}
    showToggle = 0
    lineCount = 0
    
    def __init__(self):
        # Get map name
        self.mapName = gungamelib.getMapName()
        
        # Make sure we are currently in a map
        if not gungamelib.inMap():
            raise SpawnPointError('Unable to retrieve spawn points: not currently in a map!')
        
        # Get spawnpoint file
        self.spawnFile = gungamelib.getGameDir('cfg/gungame/spawnpoints/%s.txt' % self.mapName)
        
        # Does the file exist?
        if not self.exists():
            return
        
        # Get the spawn file if it exists
        self.dict_spawnPoints = self.__getNewSpawnFile()
    
    def __getNewSpawnFile(self):
        '''PRIVATE FUNCTION: Used to load the spawn point file into memory for
        usage in-game.'''
        # Spawnpoint file exists?
        if not self.exists():
            return False
        
        # Get spawnpoint lines
        spawnPointFile = open(self.spawnFile, 'r')
        fileLines = [x.strip() for x in spawnPointFile.readlines()]
        spawnPointFile.close()
        
        # Set up variables
        self.lineCount = 0
        list_spawnCoordinates = []
        
        # Loop through the lines
        for line in fileLines:
            # If the line is blank, do not continue
            if line == '':
                break
            
            # Split the line and append to the appropriate lists
            list_spawnCoordinates.append(line.split(' '))
            
            self.lineCount += 1
        
        return dict(zip(range(0, len(list_spawnCoordinates)+1), list_spawnCoordinates))
    
    def __createNewSpawnFile(self):
        '''PRIVATE FUNCTION: Used to create a new spawnpoint file.'''
        spawnPointFile = open(self.spawnFile, 'w').close()
    
    def add(self, posX, posY, posZ, eyeYaw):
        '''Adds a spawnpoint to the current spawnpoint file.'''
        # No spawnpoint file?
        if not self.dict_spawnPoints:
            # Create the new spawn point file
            self.__createNewSpawnFile()
        
        # Open the spawnpoint file
        spawnPointFile = open(self.spawnFile, 'a')
        
        # Prep the vars
        posX = float(posX)
        posY = float(posY)
        posZ = float(posZ)
        eyeYaw = float(eyeYaw)
        
        # Write to file, flush and close
        spawnPointFile.write('%f %f %f 0.000000 %f 0.000000\n' % (posX, posY, posZ, eyeYaw))
        spawnPointFile.flush()
        spawnPointFile.close()
        
        # Add spawnpoint to memory
        self.lineCount += 1
        self.dict_spawnPoints[self.lineCount] = [posX, posY, posZ, 0.00000, eyeYaw, 0.00000]
        
        # Show spawnPoint with a prop
        self.show(1)
        self.__showProp(self.lineCount)
    
    def refresh(self):
        '''Refreshes the current spawnpoint file.'''
        # File exists?
        if not self.exists():
            raise SpawnPointError('Unable to refresh (%s): no spawnpoint file.' % self.spawnFile)
        
        # Get new spawnpoint file
        self.dict_spawnPoints = self.__getNewSpawnFile()
        
        # If the props are shown, refresh them
        if self.getShow:
            self.show(0)
            self.show(1)
    
    def delete(self, index):
        '''Deletes a specific spawnpoint (using index) from memory and the spawn
        point file.'''
        # Convert index to an int
        index = int(index)
        
        # Check the file exists
        if not self.exists():
            raise SpawnPointError('Unable to delete spawnpoint (%d): no spawnpoint file.' % index)
        
        # Check the index exists
        if not self.dict_spawnPoints.has_key(index):
            raise SpawnPointError('Unable to delete spawnpoint (%d): invalid index.' % index)
        
        # Remove spawn point from dictionary
        del self.dict_spawnPoints[index]
        
        # Open the spawn point file in 'write' mode (overwrite the old)
        spawnPointFile = open(self.spawnFile, 'w')
        
        # Loop through the spawnpoints
        for index in self.dict_spawnPoints:
            # Get list
            list_spawnCoordinates = self.dict_spawnPoints[index]
            
            # Write to file
            spawnPointFile.write('%f %f %f 0.000000 %f 0.000000\n' % (
                    float(list_spawnCoordinates[0]),
                    float(list_spawnCoordinates[1]),
                    float(list_spawnCoordinates[2]),
                    float(list_spawnCoordinates[4]))
                )
        
        # Flush and close the file
        spawnPointFile.flush()
        spawnPointFile.close()
        
        # Refresh the current spawn points
        self.refresh()
    
    def deleteAll(self):
        '''Delets all the spawnpoints from memory, and from the spawnpoint file.
        This will also delete the spawnpoint file.'''
        # Check the file exists
        if not self.exists():
            raise SpawnPointError('Unable to delete spawnpoint (%d): no spawnpoint file.' % index)
        
        # Clear the spawn point dictionary
        self.dict_spawnPoints.clear()
        
        # Delete the spawn point file
        os.remove(self.spawnFile)
        
        # Be sure that we turn off "show" if it was turned on
        self.show(0)
    
    def getRandomPoint(self):
        '''Gets a random spawnpoint.'''
        if self.list_randomSpawnPointManager:
            return self.list_randomSpawnPointManager.pop()
        
        # Re-populate list
        self.list_randomSpawnPointManager = self.dict_spawnPoints.values()
        random.shuffle(self.list_randomSpawnPointManager)
        
        # Return a random point
        return self.list_randomSpawnPointManager.pop()
    
    def getTotalPoints(self):
        '''Returns the total number of spawnpoints for the current map.'''
        return len(self.dict_spawnPoints.keys())
    
    def hasPoints(self):
        '''Returns True if the spawnpoint file for this map has at least 1 point
        in it.'''
        if self.dict_spawnPoints:
            return True
        
        return False
    
    def exists(self):
        '''Checks to see if the current spawnpoint file exists.
        
        EXAMPLE:
            spawnPoints = SpawnPointManager()
            if spawnPoints.exists():
                # ...
        '''
        return os.path.isfile(self.spawnFile)
    
    def show(self, toggle=None):
        '''Shows a model at all spawnpoint locations in the current map.
        
        EXAMPLES:
            spawnPoints = SpawnPointManager()
            
            # Toggles
            spawnPoints.show()
            
            # Turns on
            spawnPoints.show(1)
            
            # Turns off
            spawnPoints.show(0)
        '''
        # Set the original value of the toggle
        originalToggle = self.showToggle
        
        # Check there are players on the server
        if not es.getuserid():
            raise SpawnPointError('Unable to show spawn points: no players on server!')
        
        # Check to see if an argument has been provided
        if toggle == None:
            self.showToggle = not self.showToggle
        else:
            self.showToggle = gungamelib.clamp(toggle, 0, 1)
        
        # Show props
        if originalToggle == 0 and self.showToggle == 1:
            for spawnPointIndex in self.dict_spawnPoints:
                self.__showProp(spawnPointIndex)
        
        # Hide props
        elif originalToggle == 1 and self.showToggle == 0:
            self.__hideAllProps()
    
    def getShow(self):
        return self.showToggle
    
    def __showProp(self, spawnPointIndex):
        '''PRIVATE FUNCTION: Shows a model at a specific spawnpoint index.'''
        userid = es.getuserid()
        
        # Check we aren't already showing it
        if self.dict_propIndex.has_key(spawnPointIndex):
            return
        
        # Create prop and name it
        es.server.cmd('es_xprop_dynamic_create %s %s' % (userid, model))
        es.server.cmd('es_entsetname %s gg_dm_prop%i' % (userid, spawnPointIndex))
        
        # Get index
        propIndex = int(es.ServerVar('eventscripts_lastgive'))
        
        # Set position and collision group
        es.setindexprop(propIndex, 'CBaseEntity.m_CollisionGroup', 17)
        es.setindexprop(propIndex, 'CBaseEntity.m_vecOrigin', '%s, %s, %s' % (self.dict_spawnPoints[spawnPointIndex][0],
                                                                              self.dict_spawnPoints[spawnPointIndex][1],
                                                                              self.dict_spawnPoints[spawnPointIndex][2]))
        es.setindexprop(propIndex, 'CBaseEntity.m_angRotation', '0, %s, 0' % self.dict_spawnPoints[spawnPointIndex][4])
        
        # Set aestetics
        es.server.cmd('es_xfire %s prop_dynamic SetAnimation "walk_lower"' %userid)
        es.server.cmd('es_xfire %s prop_dynamic SetDefaultAnimation  "walk_lower"' %userid)
        es.server.cmd('es_xfire %s prop_dynamic AddOutput "rendermode 1"' %userid)
        es.server.cmd('es_xfire %s prop_dynamic alpha "185"' %userid)
        
        # Add to prop index points
        self.dict_propIndex[spawnPointIndex] = propIndex
    
    def __hideAllProps(self):
        '''PRIVATE FUNCTION: Hides all active spawnpoint props.'''
        # Get list of props
        list_entityIndexes = es.createentitylist('prop_dynamic').keys()
        
        # Remove all props
        for spawnPointIndex in self.dict_propIndex:
            if self.dict_propIndex[spawnPointIndex] in list_entityIndexes:
                es.server.cmd('es_xremove gg_dm_prop%i' % int(spawnPointIndex))
        
        # Clear prop index dictionary
        self.dict_propIndex.clear()
    
    def __resetProps(self):
        '''PRIVATE FUNCTION: Resets all active spawnpoint props'''
        # Remove all props
        self.__hideAllProps()
        
        # Show props in new positions
        for spawnPointIndex in self.dict_spawnPoints:
            self.__showProp(spawnPointIndex)
