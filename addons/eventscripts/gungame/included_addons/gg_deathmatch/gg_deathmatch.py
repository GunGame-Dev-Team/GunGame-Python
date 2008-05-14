# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts Imports
import es
import playerlib
import gamethread
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
info.version  = 'DM Revamp Test 318'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_deathmatch'
info.author   = 'GunGame Development Team'
    
# ==============================================================================
#  GLOBALS
# ==============================================================================
# Set up variables for use throughout gg_deathmatch
model = 'player/ct_gign.mdl'
#modelIndex = es.precachemodel('models' + model)
mySpawnFile = None

# ==============================================================================
#   ERROR CLASSES
# ==============================================================================
class SpawnPointError(Exception):
    pass
    
    
# ==============================================================================
#   SPAWN POINT CLASS
# ==============================================================================
class SpawnPoints:
    '''
    Class for controlling spawn points in GunGame: DeathMatch.
    This class is only usable when a map is loaded. If a map is
    not loaded when the class is called, it will raise an error.
    If no spawn point file is available, the class instance will
    return False.
    '''
    
    def __init__(self):
        # Retrieve the current map's name
        self.mapName = gungamelib.getMapName()
        self.showToggle = 0
        self.dict_spawnPoints = {}
        self.list_randomSpawnPoints = []
        self.list_spawnEntityIndexes = []
        self.list_spawnPointIndexes = []
        self.dict_propIndex = {}
        
        # Make sure we are currently in a map
        if self.mapName != '':
            self.spawnFile = gungamelib.getGameDir('cfg\\gungame\\spawnpoints\\%s.txt' %self.mapName)
            # We need to see if this spawn point file exists before doing anything
            if not os.path.isfile(self.spawnFile):
                return
                
            # Get the spawn file if it exists
            self.dict_spawnPoints = self.__getNewSpawnFile()
        else:
            raise SpawnPointError('[gg_deathmatch] Unable to retrieve spawn points: not currently on a map!')
        
    def __getNewSpawnFile(self):
        '''
        PRIVATE FUNCTION: Used to load the spawn point file into
        memory for usage in-game.
        '''
        
        # We need to see if this spawn point file exists before doing anything
        if not os.path.isfile(self.spawnFile):
            return False
            
        # Open the spawn point file and read the lines
        spawnPointFile = open(self.spawnFile, 'r')
        fileLines = spawnPointFile.readlines()
            
        # Set up variables and lists for the loop
        self.lineCount = 0
        list_spawnCoordinates = []
        list_counter = []
        
        # Loop through the lines
        for line in fileLines:
            # Strip the line
            line = line.strip()
            
            # If the line is blank, do not continue
            if line == '':
                break
        
            # Split the line and append to the appropriate lists
            list_spawnCoordinates.append(line.split(' '))
            list_counter.append(self.lineCount)
        
            # Increment the amount of lines
            self.lineCount += 1
            
        # Flush and close the spawn point file
        spawnPointFile.flush()
        spawnPointFile.close()
        
        return dict(zip(list_counter, list_spawnCoordinates))
                
                
    def __createNewSpawnFile(self):
        '''
        PRIVATE FUNCTION: Used to create the spawn file's *.txt
        on the physical disk in the 'cfg/gungame/spawnpoints'
        directory.
        '''
        # The file will be created if it doesn't exist when opened for appending
        spawnPointFile = open(self.spawnFile, 'w').close()
        
    def add(self, posX, posY, posZ, eyeYaw):
        '''
        Used to add a spawn point to a spawn points file. If
        a file does not exist, one will be created for you.
        '''
        # We see if any information is in the spawn points dictionary (it needs to be empty)
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
        '''
        Used to reload a spawn file that exists. This is useful
        for adding spawn points, and reloading the spawn points
        file so that the changes will take effect.
        '''
        # We need to see if this spawn point file exists before doing anything
        if os.path.isfile(self.spawnFile):
            self.dict_spawnPoints = self.__getNewSpawnFile()
            
            # If the props are shown, refresh them
            if self.getShow:
                self.show(0)
                self.show(1)
        else:
            raise SpawnPointError('[gg_deathmatch] Unable to refresh: \'%s\' does not exist!' %self.spawnFile)
            
    def delete(self, index):
        '''
        Used to delete a specific spawn point (via i' index)
        from memory, as well as from the spawn poin' text file.
        '''
        # Convert index to an int
        index = int(index)
        
        # We need to see if this spawn point file exists before doing anything
        if os.path.isfile(self.spawnFile):
            # Remove spawn point from dictionary
            del self.dict_spawnPoints[index]
            
            # Open the spawn point file in 'write' mode (overwrite the old)
            spawnPointFile = open(self.spawnFile, 'w')
            
            # Loop through the spawnpoints
            for index in self.dict_spawnPoints:
                # Get list
                list_spawnCoordinates = self.dict_spawnPoints[index]
        
                # Write to file
                spawnPointFile.write('%f %f %f 0.000000 %f 0.000000\n' % (float(list_spawnCoordinates[0]),
                    float(list_spawnCoordinates[1]), float(list_spawnCoordinates[2]), float(list_spawnCoordinates[4])))
                
            # Flush and close the file
            spawnPointFile.flush()
            spawnPointFile.close()
            
            # Refresh the current spawn points
            self.refresh()
        else:
            raise SpawnPointError('[gg_deathmatch] Unable to delete spawn index: \'%s\' does not exist!' %self.spawnFile)
            
    def deleteAll(self):
        '''
        Used to delete alls specific spawn points from memory,
        as well as from the spawn poin' text file. This will
        also delete the spawn point text file from the
        'cfg/gungame/spawnpoints' directory.
        '''
        # We need to see if this spawn point file exists before doing anything
        if os.path.isfile(self.spawnFile):
            # Clear the spawn point dictionary
            self.dict_spawnPoints.clear()
            
            # Delete the spawn point file
            os.remove(self.spawnFile)
            
            # Be sure that we turn off "show" if it was turned on
            self.show(0)
        else:
            raise SpawnPointError('[gg_deathmatch] Unable to delete spawn points: \'%s\' does not exist!' %self.spawnFile)
            
    def getPoint(self):
        '''
        Retrieves a single spawn point from the list of spawn points.
        Each time this command is called, it removes a spawn point from
        the list until the list is empty. Once empty, the list of spawn
        points is re-populated and randomized for reuse.
        '''
        if self.list_randomSpawnPoints:
            return self.list_randomSpawnPoints.pop()
        else:
            self.list_randomSpawnPoints = self.dict_spawnPoints.values()
            random.shuffle(self.list_randomSpawnPoints)
            return self.list_randomSpawnPoints.pop()
                
    def getTotalPoints(self):
        '''
        Returns the total number of spawn points from the spawn point
        text file located in the 'cfg/gungame/spawnpoints' directory.
        '''
        return len(self.dict_spawnPoints.keys())
    
    def hasPoints(self):
        '''
        Returns True if the spawn point file has at least 1 point.
        '''
        if self.dict_spawnPoints:
            return True
        return False
        
    def exists(self):
        '''
        This is intended for use on first calling the class. Coders can
        use this to make sure that the instance does not refer to a
        non-existant spawn point file.
        EXAMPLE:
                mySpawnFile = SpawnPoints()
                if mySpawnFile.exists():
                    # Code here
        '''
        return os.path.isfile(self.spawnFile)
        
    def show(self, toggle=None):
        '''
        This is used to show all spawn points that have been created by
        the spawn point file. A model will be spawned at all spawn locations
        that are in the spawn point file.
        
        EXAMPLES:
                mySpawnFile = SpawnPoints()
                # Toggles to on if off, off if on
                mySpawnFile.show()
                
                # Turns on
                mySpawnFile.show(1)
                
                # Turns off
                mySpawnFile.show(0)
        '''
        # Set the original value of the toggle
        originalToggle = self.showToggle
        
        # Check to see if an argument has been provided
        if toggle != None:
            if int(toggle) == 0:
                self.showToggle = 0
            elif int(toggle) == 1:
                if not es.getuserid():
                    raise SpawnPointError('[gg_deathmatch] Unable to show spawn points: no players on server!')
                self.showToggle = 1
        else:
            if self.showToggle():
                self.showToggle = 0
            else:
                if not es.getuserid():
                    raise SpawnPointError('[gg_deathmatch] Unable to show spawn points: no players on server!')
                self.showToggle = 1
        
        if originalToggle == 0 and self.showToggle == 1:
            for spawnPointIndex in self.dict_spawnPoints:
                self.__showProp(spawnPointIndex)
            
        elif originalToggle == 1 and self.showToggle == 0:
            self.__hideAllProp()
            
    def getShow(self):
        return self.showToggle
    
    def __showProp(self, spawnPointIndex):
        userid = es.getuserid()
        es.server.cmd('es_xprop_dynamic_create %s %s' % (userid, model))
        es.server.cmd('es_entsetname %s tester%i' % (userid, spawnPointIndex))
        propIndex = int(es.ServerVar('eventscripts_lastgive'))
        es.setindexprop(propIndex, 'CBaseEntity.m_CollisionGroup', 17)
        es.setindexprop(propIndex, 'CBaseEntity.m_vecOrigin', '%s, %s, %s' % (self.dict_spawnPoints[spawnPointIndex][0],
                                                                              self.dict_spawnPoints[spawnPointIndex][1],
                                                                              self.dict_spawnPoints[spawnPointIndex][2]))
        es.setindexprop(propIndex, 'CBaseEntity.m_angRotation', '0, %s, 0' % self.dict_spawnPoints[spawnPointIndex][4])
        es.server.cmd('es_xfire %s prop_dynamic SetAnimation \"walk_lower\"' %userid)
        es.server.cmd('es_xfire %s prop_dynamic SetDefaultAnimation  \"walk_lower\"' %userid)
        es.server.cmd('es_xfire %s prop_dynamic addOutput \"rendermode 1\"' %userid)
        es.server.cmd('es_xfire %s prop_dynamic alpha \"185\"' %userid)

        self.dict_propIndex[spawnPointIndex] = propIndex
    
    def __hideAllProp(self):
        # Get a list of props
        list_entityIndexes = es.createentitylist('prop_dynamic').keys()
        for spawnPointIndex in self.dict_propIndex:
            # Check to make sure the entity exists before we delete it.
            if self.dict_propIndex[spawnPointIndex] in list_entityIndexes:
                es.server.cmd('es_xremove tester%i' % int(spawnPointIndex))
    
    def __resetProps(self):
        self.dict_propIndex = 0
        for spawnPointIndex in self.dict_spawnPoints:
            self.__showProp(spawnPointIndex)

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    global mySpawnFile
    
    # Register addon with gungamelib
    gg_deathmatch = gungamelib.registerAddon('gg_deathmatch')
    gg_deathmatch.addDependency('gg_turbo', 1)
    gg_deathmatch.addDependency('gg_dead_strip', 1)
    gg_deathmatch.addDependency('gg_dissolver', 1)
    gg_deathmatch.addDependency('gg_map_obj', 0)
    gg_deathmatch.addDependency('gg_knife_elite', 0)
    gg_deathmatch.addDependency('gg_elimination', 0)
    
    '''
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
    '''
    
    # Create the player's custom repeat for respawning into the game
    for userid in es.getUseridList():    
        repeat.create('respawnPlayer%s' %userid, respawnCountDown, (userid))
    
    # Get the spawn points for the map
    if es.ServerVar('eventscripts_currentmap') != '':
        mySpawnFile = SpawnPoints()
        
    # Get a player list of dead players then spawn them
    for userid in playerlib.getUseridList('#dead'):
        repeat.start('respawnPlayer%s' %userid, 1, gungamelib.getVariable('gg_dm_respawn_delay'))
    
    # Set freezetime and roundtime
    es.server.cmd('mp_freezetime 0')
    es.server.cmd('mp_roundtime 900')
    
