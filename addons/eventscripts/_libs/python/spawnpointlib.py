''' (c) 2008 by the GunGame Coding Team

    Title: spawnpointlib
    Version: 1.0.448
    Description: GunGame Spawnpoint Library
'''

import os
import random
import es
import vecmath
import gamethread
import gungamelib

model = 'player/ct_gign.mdl'

class SpawnPointError(Exception):
    pass

class SpawnPointManager(object):
    '''Manages spawnpoints in accordance to the CSS:DM spawnpoint file format.
    This class is only usable when in a map, if this class is initialized when
    not in map, SpawnPointError will be raised.'''
    
    spawnPoints = []
    randomPoints = []
    propIndexes = {}
    showState = 0
    
    def __init__(self, spawnPointDirectory='cfg/spawnpoints'):
        # Get map name
        self.mapName = str(es.ServerVar('eventscripts_currentmap'))
        
        # Make sure we are currently in a map
        if str(es.ServerVar('eventscripts_currentmap')) == '':
            raise SpawnPointError('Unable to retrieve spawn points: not currently in a map!')
        
        # Get spawnpoint file
        self.spawnFile = '%s/%s/%s.txt' % (str(es.ServerVar('eventscripts_gamedir')).replace('\\', '/'), spawnPointDirectory, self.mapName)
        
        # Does the file exist?
        if not self.exists():
            return
        
        # Load the spawnpoint file
        self.loadSpawnFile()
    
    def __getitem__(self, item):
        # Make index an int
        item = int(item)
        
        # Value index?
        if not self.validIndex(item):
            raise IndexError('No spawnpoint under "%s".' % item)
        
        # Return spawnpoint data
        return self.spawnPoints[item]
    
    def loadSpawnFile(self):
        '''Used to load the spawn point file into memory for usage in-game.'''
        # Spawnpoint file exists?
        if not self.exists():
            return None
        
        # Get spawnpoint lines
        spawnPointFile = open(self.spawnFile, 'r')
        fileLines = [x.strip() for x in spawnPointFile.readlines()]
        spawnPointFile.close()
        
        # Set up variables
        self.spawnPoints = [x.split(' ', 6) for x in fileLines]
        
        if not self.hasPoints():
            return
        
        gamethread.delayed(0, self.__createSpawnPoints, ())
    
    def __createSpawnPoints(self):
        '''PRIVATE: Creates info_player_[counter]terrorist entities randomly at
        spawnpoint locations.'''
        # Remove all existing spawnpoints
        for x in es.createentitylist('info_player_terrorist'):
            es.server.cmd('es_xremove %i' % x)
        for x in es.createentitylist('info_player_counterterrorist'):
            es.server.cmd('es_xremove %i' % x)
        
        # Get a userid
        userid = es.getuserid()
        fakeBot = bool(userid)
        if fakeBot:
            userid = es.createbot('Spawnpoint Maker')
        
        # Shuffle up the spawnpoints
        randomPoints = self.spawnPoints[:]
        random.shuffle(randomPoints)
        
        # Initialise variables
        invalid = set()
        team = True
        
        # Loop through the spawn points
        for x in randomPoints:
            # Skip invalid spawnpoints
            if str(x) in invalid:
                print '[spawnpointlib] The spawnpoint at %s,%s,%s is within 100 units of another spawnpoint at %s,%s,%s' % (x[0], x[1], x[2], y[0], y[1], y[2])
                continue
            
            # Initialise variables
            currentPoint = vecmath.vector(*x[:3])
            
            # Distance check
            for y in self.spawnPoints:
                # Don't check ourselves
                if x == y:
                    continue
                
                # Distance is 100 units or less, add it to the invalid spawnpoint list
                if vecmath.distance(currentPoint, y[:3]) < 100:
                    invalid.add(str(y))
            
            # Create the spawnpoint and get the index
            es.server.cmd('es_xgive %s %s' % (userid, 'info_player_counterterrorist' if team else 'info_player_terrorist'))
            index = int(es.ServerVar('eventscripts_lastgive'))
            
            # Set the spawnpoint position and rotation
            es.setindexprop(index, 'CBaseEntity.m_vecOrigin', currentPoint.getstr())
            es.setindexprop(index, 'CBaseEntity.m_angRotation', '0,%s,0' %  x[4])
            
            # Swap the team around
            team = not team
        
        # Kick the bot
        if fakeBot:
            es.delayed(0, 'kickid %s' % userid)
    
    def createNewSpawnFile(self):
        '''Used to create a new spawnpoint file.'''
        open(self.spawnFile, 'w').close()
    
    def add(self, posX, posY, posZ, eyeYaw):
        '''Adds a spawnpoint to the current spawnpoint file.'''
        # Create spawnpoint file if it doesn't exist
        if not self.exists():
            self.createNewSpawnFile()
        
        # Open the spawnpoint file
        spawnPointFile = open(self.spawnFile, 'a')
        
        # Prep the vars
        posX = float(posX)
        posY = float(posY)
        posZ = float(posZ)
        eyeYaw = float(eyeYaw)
        
        # Add spawnpoint to file
        spawnPointFile.write('%f %f %f 0.000000 %f 0.000000\n' % (posX, posY, posZ, eyeYaw))
        spawnPointFile.close()
        
        # Add spawnpoint to memory
        self.spawnPoints.append([posX, posY, posZ, 0.00000, eyeYaw, 0.00000])
    
    def refresh(self):
        '''Refreshes the current spawnpoint file.'''
        # File exists?
        if not self.exists():
            raise SpawnPointError('Unable to refresh (%s): no spawnpoint file.' % self.spawnFile)
        
        # Refresh spawnpoint file
        self.loadSpawnFile()
        
        # Refresh props
        if self.getShow():
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
        if not self.validIndex(index):
            raise SpawnPointError('Unable to delete spawnpoint (%d): invalid index.' % index)
        
        # Remove spawn point from dictionary
        del self.spawnPoints[index]
        
        # Open the spawn point file in 'write' mode (overwrite the old)
        spawnPointFile = open(self.spawnFile, 'w')
        
        # Write spawnpoints to file
        for s in self.spawnPoints:
            spawnPointFile.write('%f %f %f 0.000000 %f 0.000000\n' % (s[0], s[1], s[2], s[4]))
        
        # Close and refresh
        spawnPointFile.close()
        self.refresh()
    
    def deleteAll(self):
        '''Delets all the spawnpoints from memory, and from the spawnpoint file.
        This will also delete the spawnpoint file.'''
        # Check the file exists
        if not self.exists():
            raise SpawnPointError('Unable to delete spawnpoint (%d): no spawnpoint file.' % index)
        
        # Clear the spawn point dictionary
        self.spawnPoints = []
        
        # Delete the spawn point file
        os.remove(self.spawnFile)
        
        # Be sure that we turn off "show" if it was turned on
        self.show(0)
    
    def getRandomPoint(self):
        '''Gets a random spawnpoint.
        
        UNDO: Is this needed anymore with the new spawnpoint system?'''
        if self.randomPoints:
            return self.randomPoints.pop()
        
        # Re-populate list
        self.randomPoints = self.spawnPoints[:]
        random.shuffle(self.randomPoints)
        
        # Return a random point
        return self.randomPoints.pop()
    
    def show(self, toggle=None):
        '''Shows a model at all spawnpoint locations in the current map.'''
        # Check there are players on the server
        if not es.getuserid():
            return
        
        # Set the original value of the toggle
        originalToggle = self.showState
        
        # Check to see if an argument has been provided
        if toggle == None:
            self.showState = not self.showState
        else:
            self.showState = int(toggle)
        
        # Show props
        if originalToggle == 0 and self.showState == 1:
            for index in self.getIndexIter():
                self.__showProp(index)
        
        # Hide props
        elif originalToggle == 1 and self.showState == 0:
            self.__hideAllProps()
    
    def __showProp(self, index):
        '''PRIVATE: Shows a model at a specific spawnpoint index.'''
        self.userid = es.getuserid()
        
        # Check we aren't already showing it
        if index in self.propIndexes:
            return
        
        # Create prop and name it
        es.server.cmd('es_xprop_dynamic_create %s %s' % (userid, model))
        es.server.cmd('es_xentsetname %s gg_dm_prop%i' % (userid, index))
        
        # Get index
        propIndex = int(es.ServerVar('eventscripts_lastgive'))
        
        # Set position and collision group
        es.setindexprop(propIndex, 'CBaseEntity.m_CollisionGroup', 2)
        es.setindexprop(propIndex, 'CBaseEntity.m_vecOrigin', '%s, %s, %s' % (self.spawnPoints[index][0],
                                                                              self.spawnPoints[index][1],
                                                                              self.spawnPoints[index][2]))
        es.setindexprop(propIndex, 'CBaseEntity.m_angRotation', '0, %s, 0' % self.spawnPoints[index][4])
        
        # Set aestetics
        es.server.cmd('es_xfire %s prop_dynamic SetAnimation "walk_lower"' % userid)
        es.server.cmd('es_xfire %s prop_dynamic SetDefaultAnimation  "walk_lower"' % userid)
        es.server.cmd('es_xfire %s prop_dynamic AddOutput "rendermode 1"' % userid)
        es.server.cmd('es_xfire %s prop_dynamic alpha "185"' % userid)
        
        # Add to prop index points
        self.propIndexes[index] = propIndex
    
    def __hideAllProps(self):
        '''PRIVATE: Hides all active spawnpoint props.'''
        # Get list of props
        entityIndexes = es.createentitylist('prop_dynamic').keys()
        
        # Remove all props
        for index in self.propIndexes:
            if self.propIndexes[index] in entityIndexes:
                es.server.cmd('es_xremove gg_dm_prop%i' % int(index))
        
        # Clear prop index dictionary
        self.propIndexes.clear()
    
    def __resetProps(self):
        '''PRIVATE: Resets all active spawnpoint props'''
        # Remove all props
        self.__hideAllProps()
        
        # Show props in new positions
        for index in self.getIndexIter():
            self.__showProp(index)
    
    def validIndex(self, index):
        '''Checks to see if <index> is a valid index'''
        return index in self.getIndexIter()
    
    def getIndexIter(self):
        '''Returns a spawnpoint index iterator.'''
        return range(0, len(self.spawnPoints))
    
    def getTotalPoints(self):
        '''Returns the total number of spawnpoints for the current map.'''
        return len(self.spawnPoints)
    
    def hasPoints(self):
        '''Returns True if the spawnpoint file for this map has at least 1 point
        in it.'''
        return bool(self.spawnPoints)
    
    def exists(self):
        '''Checks to see if the current spawnpoint file exists.'''
        return os.path.isfile(self.spawnFile)
    
    def getShow(self):
        '''Returns the current prop visibility state.'''
        return self.showState