def unload():
    global mySpawnFile
    
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_deathmatch')
    
    for userid in es.getUseridList():
        # Create the player's custom repeat for respawning into the game
        repeat.delete('respawnPlayer%s' %userid)
    
    if mySpawnFile.getShow():
        mySpawnFile.show(0)

def es_map_start(event_var):
    global mySpawnFile
    # Don't allow respawn
    gungamelib.setGlobal('respawn_allowed', 0)
    
    del mySpawnFile
    mySpawnFile = SpawnPoints()
    
def player_team(event_var):
    # Don't allow it if people are disconnecting
    if event_var['disconnect'] != '0':
        return
    
    # Get the userid
    userid = event_var['userid']
    
    # If the player does not have a respawn repeat, create one
    respawnPlayer = repeat.find('respawnPlayer%s' %userid)
    if not respawnPlayer:
        repeat.create('respawnPlayer%s' %userid, respawnCountDown, (userid))
        
    # Don't allow spectators or players that are unassigned to respawn
    if int(event_var['team']) < 2:
        # See if the player's repeat is currently running
        if repeat.status('respawnPlayer%s' %userid) != 1:
            # Stop the repeat
            repeat.stop('respawnPlayer%s' %userid)
            # Send the player a hudhint
            gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_CancelTeam')
        return
    
    # Respawn the player (alive check in loop)
    repeat.start('respawnPlayer%s' %userid, 1, gungamelib.getVariable('gg_dm_respawn_delay'))
    
def player_spawn(event_var):
    global mySpawnFile
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
    if not mySpawnFile.hasPoints():
        return
        
    # Teleport the player
    list_teleportInfo = mySpawnFile.getPoint()
    gungamelib.getPlayer(userid).teleportPlayer(list_teleportInfo[0],
                                                list_teleportInfo[1],
                                                list_teleportInfo[2],
                                                0,
                                                list_teleportInfo[4])
    
def player_death(event_var):
    # Get the userid
    userid = event_var['userid']
    
    if playerlib.getPlayer(userid).get('defuser'):
        gamethread.delayed(0.5, es.remove, ('item_defuser'))
    
    # Respawn the player if the round hasn't ended
    if gungamelib.getGlobal('respawn_allowed'):
        repeat.start('respawnPlayer%s' %userid, 1, gungamelib.getVariable('gg_dm_respawn_delay'))
        
def player_disconnect(event_var):
    # Get userid
    userid = event_var['userid']
    
    # Delete the player-specific repeat
    if repeat.find('respawnPlayer%s' %userid):
        repeat.delete('respawnPlayer%s' %userid)
    
def round_start(event_var):
    global mySpawnFile
    if mySpawnFile.getShow():
        mySpawnFile.__resetProps()
    # Allow respawn
    gungamelib.setGlobal('respawn_allowed', 1)
    
def round_end(event_var):
    # Don't allow respawn
    gungamelib.setGlobal('respawn_allowed', 0)
    
    for userid in es.getUseridList():
        playerRespawn = repeat.find('respawnPlayer%s' %userid)
        if playerRespawn:
            if playerRespawn.status() != 1:
                gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_RoundEnd')
    
def respawnCountDown(userid):
    # Make sure that the repeat exists
    respawnRepeat = repeat.find('respawnPlayer%s' %userid)
    if not respawnRepeat:
        return
        
    # If the player is not dead, we don't need to respawn them
    if not gungamelib.isDead(userid):
        respawnRepeat.stop()
        return
        
    # Do not display these messages during the warmup round or when a vote is active
    if not int(gungamelib.getGlobal('isWarmup')) and not int(gungamelib.getGlobal('voteActive')):
        if gungamelib.getGlobal('respawn_allowed'):
            if respawnRepeat['remaining'] > 1:
                gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_Plural', {'time': respawnRepeat['remaining']})
            # Is the counter 1?
            elif respawnRepeat['remaining'] == 1:
                gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_Singular')
            elif respawnRepeat['remaining'] == 0:
                gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_Ended')
        else:
            gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_RoundEnd')      
    
    # Respawn the player
    if respawnRepeat['remaining'] == 0:
        # See if we are going to allow them to respawn
        if gungamelib.getGlobal('respawn_allowed'):
            es.server.cmd('%s %s' %(gungamelib.getVariable('gg_dm_respawn_cmd'), userid))

'''                                                        
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
        gungamelib.msg('gg_deathmatch', userid, '')

def cmd_dm_print(userid):
    # Get map name
    mapName = gungamelib.getMapName()
    
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
'''