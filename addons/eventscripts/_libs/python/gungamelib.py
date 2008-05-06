''' (c) 2008 by the GunGame Coding Team

    Title: gungamelib
    Version: 1.0.302
    Description:
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python Imports
import string
import random
import os
import time
import ConfigParser
import cPickle

# EventScripts Imports
import es
import playerlib
import gamethread
import popuplib
import langlib
import usermsg
from configobj import ConfigObj

# ==============================================================================
#   GLOBALS
# ==============================================================================
dict_weaponOrders = {}
dict_weaponOrderSettings = {}
dict_weaponOrderSettings['currentWeaponOrderFile'] = None

dict_leaderInfo = {}
dict_leaderInfo['currentLeaders'] = []
dict_leaderInfo['oldLeaders'] = []
dict_leaderInfo['leaderLevel'] = 1

dict_players = {}
dict_variables = {}
dict_globals = {}
dict_cfgSettings = {}
dict_sounds = {}
dict_addons = {}
dict_dependencies = {}
dict_uniqueIds = {}
dict_winners = {}

list_validWeapons = ['glock','usp','p228','deagle','fiveseven',
                    'elite','m3','xm1014','tmp','mac10','mp5navy',
                    'ump45','p90','galil','famas','ak47','scout',
                    'm4a1','sg550','g3sg1','awp','sg552','aug',
                    'm249','hegrenade','knife']

list_criticalConfigs = ('gg_en_config.cfg', 'gg_default_addons.cfg')
list_configs = []

# ==============================================================================
#   ERROR CLASSES
# ==============================================================================
class UseridError(Exception):
    pass
    
class PlayerError(Exception):
    pass
    
class TeamError(Exception):
    pass
    
class DeadError(Exception):
    pass
    
class FileError(Exception):
    pass
    
class ArgumentError(Exception):
    pass

# ==============================================================================
#   CONVARS
# ==============================================================================
gungameDebugLevel = es.ServerVar('gg_debuglevel')
gungameDebugLevel.makepublic()

# ==============================================================================
#   PLAYER CLASS
# ==============================================================================
class Player:
    '''Player class, holds all a players information and attributes.'''
    
    def __init__(self, userid):
        '''Called everytime getPlayer() is called, and all the attributes are
        refreshed.'''
        # Check the userid is numeric
        if not isNumeric(userid):
            raise ValueError('Cannot get player (%s): userid must be numerical.' % userid)
        
        # Make userid an int
        self.userid = int(userid)
        
        if not clientInServer(self.userid):
            if self.__validatePlayer():
                # Get their attributes
                self.attributes = dict_players[self.userid]
            else:
                # Invalid userid
                raise UseridError('Cannot get player (%s): not on the server.' % self.userid)
        else:
            # Check they exist
            if not self.__validatePlayer():
                # Create the player
                self.__createPlayer()
            else:
                # Get the attributes
                self.attributes = dict_players[self.userid]
    
    def __getitem__(self, item):
        # Lower-case the item
        item = str(item).lower()
        
        # Return the attribute
        if item in self.attributes:
            return self.attributes[item]
        else:
            raise ValueError('Unable to get attribute (%s): invalid attribute.' % item)
    
    def __setitem__(self, item, value):
        # Format the item and value
        item = str(item).lower()
        value = int(value)
        
        # Does the attribute exist?
        if item not in self.attributes:
            raise ValueError('Unable to set attribute (%s): invalid attribute.' % item)
        
        # LEVEL
        if item == 'level':
            if value > 0 and value <= (getTotalLevels() + 1):
                currentLevel = self.attributes['level']
                
                # Let's see if the new level that they are trying to set is greater than their current level
                if value > currentLevel:
                    # Let's see if the new level that they are trying to set is greater than the leader level
                    if value > dict_leaderInfo['leaderLevel']:
                        dict_leaderInfo['leaderLevel'] = value
                        
                        # Check to see if this is a new leader for the first time in the GunGame round
                        if len(dict_leaderInfo['currentLeaders']) == 0:
                            dict_leaderInfo['currentLeaders'].append(self.userid)
                            # FIRE NEW LEADER EVENT HERE event gg_new_leader
                            es.event('initialize', 'gg_new_leader')
                            es.event('setint', 'gg_new_leader', 'userid', self.userid)
                            es.event('fire', 'gg_new_leader')
                        
                        # Check to see if this is a new leader
                        elif len(dict_leaderInfo['currentLeaders']) > 1:
                            if self.userid in dict_leaderInfo['currentLeaders']:
                                dict_leaderInfo['currentLeaders'].remove(self.userid)
                            dict_leaderInfo['oldLeaders'][:] = dict_leaderInfo['currentLeaders']
                            dict_leaderInfo['currentLeaders'] = [self.userid]
                            # FIRE NEW LEADER EVENT HERE event gg_new_leader
                            es.event('initialize', 'gg_new_leader')
                            es.event('setint', 'gg_new_leader', 'userid', self.userid)
                            es.event('fire', 'gg_new_leader')
                        
                        # The leader is the same leader
                        else:
                            dict_leaderInfo['oldLeaders'] = [self.userid]
                        
                    # See if they tied the leader
                    elif value == dict_leaderInfo['leaderLevel']:
                        dict_leaderInfo['oldLeaders'][:] = dict_leaderInfo['currentLeaders']
                        dict_leaderInfo['currentLeaders'].append(self.userid)
                        
                        # FIRE TIED LEADER EVENT HERE event gg_tied_leader
                        es.event('initialize', 'gg_tied_leader')
                        es.event('setint', 'gg_tied_leader', 'userid', self.userid)
                        es.event('fire', 'gg_tied_leader')
                
                # Let's see if the new level that they are trying to set is less than their current level
                elif value < currentLevel:
                    # Check to see if the player that lost the level is a leader
                    if currentLevel == dict_leaderInfo['leaderLevel']:
                        if len(dict_leaderInfo['currentLeaders']) > 1:
                            dict_leaderInfo['oldLeaders'][:] = dict_leaderInfo['currentLeaders']
                            dict_leaderInfo['currentLeaders'].remove(self.userid)
                            
                            # FIRE LEADER LOST LEVEL EVENT HERE event gg_leader_lostlevel
                            es.event('initialize', 'gg_leader_lostlevel')
                            es.event('setint', 'gg_leader_lostlevel', 'userid', self.userid)
                            es.event('fire', 'gg_leader_lostlevel')
                        else:
                            dict_leaderInfo['oldLeaders'][:] = dict_leaderInfo['currentLeaders']
                            
                            # Find the new leader level by looping though the GunGame Core Dictionary
                            leaderLevel = 0
                            
                            # Set the old leader's level to the new value prior to checking the highest level
                            self.attributes[item] = value
                            
                            # Check for a new leader
                            for userid in dict_players:
                                if int(dict_players[userid]['level']) > leaderLevel:
                                    dict_leaderInfo['currentLeaders'] = [userid]
                                    leaderLevel = int(dict_players[userid]['level'])
                                elif dict_players[userid]['level'] == leaderLevel:
                                    dict_leaderInfo['currentLeaders'].append(userid)
                            
                            # Set the leader level to the new level
                            dict_leaderInfo['leaderLevel'] = leaderLevel
                            
                            # FIRE LEADER LOST LEVEL EVENT HERE event gg_leader_lostlevel
                            es.event('initialize', 'gg_leader_lostlevel')
                            es.event('setint', 'gg_leader_lostlevel', 'userid', self.userid)
                            es.event('fire', 'gg_leader_lostlevel')
                
                self.attributes[item] = value
            else:
                raise ValueError('Invalid value (%s): level value must be greater than 0 and less than %s.' % (value, getTotalLevels() + 1))
        
        # AFK ROUNDS
        elif item == 'afkrounds':
            if value > -1:
                self.attributes[item] = value
            else:
                raise ValueError('Invalid value (%s): AFK Rounds value must be a positive number.' % value)
        
        # MULTIKILL
        elif item == 'multikill':
            if value > -1:
                self.attributes[item] = value
            else:
                raise ValueError('Invalid value (%s): multikill value must be a positive number.' % value)
        
        # TRIPLE
        elif item == 'triple':
            if value > -1 and value < 4:
                self.attributes[item] = value
            else:
                raise ValueError('Invalid value (%s): triple level value must be between 0 and 3.' % value)
        
        # PREVENT LEVEL
        elif item == 'preventlevel':
            if value == 0 or value == 1:
                self.attributes[item] = value
            else:
                raise ValueError('Invalid value (%s): prevent level must be 1 or 0.' % value)
        
        # CUSTOM ATTRIBUTES
        else:
            self.attributes[item] = value
    
    def __int__(self):
        '''Returns the players userid.'''
        return self.userid
        
    def __validatePlayer(self):
        '''Checks the player exists in the player database.'''
        return dict_players.has_key(self.userid)
    
    def __createPlayer(self, connectFlag=None):
        '''Creates the player in the players database.'''
        names = ['level', 'afkrounds', 'multikill',
                'triple', 'preventlevel', 'afkmathtotal',
                'steamid', 'index']
        values = [1, 0, 0, 0, 0, 0, playerlib.uniqueid(self.userid, 1), int(playerlib.getPlayer(self.userid).attributes['index'])]
        
        # Set attributes
        self.attributes = dict(zip(names, values))
        
        # Get Unique ID of player
        dict_uniqueIds[self.userid] = playerlib.uniqueid(self.userid, 1)
        
        # Create them in the players dictionary
        dict_players[self.userid] = self.attributes
        
    def removePlayer(self):
        '''Removes a player from the GunGame player dictionary.'''
        if self.__validatePlayer():
            # Check they exist on the server
            if self.__validatePlayerConnection():
                raise ValueError('Unable to remove the player (%s): player still in server.' % self.userid)
            
            # Remove the player
            del dict_players[self.userid]
    
    def __validatePlayerConnection(self):
        '''Check the player exists in the server.'''
        return bool(es.exists('userid', self.userid))
    
    def resetPlayer(self):
        '''Reset the players attributes.'''
        self.__createPlayer()
        
    def resetPlayerLocation(self):
        '''Resets a players AFK math total.'''
        # Check the player exists
        if not self.__validatePlayerConnection():
            return
        
        # Get the player's location
        x, y, z = es.getplayerlocation(self.userid)
        
        # Get the AFK math total
        afkMathTotal = int(int(x) + int(y) + int(es.getplayerprop(self.userid, 'CCSPlayer.m_angEyeAngles[0]')) + int(es.getplayerprop(self.userid, 'CCSPlayer.m_angEyeAngles[1]')))
        
        # Update the AFK math total
        self.attributes['afkmathtotal'] = int(afkMathTotal)
    
    def playerNotAFK(self):
        '''Makes a player not AFK.'''
        # Make sure player is on a team
        if isSpectator(self.userid):
            raise TeamError('Unable to make player active (%s): not on a team.' % self.userid)
        
        # Reset player math total
        self.attributes['afkmathtotal'] = 0
    
    def isPlayerAFK(self):
        '''Checks a player is AFK.'''
        # Make sure player is on a team
        if isSpectator(self.userid):
            raise TeamError('Unable to check player AFK status (%s): not on a team.' % self.userid)
        
        # Get the player's location
        x, y, z = es.getplayerlocation(self.userid)
        
        # Get AFK math total
        afkMathTotal = int(int(x) + int(y) + int(es.getplayerprop(self.userid, 'CCSPlayer.m_angEyeAngles[0]')) + int(es.getplayerprop(self.userid, 'CCSPlayer.m_angEyeAngles[1]')))
        
        return (int(afkMathTotal) == self.attributes['afkmathtotal'])
    
    def teleportPlayer(self, x, y, z, eyeangle0=0, eyeangle1=0):
        '''Teleport a player.'''
        # Make sure player is on a team
        if isSpectator(self.userid):
            raise TeamError('Unable to teleport player (%s): not on a team.' % self.userid)
        
        # Make sure the player is alive
        if isDead(self.userid):
            raise DeadError('Unable to teleport player (%s): not alive.' % self.userid)
        
        # Set position
        es.server.cmd('es_xsetpos %d %s %s %s' % (self.userid, x, y, z))
        
        # Set eye angles
        if eyeangle0 != 0 or eyeangle1 != 0:
            es.server.cmd('es_xsetang %d %s %s' %(self.userid, eyeangle0, eyeangle1))
        
        # Reset player AFK status
        gamethread.delayed(0.1, self.resetPlayerLocation, ())
    
    def setPlayerEyeAngles(self, eyeAngle0, eyeAngle1):
        '''Sets a players view angle.'''
        # Make sure player is on a team
        if isSpectator(self.userid):
            raise TeamError('Unable to set player angles (%s): not on a team' % self.userid)
        
        # Make sure player is alive
        if isDead(self.userid):
            raise DeadError('Unable to set player angles (%s): not alive.' % self.userid)
        
        # Set angles
        es.server.cmd('es_xsetang %d %s %s' % (self.userid, eyeangle0, eyeangle1))
        
        # Reset player AFK status
        gamethread.delayed(0.1, self.resetPlayerLocation, ())
    
    def stripPlayer(self):
        '''Strips a player of all their weapons, except knife.'''
        es.server.cmd('es_xgive %s weapon_knife' % self.userid)
        es.server.cmd('es_xgive %s player_weaponstrip' % self.userid)
        es.server.cmd('es_xfire %s player_weaponstrip Strip' % self.userid)
        es.server.cmd('es_xfire %s player_weaponstrip Kill' % self.userid)
        
        '''
        # Make sure player is on a team
        if isSpectator(self.userid):
            raise TeamError('Unable to strip player (%s): not on a team' % self.userid)
        
        # Make sure player is alive
        if isDead(self.userid):
            raise DeadError('Unable to strip player (%s): is not alive' % self.userid)
        
        # Get player object
        playerObj = playerlib.getPlayer(self.userid)
        
        # Get player weapon names
        primary = playerObj.get('primary')
        secondary = playerObj.get('secondary')
        
        # Remove primary
        if primary:
            es.server.cmd('es_xremove %d' % int(playerObj.get('weaponindex', primary)))
        
        # Remove secondary
        if secondary:
            es.server.cmd('es_xremove %d' % int(playerObj.get('weaponindex', secondary)))
        '''
    
    def giveWeapon(self):
        '''Gives a player their current weapon.'''
        # Make sure player is on a team
        if isSpectator(self.userid):
            raise TeamError('Unable to give player weapon (%s): not on a team' % self.userid)
        
        # Make sure player is alive
        if isDead(self.userid):
            raise DeadError('Unable to give player weapon (%s): is not alive' % self.userid)
        
        # Get active weapon
        playerWeapon = self.getWeapon()
        
        if playerWeapon != 'knife':
            es.delayed('0.001', 'es_xgive %s weapon_%s' % (self.userid, playerWeapon))
        
        if playerWeapon == 'hegrenade':
            es.delayed('0.001', 'es_xsexec %s "use weapon_hegrenade"' % self.userid)
    
    def getWeapon(self):
        '''Returns the weapon for the players level.'''
        if dict_weaponOrderSettings['currentWeaponOrderFile'] != None:
            return dict_weaponOrders[dict_weaponOrderSettings['currentWeaponOrderFile']][self.attributes['level']][0]

# ==============================================================================
#   WEAPON ORDER CLASS
# ==============================================================================
class WeaponOrder:
    '''Parses weapon order files.'''
    
    def __init__(self, fileName):
        '''Initializes the WeaponOrder class.'''
        # Set variables
        self.filePath = getGameDir('cfg/gungame/weapon_order_files/%s' % fileName)
        self.fileName = fileName
        
        # Check to see if it has been registered before
        if not self.__isRegistered(fileName):
            self.__parse()
        else:
            echo('gungame', 0, 1, 'WeaponOrder:AlreadyRegistered', {'file': fileName})
    
    def __parse(self):
        '''Parses the weapon file.'''
        # Try to open the file
        try:
            weaponOrderFile = open(self.filePath, 'r')
        except IOError, e:
            raise FileError('Cannot parse weapon order file (%s): IOError: %s' % e)
        
        # Variable preparation
        dict_tempWeaponOrder = {}
        dict_tempWeaponOrderSettings = {}
        levelCounter = 0
        
        # Clean and format the lines
        lines = [x.strip().lower() for x in weaponOrderFile.readlines()]
        lines = filter(lambda x: x and (not x.startswith('//')), lines)
        
        # Close the file, we have the lines
        weaponOrderFile.close()
        
        # Loop through each line
        for line in lines:
            # Remove double spacing
            while '  ' in line:
                line = line.replace('  ', ' ')
            
            # Split line
            list_splitLine = line.split()
            
            # Check the weapon name
            weaponName = str(list_splitLine[0])
            if weaponName not in list_validWeapons:
                echo('gungame', 0, 0, 'WeaponOrder:InvalidWeapon', {'weapon': weaponName})
                continue
            
            # Multikill?
            if len(list_splitLine) > 1:
                # Make sure the multikill value is numerical
                if not isNumeric(list_splitLine[1]):
                    echo('gungame', 0, 0, 'WeaponOrder:MultikillNotNumeric', {'weapon': weaponName, 'to': list_splitLine[1]})
                    continue
                
                # Get multikill value
                multiKillValue = int(list_splitLine[1])
                
                # Set values for this level
                levelCounter += 1
                list_splitLine[1] = multiKillValue
            else:
                # Set values for this level
                levelCounter += 1
                list_splitLine.append(1)
            
            # Set level values
            dict_tempWeaponOrder[levelCounter] = list_splitLine
        
        # Get display names
        weaponOrderINI = ConfigObj(getGameDir('cfg/gungame/gg_weapon_orders.ini'))
        
        # Loop through each section (the section name is the "Display Name") in the INI
        for displayName in weaponOrderINI:
            if weaponOrderINI[displayName]['fileName'] == self.fileName: dict_tempWeaponOrderSettings['displayName'] = displayName
        
        # Set the order type to default
        dict_tempWeaponOrderSettings['weaponOrder'] = '#default'
        
        # Copy the temporary dictionaries over
        dict_weaponOrderSettings[self.fileName] = dict_tempWeaponOrderSettings.copy()
        dict_weaponOrders[self.fileName] = dict_tempWeaponOrder.copy()
    
    def __isRegistered(self, fileName):
        '''Checks if a weapon order is already registered.'''
        return dict_weaponOrders.has_key(fileName)
    
    def echo(self):
        '''Echos the current weapon order to console.'''
        weaponOrder = dict_weaponOrders[self.fileName]
        
        es.dbgmsg(0, '[GunGame] ')
        echo('gungame', 0, 0, 'WeaponOrder:Echo:Info')
        es.dbgmsg(0, '[GunGame] ')
        echo('gungame', 0, 0, 'WeaponOrder:Echo:FileName', {'file': self.fileName})
        echo('gungame', 0, 0, 'WeaponOrder:Echo:DisplayName', {'name': dict_weaponOrderSettings[self.fileName]['displayName']})
        echo('gungame', 0, 0, 'WeaponOrder:Echo:Order', {'order': self.getWeaponOrderType()})
        es.dbgmsg(0, '[GunGame] ')
        es.dbgmsg(0, '[GunGame] +-------+-----------+---------------+')
        echo('gungame', 0, 0, 'WeaponOrder:Echo:TableColumns')
        es.dbgmsg(0, '[GunGame] +-------+-----------+---------------+')
        
        # Loop through each level
        for level in dict_weaponOrders[self.fileName]:
            # Set variables
            weaponName = dict_weaponOrders[self.fileName][level][0]
            multiKillValue = dict_weaponOrders[self.fileName][level][1]
            cleanLevel = '0%d' % level if level < 10 else level
            
            # Print to console
            es.dbgmsg(0, '[GunGame] |  %s   |     %d     | %s%s|' % (cleanLevel, multiKillValue, weaponName, ' ' * (14-len(weaponName))))
        
        es.dbgmsg(0, '[GunGame] +-------+-----------+---------------+')
        es.dbgmsg(0, '[GunGame] ')
    
    def setMultiKillOverride(self, value):
        '''Sets the multikill override.'''
        value = int(value)
        
        # Create a temporary weapon order dictionary
        dict_tempWeaponOrder = dict_weaponOrders[self.fileName].copy()
        
        # Loop through the weapon order dictionary
        for level in dict_tempWeaponOrder:
            # Set multikill if its not a knife or a hegrenade
            if dict_tempWeaponOrder[level][0] != 'knife' and dict_tempWeaponOrder[level][0] != 'hegrenade':
                dict_tempWeaponOrder[level][1] = value
        
        # Copy the temporary weapon order back
        dict_weaponOrders[self.fileName] = dict_tempWeaponOrder.copy()
        
        # Rebuild weapon order menu
        self.buildWeaponOrderMenu()
        
        # Tell players the multikill value changed
        msg('gungame', '#all', 'WeaponOrder:MultikillValuesChanged', {'to': value})
        es.server.cmd('mp_restartgame 2')
    
    def setMultiKillDefaults(self):
        '''Sets the multikill values back to their default values.'''
        # Re-parse the file
        self.__parse()
        
        # Tell players the multikill values have been reset
        msg('gungame', '#all', 'WeaponOrder:MultikillReset')
        es.server.cmd('mp_restartgame 2')
    
    def setWeaponOrderFile(self):
        '''Sets the current weapon order file to this.'''
        # Check its not the current one
        if dict_weaponOrderSettings['currentWeaponOrderFile'] == self.fileName:
            return
        
        # Set the current weapon order file
        dict_weaponOrderSettings['currentWeaponOrderFile'] = self.fileName
        
        # Rebuild the weapon order menu
        self.buildWeaponOrderMenu()
        
        # Tell players the weapon order file has changed
        msg('gungame', '#all', 'WeaponOrder:FileChanged', {'to': self.fileName})
        es.server.cmd('mp_restartgame 2')
    
    def getWeaponOrderType(self):
        '''Returns the weapon order type.'''
        return dict_weaponOrderSettings[self.fileName]['weaponOrder']
    
    def __setWeaponOrder(self, value):
        '''Sets the weapon order type.'''
        # Set the weapon order type
        dict_weaponOrderSettings[self.fileName]['weaponOrder'] = str(value)
        
        # Restart game
        es.server.cmd('mp_restartgame 2')
    
    def changeWeaponOrderType(self, weaponOrder):
        '''Changes the weapon order type.'''
        weaponOrder = str(weaponOrder.lower())
        
        # Is this the current value?
        if weaponOrder == self.getWeaponOrderType():
            raise ValueError('Cannot change weapon order type (%s): this is the current weapon order type.' % weaponOrder)
        
        # Shuffled
        if weaponOrder == '#random':
            # Get temporary weapon order
            dict_tempWeaponOrder = dict_weaponOrders[self.fileName].copy()
            
            # Get levels and shuffle it
            list_gungameLevels = dict_tempWeaponOrder.keys()
            random.shuffle(list_gungameLevels)
            
            # Get weapons and shuffle it
            list_gungameWeapons = dict_tempWeaponOrder.values()
            random.shuffle(list_gungameWeapons)
            
            # Loop through the levels and set the weapons
            weaponArrayNumber = 0
            for level in list_gungameLevels:
                dict_tempWeaponOrder[level] = list_gungameWeapons[weaponArrayNumber]
                weaponArrayNumber += 1
            
            # Set the weapon orders back
            dict_weaponOrders[self.fileName] = dict_tempWeaponOrder
            
            # Tell the players the weapon order has changed
            self.__setWeaponOrder('#random')
            msg('gungame', '#all', 'WeaponOrder:ChangedTo', {'to': '#random'})
        
        # Default
        elif weaponOrder == '#default':
            # Re-parse the file
            self.__parse(self.fileName, filePath)
            
            # Tell the players the weapon order has changed
            msg('gungame', '#all', 'WeaponOrder:ChangedTo', {'to': '#default'})
        
        # Reversed
        elif weaponOrder == '#reversed':
            # Get temporary weapon order
            dict_tempWeaponOrder = dict_weaponOrders[self.fileName].copy()
            
            # Get levels and weapons
            list_gungameLevels = dict_tempWeaponOrder.keys()
            list_gungameWeapons = dict_tempWeaponOrder.values()
            
            # Reverse it
            list_gungameWeapons.reverse()
            
            # Loop through the levels and reverse the weapons
            weaponArrayNumber = 0
            for level in list_gungameLevels:
                dict_tempWeaponOrder[level] = list_gungameWeapons[weaponArrayNumber]
                weaponArrayNumber += 1
            
            # Set the weapon orders back
            dict_weaponOrders[self.fileName] = dict_tempWeaponOrder
            
            # Tell the players the weapon order has changed
            self.__setWeaponOrder('#reversed')
            msg('gungame', '#all', 'WeaponOrder:ChangedTo', {'to': '#reversed'})
        
        # Invalid value
        else:
            raise ValueError('Cannot change weapon order type (%s): must be: #default, #random or #reversed.' % weaponOrder)
    
    def buildWeaponOrderMenu(self):
        '''Builds the weapon order menu.'''
        dict_tempWeaponOrder = dict_weaponOrders[self.fileName].copy()
        
        # Create a list of level numbers to use for creating the popup
        list_gungameLevels = dict_tempWeaponOrder.keys()
        
        # Create a list of weapon names to use for creating the popup
        list_gungameWeapons = dict_tempWeaponOrder.values()
        
        # Find out how many menu pages there are going to be
        totalMenuPages = int(round((int(getTotalLevels()) * 0.1) + 0.4))
        
        # Create a variable to store the current page count
        buildPageCount = 1
        
        # Create a variable to keep track of the index number for pulling the level/weapon information from the list_gungameLevels and list_gungameWeapons
        levelCountIndex = 0
        
        # Create a variable to track the "max" or the "cap" of indexes to retrieve from the lists
        levelCountMaxIndex = 0
        
        # Do the following loop until we have reached the total number of pages that we have to create
        while buildPageCount <= totalMenuPages:
            # Set a Python variable so we don't have to keep on formatting text for the menu name
            menuName = 'gungameWeaponOrderMenu_page%d' %buildPageCount
            
            # Check to see if the popup "gungameWeaponOrderMenu" exists
            if popuplib.exists('gungameWeaponOrderMenu'):
                # The popup exists...let's unsend it
                popuplib.unsendname(menuName, playerlib.getUseridList('#human'))
                
                # Now, we need to delete it
                popuplib.delete(menuName)
            
            # Let's create the "gungameWeaponOrderMenu" popup and name it according to the page number
            gungameWeaponOrderMenu = popuplib.create(menuName)
            
            # Make sure there is more than 1 page of levels/weapons
            if totalMenuPages > 1:
                # Now, we add the "Title Text", along with the page number as well as the following line for aesthetic appearances, "--------"
                gungameWeaponOrderMenu.addline('GunGame Weapon Order:  (%d/%d)\n----------------------------' %(buildPageCount, totalMenuPages))
            # Wow. Only 1 page of levels/weapons...no page number needed, then.
            else:
                # Now we add the "Title Text" as well as the following line for aesthetic appearances, "--------"
                gungameWeaponOrderMenu.addline('GunGame Weapon Order:\n----------------------------')
            
            levelCountMaxIndex += 10
            if levelCountMaxIndex > len(list_gungameLevels) - 1:
                levelCountMaxIndex = len(list_gungameLevels)
                
            for level in range(levelCountIndex, levelCountMaxIndex):
                # For aesthetic purposes, I will be adding a "space" for weapons in the list below level 10
                if int(list_gungameLevels[levelCountIndex]) < 10:
                    # Now, we add the weapons to the popup, as well as number them by level (with the extra "space")
                    gungameWeaponOrderMenu.addline('->%d.   [%d] %s' %(list_gungameLevels[levelCountIndex], list_gungameWeapons[levelCountIndex][1], list_gungameWeapons[levelCountIndex][0]))
                else:
                    # Now, we add the weapons to the popup, as well as number them by level (without the extra "space")
                    gungameWeaponOrderMenu.addline('->%d. [%d] %s' %(list_gungameLevels[levelCountIndex], list_gungameWeapons[levelCountIndex][1],list_gungameWeapons[levelCountIndex][0]))
                    
                # Increment the index counter by 1 for the next for loop iteration
                levelCountIndex += 1
                
            # Once again, for aesthetic purposes (to keep the menu the same size), we will add blank lines if the listed levels in the menu do not = 10
            # See if this is the final page of the menu
            if buildPageCount == totalMenuPages:
                # Calculate the number of needed blank lines in the menu
                neededBlankLines = 10 - int(round((len(list_gungameLevels) * 0.1) + 0.4))
                
                # Set a variable for the loop below to keep track of the number of blank lines left to add
                blankLineCount = 0
                
                # Loop to add the blank lines to the menu
                while blankLineCount < neededBlankLines:
                    gungameWeaponOrderMenu.addline(' ')
                    blankLineCount += 1
                    
            # Add the "----------" separator at the bottom of the menu
            gungameWeaponOrderMenu.addline('----------------------------')
            
            # Add the "browsing pages" options at the bottom of the menu
            # If this is NOT page #1 of the weapons menu
            if buildPageCount != 1:
                # If the current page number IS NOT == to the total number of pages
                if buildPageCount != totalMenuPages:
                    gungameWeaponOrderMenu.addline('->8. Previous Page')
                    gungameWeaponOrderMenu.addline('->9. Next Page')
                    gungameWeaponOrderMenu.submenu(8, 'gungameWeaponOrderMenu_page%d' %(buildPageCount - 1))
                    gungameWeaponOrderMenu.submenu(9, 'gungameWeaponOrderMenu_page%d' %(buildPageCount + 1))
                # The current page number IS == to the total number of pages
                else:
                    gungameWeaponOrderMenu.addline('->8. Previous Page')
                    gungameWeaponOrderMenu.addline('->9. First Page')
                    gungameWeaponOrderMenu.submenu(8, 'gungameWeaponOrderMenu_page%d' %(buildPageCount - 1))
                    gungameWeaponOrderMenu.submenu(9, 'gungameWeaponOrderMenu_page1')
            # This IS page #1 of the weapons menu
            else:
                # If the total number of pages is > 1
                if totalMenuPages > 1:
                    # If the total number of pages is > 2
                    if totalMenuPages > 2:
                        gungameWeaponOrderMenu.addline('->8. Last Page')
                        gungameWeaponOrderMenu.addline('->9. Next Page')
                        gungameWeaponOrderMenu.submenu(8, 'gungameWeaponOrderMenu_page%d' %totalMenuPages)
                        gungameWeaponOrderMenu.submenu(9, 'gungameWeaponOrderMenu_page%d' %(buildPageCount + 1))
                    # The total number of pages == 2
                    else:
                        gungameWeaponOrderMenu.addline('->9. Last Page')
                        gungameWeaponOrderMenu.submenu(9, 'gungameWeaponOrderMenu_page%d' %(buildPageCount + 1))
            # Make sure that the player can Exit out of the menu
            gungameWeaponOrderMenu.select(10, weaponOrderMenuHandler)
            
            # Finally, we add the "Exit" option to the menu
            gungameWeaponOrderMenu.addline('0. Exit')
            
            # Now, we end this whole menu-making debacle by making the menu "sticky"
            gungameWeaponOrderMenu.displaymode = 'sticky'
            
            # Increment the page count for the next while loop iteration to create another menu page
            buildPageCount += 1

# ==============================================================================
#   CONFIG CLASS
# ==============================================================================
class Config:
    '''Class for registration of config files used by GunGame.'''
    
    def __init__(self, name):
        '''Sets the class's variables.'''
        self.name = name
        self.path = getGameDir('cfg/gungame/%s' % name)
        
        # Check to see if it has been loaded before
        if not self.__isLoaded():
            # Add to configs list
            list_configs.append(self.name)
            
            # Parse file
            self.__parse()
    
    def __isLoaded(self):
        '''Checks to see if the config is already loaded.'''
        return (self.name in list_configs)
    
    def __parse(self):
        '''Parses the config file.'''
        # Try to open the config file
        try:
            configFile = open(self.path, 'r')
        except IOError, e:
            if not configName.lower() in list_criticalConfigs:
                raise FileError('Unable to load config (%s): %s' % (self.name, e))
            else:
                es.server.queuecmd('es_xunload gungame')
                raise FileError('Unable to load required config (%s): %s' % (self.name, e))
        
        # Format lines
        lines = map(lambda x: x.strip().lower(), configFile.readlines())
        lines = filter(lambda x: x and (not x.startswith('//')), lines)
        
        # Close file
        configFile.close()
        
        # Loop through each line in the Config
        for line in lines:
            # Remove excess whitespace
            while '  ' in line:
                line = line.replace('  ', ' ')
            
            # Get variable name and value
            variableName, variableValue = line.split(' ', 1)
            
            # Don't re-add variables, but change the value instead
            if dict_variables.has_key(variableName):
                dict_variables[variableName].set(variableValue)
                echo('gungame', 0, 2, 'Config:AlreadyAdded', {'name': variableName})
                
                # Skip to next line
                continue
            
            # Add the variable and value
            dict_variables[variableName] = es.ServerVar(variableName, variableValue)
            dict_variables[variableName].set(variableValue)
            
            # Make variable public
            dict_variables[variableName].addFlag('notify')
            
            # Use a server command to fire the server_cvar event
            es.server.cmd('%s %s' % (variableName, variableValue))
            
            # Is an addon?
            if addonExists(variableName):
                continue
            
            # Set the CFG value
            if dict_cfgSettings.has_key(self.name):
                dict_cfgSettings[self.name].append(variableName)
                continue
            
            # Make the CFG setting for this config
            dict_cfgSettings[self.name] = [variableName]
        
        # Print config loaded
        echo('gungame', 0, 0, 'Config:Loaded', {'name': self.name})

# ==============================================================================
#   SOUND CLASS
# ==============================================================================
class InvalidSoundPack(Exception):
    pass

class SoundError(Exception):
    pass

class Sounds:
    '''Soundpack class, adds sounds from a soundpack.'''
    
    def __init__(self, soundPackName):
        '''Initializes the Sound class.'''
        self.soundPackName = soundPackName
        
        # Set up the sound pack path
        if '.ini' in soundPackName:
            self.soundPackPath = getGameDir('cfg/gungame/sound_packs/%s' % soundPackName)
        else:
            self.soundPackPath = getGameDir('cfg/gungame/sound_packs/%s.ini' % soundPackName)
        
        # Make sure that the sound pack INI exists
        if self.__checkSoundPack():
            self.__parse()
        else:
            raise InvalidSoundPack('Cannot register soundpack (%s): file not found.' % soundPackName)
    
    def __checkSoundPack(self):
        '''Checks to see if the file exists.'''
        return os.path.isfile(self.soundPackPath)
    
    def __parse(self):
        # Open the INI file
        soundPackINI = ConfigObj(self.soundPackPath)
        
        # Loop through each section in the soundpack
        for section in soundPackINI:
            # Loop through each option in the soundpack INI
            for option in soundPackINI[section]:
                # Get the sound file
                soundFile = soundPackINI[section][option]
                
                # Make sure there is a sound
                if soundPackINI.get(section, option) == '0':
                    dict_sounds[option] = 0
                
                # Check to make sure that the sound file exists
                if self.__checkSound(soundFile):
                    # Add sound here
                    dict_sounds[option] = soundFile
                else:
                    # The sound may not exist, so we warn them that we were unable to locate it
                    echo('gungame', 0, 0, 'Sounds:CannotAdd', {'file': soundFile})
                    
                    # Add it anyway
                    dict_sounds[option] = soundFile
        
        # Add downloadables
        addDownloadableSounds()
    
    def __checkSound(self, soundFile):
        # Set path
        soundPath = getGameDir('sound/%s' % soundFile)
        
        # File exists?
        return os.path.isfile(soundPath)

# ==============================================================================
#   ADDON CLASS
# ==============================================================================
class AddonError(Exception):
    pass
    
class Addon:
    def __init__(self, addonName):
        self.addon = str(addonName)
        
        # Make sure the addon exists
        if not self.validateAddon():
            raise AddonError('Cannot create addon (%s): addon folder doesn\'t exist.' % addonName)
        
        # Set up default attributes for this addon
        self.displayName = 'Untitled Addon'
        self.commands = {}
        self.dependencies = []
        self.menu = None
        
        # Tell them the addon was registered
        echo('gungame', 0, 0, 'Addon:Registered', {'name': addonName})

    def __del__(self):
        # Remove all registered dependencies
        for dependency in self.dependencies:
            # Remove dependency
            dict_dependencies[dependency].delDependent(self.addon)
            echo('gungame', 0, 2, 'Addon:DependencyRemoved', {'name': self.addon, 'dependency': dependency})
        
        echo('gungame', 0, 0, 'Addon:Unregistered', {'name': self.addon})
    
    def validateAddon(self):
        if os.path.isdir(getGameDir('addons/eventscripts/gungame/included_addons/%s' % self.addon)):
            # Is an included addon
            self.addonType = 'included'
            return True
        elif os.path.isdir(getGameDir('addons/eventscripts/gungame/custom_addons/%s' % self.addon)):
            # Is a custom addon
            self.addonType = 'custom'
            return True
        else:
            return False
    
    '''Command options:'''
    def registerCommand(self, command, function, syntax='', console=True, log=True):
        if not callable(function):
            raise AddonError('Cannot register command (%s): callback is not callable.' % command)
        
        # Add command to commands dictionary
        self.commands[command] = function, syntax, console, log
        
        # Register console command (set console to False if you are getting conflicts)
        if console:
            # Register block
            es.addons.registerBlock('gungamelib', command, self.__functionCallback)
            
            # Register command if its not already registered
            if not es.exists('command', 'gg_%s' % command):
                es.regcmd('gg_%s' % command, 'gungamelib/%s' % command, 'Syntax: %s' % syntax)
    
    def unregisterCommands(self):
        # Unregister the block of each command
        for command in filter(lambda x: x[2], self.commands):
            es.addons.unregisterBlock('gungamelib', command)
    
    def callCommand(self, command, userid, arguments):
        if not self.commands.has_key(command):
            raise AddonError('Cannot call command (%s): not registered.' % command)
        
        # Clean up the variables
        userid = int(userid)
        arguments = list(arguments)
        
        # Get details of the admin who called the command
        adminIndex = getPlayer(userid)['index'] if userid else -1
        name = es.getplayername(userid) if userid else 'CONSOLE'
        steamid = es.getplayersteamid(userid) if userid else 'CONSOLE'
        
        # Get command info
        callback, syntax, console, log = self.commands[command]
        
        # Try and call the command
        try:
            callback(userid, *arguments)
        except TypeError:
            # Show an Invalid Syntax message to the player
            msg('gungame', userid, 'InvalidSyntax', {'cmd': command, 'syntax': syntax})
            return
        
        # Tell everyone about what the admin ran
        saytext2('gungame', '#all', adminIndex, 'AdminRan', {'name': name, 'command': command, 'args': ' '.join(arguments)})
        
        # Print to the admin log
        if userid and log and getVariableValue('gg_admin_log'):
            # Get file info
            logFileName = getGameDir('addons/eventscripts/gungame/logs/adminlog.txt')
            size = os.path.getsize(logFileName) / 1024
            
            # Set log file opening mode
            if size > getVariableValue('gg_admin_log'):
                logFile = open(logFileName, 'w')
                logFile.write('%s Log cleared, limit reached.\n' % time.strftime('[%d/%m/%Y %H:%M:%S]'))
            else:
                logFile = open(logFileName, 'a')
            
            # Open write to log then close
            logFile.write('%s Admin %s <%s> ran: %s %s\n' % (time.strftime('[%d/%m/%Y %H:%M:%S]'), name, steamid, command, ' '.join(arguments)))
            logFile.close()
    
    def hasCommand(self, command):
        return self.commands.has_key(command)
    
    def getCommandSyntax(self, command):
        if not self.commands.has_key(command):
            raise AddonError('Cannot get command syntax (%s): not registered.' % command)
        
        return self.commands[command][1]
    
    def __functionCallback(self):
        # Call command
        self.callCommand(es.getargv(0)[3:], 0, formatArgs())
    
    '''Menu options:'''
    def createMenu(self, selectfunc):
        self.menu = popuplib.easymenu(self.addon, None, selectfunc)
        self.menu.settitle(self.displayName)
    
    def setDescription(self, description):
        if not self.hasMenu(): raise AddonError('Cannot set menu description (%s): menu hasn\'t been created.' % self.addon)
        
        self.menu.setdescription('%s\n * %s' % (self.menu.c_beginsep, description))
    
    def hasMenu(self):
        return (self.menu != None)
    
    def sendMenu(self, userid):
        if not self.hasMenu(): raise AddonError('Cannot show menu (%s): menu hasn\'t been created.' % self.addon)
        
        self.menu.send(userid)
    
    '''Display name options:'''
    def setDisplayName(self, name):
        self.displayName = name
        
        # Set menu title (if created)
        if self.hasMenu():
            self.menu.settitle(name)
    
    def getDisplayName(self):
        return self.displayName
    
    '''Dependency options:'''
    def addDependency(self, dependencyName, value):
        if isNumeric(value):
            value = int(value)
        
        # Check if dependency already exists
        if not dict_dependencies.has_key(dependencyName):
            # Check if dependency is a valid gungame variable
            if dict_variables.has_key(dependencyName):
                
                # Add dependency and original value to addon attributes
                self.dependencies.append(dependencyName)
                
                # Create dependency class
                dict_dependencies[dependencyName] = addonDependency(dependencyName, value, self.addon)
                
                # Set GunGame variable to dependents value
                setVariableValue(dependencyName, value)
            else:
                raise AddonError('Cannot add dependency (%s): variable not registered.' % dependencyName)
        # Dependent is already registered
        else:
            # Add dependency and original value to addon attributes
            self.dependencies.append(dependencyName)
            
            # Add dependent to existing dependency
            dict_dependencies[dependencyName].addDependent(value, self.addon)
    
    def delDependency(self, dependencyName):
        # Check if dependency exists first
        if dict_dependencies.has_key(dependencyName):
            # Delete dependency
            dict_dependencies[dependencyName].delDependent(self.addon)
        else:
            raise AddonError('Cannot delete dependency (%s): not registered.' % dependencyName)

# ==============================================================================
#   ADDON DEPENDENCY CLASS
# ==============================================================================
class addonDependency:
    def __init__(self, dependencyName, value, dependentName):
        # Setup dependency class vars
        self.dependency = dependencyName
        self.dependencyValue = value
        self.dependencyOriginalValue = getVariableValue(dependencyName)
        self.dependentList = [dependentName]
        
        echo('gungame', 0, 2, 'Dependency:Registered', {'name': self.dependency})
    
    def addDependent(self, value, dependentName):
        # Check if dependents value is the same as the previous dependents value
        if self.dependencyValue == value:
            # Add dependent to list of dependencies dependents
            self.dependentList.append(dependentName)
            echo('gungame', 0, 1, 'Dependency:Registered', {'name': self.dependency})
        # Dependent has a different value
        else:
            # Unload addon since it conflicts with existant dependents
            if dict_addons[dependentName].addonType == 'included':
                setVariableValue(dependentName, 0)
            else:
                es.unload('gungame/custom_addons/%s' % dependentName)
            
            echo('gungame', 0, 0, 'Dependency:Failed', {'name': self.dependency})
    
    def delDependent(self, dependentName):
        # Remove dependent from dependents list
        if dependentName in self.dependentList:
            self.dependentList.remove(dependentName)
            echo('gungame', 0, 1, 'Dependency:Unregistered', {'name': self.dependency})
            
            # Check if there are any more dependencies
            if not self.dependentList:
                if dict_variables:
                    # Set Variable back to it's original value
                    setVariableValue(self.dependency, self.dependencyOriginalValue)
                
                # Delete dependency
                del dict_dependencies[self.dependency]

# ==============================================================================
#   MESSAGE CLASS
# ==============================================================================
class Message:
    '''Message class is used to broadcast linguistic messages around the server,
    with the use of translation files.'''
    
    def __init__(self, addonName, filter):
        '''Initializes the class.'''
        # Format filter
        filter = str(filter)
        if filter.isdigit():
            self.filter = int(filter)
        else:
            self.filter = filter
        
        # Set other variables
        self.addonName = addonName
        self.strings = None

    def __loadStrings(self):
        '''Loads the Strings instance into the class.'''
        # Does the language file exist?
        if os.path.isfile(getGameDir('cfg/gungame/translations/%s.ini' % self.addonName)):
            self.strings = langlib.Strings(getGameDir('cfg/gungame/translations/%s.ini' % self.addonName))
        else:
            raise IOError('Cannot load strings (%s): no string file exists.' % self.addonName)
    
    def __cleanString(self, string):
        '''Cleans the string for output to the console.'''
        return string.replace('\3', '').replace('\4', '').replace('\1', '')
    
    def __formatString(self, string, tokens, player=None):
        '''Retrieves and formats the string.'''
        # Try to get string
        try:
            rtnStr = self.strings(string, tokens, player.get('lang'))
        except AttributeError:
            rtnStr = self.strings(string, tokens)
        
        # Format it
        rtnStr = rtnStr.replace('#lightgreen', '\3').replace('#green', '\4').replace('#default', '\1')
        rtnStr = rtnStr.replace('\\3', '\3').replace('\\4', '\4').replace('\\1', '\1')
        rtnStr = rtnStr.replace('\\x03', '\3').replace('\\x04', '\4').replace('\\x01', '\1')
        
        # Return the string
        return rtnStr
    
    def msg(self, string, tokens, showPrefix = False):
        # Load the strings
        self.__loadStrings()
        
        # Format the message
        if showPrefix:
            message = '\4[%s]\1 ' % getAddonDisplayName(self.addonName)
        else:
            message = ''
        
        # Loop through the players in the filter
        if isinstance(self.filter, int):
            # Get player object
            player = playerlib.getPlayer(self.filter)
            
            # Send message
            es.tell(self.filter, '#multi', '%s%s' % (message, self.__formatString(string, tokens, player)))
        else:
            if self.filter == '#all':
                # Show in console
                self.echo(0, string, tokens, showPrefix)
            
            # Get player list
            players = playerlib.getUseridList(self.filter)
            
            for userid in players:
                player = playerlib.getPlayer(userid)
                
                es.tell(int(player), '#multi', '%s%s' % (message, self.__formatString(string, tokens, player)))
    
    def hudhint(self, string, tokens):
        # Load the strings
        self.__loadStrings()
        
        # Loop through the players in the filter
        if isinstance(self.filter, int):
            # Get player object
            player = playerlib.getPlayer(self.filter)
            
            # Send message
            usermsg.hudhint(int(player), self.__formatString(string, tokens, player))
        else:
            # Get player list
            players = playerlib.getUseridList(self.filter)
            
            for userid in players:
                player = playerlib.getPlayer(userid)
                
                # Send message
                usermsg.hudhint(int(player), self.__formatString(string, tokens, player))
    
    def saytext2(self, index, string, tokens, showPrefix = False):
        # Load the strings
        self.__loadStrings()
        
        # Format the message
        if showPrefix:
            message = '\4[%s]\1 ' % getAddonDisplayName(self.addonName)
        else:
            message = ''
        
        # Loop through the players in the filter
        if isinstance(self.filter, int):
            # Get player object
            player = playerlib.getPlayer(self.filter)
            
            # Send message
            usermsg.saytext2(int(player), index, '\1%s%s' % (message, self.__formatString(string, tokens, player)))
        else:
            # Get player list
            players = playerlib.getPlayerList(self.filter)
            
            if self.filter == '#all':
                # Show in console
                self.echo(0, string, tokens, showPrefix)
            
            for player in players:
                # Send message
                usermsg.saytext2(int(player), index, '\1%s%s' % (message, self.__formatString(string, tokens, player)))
    
    def centermsg(self, string, tokens):
        # Load the strings
        self.__loadStrings()
        
        # Loop through the players in the filter
        if isinstance(self.filter, int):
            # Get player object
            player = playerlib.getPlayer(self.filter)
            
            # Send message
            usermsg.centermsg(int(player), self.__formatString(string, tokens, player))
        else:
            # Get player list
            players = playerlib.getUseridList(self.filter)
            
            for userid in players:
                player = playerlib.getPlayer(userid)
                
                # Send message
                usermsg.centermsg(int(player), self.__formatString(string, tokens, player))
    
    def echo(self, level, string, tokens, showPrefix = False):
        # Load the strings
        self.__loadStrings()
        
        # Is the debug level high enough?
        if int(gungameDebugLevel) < level:
            return
        
        # Format the message
        if showPrefix:
            message = '[%s] ' % getAddonDisplayName(self.addonName)
        else:
            message = ''
        
        # Loop through the players in the filter
        if type(self.filter) == int and self.filter != 0:
            # Get player object
            player = playerlib.getPlayer(self.filter)
            
            # Get clean string
            cleanStr = self.__cleanString(self.__formatString(string, tokens, player))
            
            # Send message
            usermsg.echo(int(player), '%s%s' % (message, cleanStr))
        elif self.filter == 0:
            # Get clean string
            cleanStr = self.__cleanString(self.__formatString(string, tokens, None))
            
            # Print message
            es.dbgmsg(0, '%s%s' % (message, cleanStr))
        else:
            # Get player list
            players = playerlib.getUseridList(self.filter)
            
            for userid in players:
                player = playerlib.getPlayer(userid)
                
                # Get clean string
                cleanStr = self.__cleanString(self.__formatString(string, tokens, player))
                
                # Send message
                usermsg.echo(int(player), '%s%s' % (message, cleanStr))

# ==============================================================================
#   EASYINPUT CLASS
# ==============================================================================
class EasyInput:
    '''Makes "Esc"-style input boxes quickly and simply.
    
    Inspiration:
     * SuperDave (http://forums.mattie.info/cs/forums/viewtopic.php?t=21958)
    '''
    
    def __init__(self, name, callback, extras=''):
        '''Called on initialization, sets default values and registers the
        command.'''
        # Check the callback is callable
        if not callable(callback):
            raise ValueError('Cannot create EasyInput object: callback must be callable.')
        
        # Set variables
        self.name = name
        self.userid = 0
        self.callback = callback
        self.extras = extras
        self.setTimeout(199)
        
        # Set default options
        self.title = 'Untitled'
        self.text = 'Enter an option:'
        
        # Create command variables
        self.cmd = '_easyinput_%s' % name
        
        # Unregister command
        if es.exists('clientcommand', self.cmd):
            es.unregclientcmd(self.cmd)
            es.addons.unregisterBlock('gungamelib', self.cmd)
        
        # Register the command again
        es.addons.registerBlock('gungamelib', self.cmd, self.__inputCallback)
        es.regclientcmd(self.cmd, 'gungamelib/%s' % self.cmd, 'Command for retrieving input box data.') 
    
    def setTitle(self, title):
        '''Self-explantory.'''
        # Set title
        self.title = title
    
    def setText(self, text):
        '''Self-explantory.'''
        # Set text
        self.text = text
    
    def setTimeout(self, timeout):
        '''Sets timeout for the player to press "Esc" before the menu is
        discarded. Value must be between 10 and 199, inclusive.'''
        # Make timeout an integer
        timeout = int(timeout)
        
        # Check timeout
        if timeout not in range(10, 200):
            raise ValueError('Cannot set timeout (%s): value must be between 10 and 200.' % timeout)
        
        # Set timeout
        self.timeout = timeout
    
    def send(self, userid):
        '''Sends the input box to <userid>.'''
        userid = int(userid)
        
        # Send input
        es.escinputbox(self.timeout, userid, self.title, self.text, self.cmd)
        
        # Make it the accepted userid
        self.userid = userid
    
    def __inputCallback(self):
        '''Called when the input is sent back to the server. Will call the
        callback with the userid of the user, the arguments and the value they
        inputted.'''
        # Get userid
        userid = int(es.getcmduserid())
        
        # Check the userid
        if userid != self.userid:
            # Tell them they can't run this
            msg('gungame', userid, 'EasyInput:Unauthorized')
            return
        
        # Call the function, if it exists
        self.callback(userid, formatArgs(), self.extras)

# ==============================================================================
#  WINNERS CLASS
# ==============================================================================
class Winners:
    ''' Class used for tracking and storing Winners'''
    
    def __init__(self, uniqueid):
        self.uniqueid = str(uniqueid)
        
        # Make sure that the winner's database has been loaded
        if not getGlobal('winnersloaded'):
            # Load the database using pickle
            loadWinnerDatabase()
        
        if not dict_winners.has_key(self.uniqueid):
            self.attributes = {'wins': 0, 'timestamp': time.time()}
            dict_winners[self.uniqueid] = self.attributes
        else:
            self.attributes = dict_winners[self.uniqueid]
    
    def __getitem__(self, item):
        # We will be nice and convert the "item" to a lower-cased string
        item = str(item).lower()
        
        # Let's make sure that the item that they are trying to change exists
        if item in self.attributes:
            # Allowing the retrieving of attributes in the dictionary
            return self.attributes[item]
    
    def __setitem__(self, item, value):
        # We will be nice and convert the "item" to a lower-cased string
        item = str(item).lower()
        
        # Let's make sure that the item that they are trying to change exists
        if item in self.attributes:
            if item == 'wins':
                self.attributes[item] = int(value)
            if item == 'timestamp':
                self.attributes[item] = float(value)

# ==============================================================================
#  CLASS WRAPPERS
# ==============================================================================
def getPlayer(userid):
    userid = int(userid)
    try:
        return Player(userid)
    except (UseridError, TypeError), e:
        raise e

def getWeaponOrderFile(weaponOrderFile):
    try:
        return WeaponOrder(weaponOrderFile)
    except TypeError, e:
        raise e

def getConfig(configName):
    try:
        return Config(configName)
    except TypeError, e:
        raise e

def getSoundPack(soundPackName):
    try:
        return Sounds(soundPackName)
    except TypeError, e:
        raise e

def getWinner(uniqueid):
    try:
        return Winners(uniqueid)
    except TypeError, e:
        raise e

# ==============================================================================
#   MESSAGE FUNCTIONS
# ==============================================================================
def msg(addon, filter, string, tokens={}, showPrefix=True):
    if filter == 0:
        echo(addon, 0, 0, string, tokens, showPrefix)
    else:
        Message(addon, filter).msg(string, tokens, showPrefix)
    
def echo(addon, filter, level, string, tokens={}, showPrefix=True):
    Message(addon, filter).echo(level, string, tokens, showPrefix)

def saytext2(addon, filter, index, string, tokens={}, showPrefix=True):
    if filter == 0:
        echo(addon, 0, 0, string, tokens, showPrefix)
    else:
        Message(addon, filter).saytext2(index, string, tokens, showPrefix)

def hudhint(addon, filter, string, tokens={}):
    Message(addon, filter).hudhint(string, tokens)
    
def centermsg(addon, filter, string, tokens={}):
    Message(addon, filter).centermsg(string, tokens)

# ==============================================================================
#   LEVEL UP AND LEVEL DOWN TRIGGERING
# ==============================================================================
def triggerLevelUpEvent(levelUpUserid, levelUpSteamid, levelUpName, levelUpTeam, levelUpOldLevel, levelUpNewLevel, victimUserid=0, victimName=None, weapon=None):
    es.event('initialize', 'gg_levelup')
    es.event('setint', 'gg_levelup', 'userid', levelUpUserid)
    es.event('setstring', 'gg_levelup', 'steamid', levelUpSteamid)
    es.event('setstring', 'gg_levelup', 'name', levelUpName)
    es.event('setstring', 'gg_levelup', 'team', levelUpTeam)                                
    es.event('setint', 'gg_levelup', 'old_level', levelUpOldLevel)
    es.event('setint', 'gg_levelup', 'new_level', levelUpNewLevel)
    es.event('setint', 'gg_levelup', 'victim', victimUserid)
    es.event('setstring', 'gg_levelup', 'victimname', victimName)
    es.event('setstring', 'gg_levelup', 'weapon', weapon)
    es.event('fire', 'gg_levelup')
    
def triggerLevelDownEvent(levelDownUserid, levelDownSteamid, levelDownName, levelDownTeam, levelDownOldLevel, levelDownNewLevel, attackerUserid=0, attackerName=None):
    es.event('initialize', 'gg_leveldown')
    es.event('setint', 'gg_leveldown', 'userid', levelDownUserid)
    es.event('setstring', 'gg_leveldown', 'steamid', levelDownSteamid)
    es.event('setstring', 'gg_leveldown', 'name', levelDownName)
    es.event('setint', 'gg_leveldown', 'team', levelDownTeam)
    es.event('setint', 'gg_leveldown', 'old_level', levelDownOldLevel)
    es.event('setint', 'gg_leveldown', 'new_level', levelDownNewLevel)
    es.event('setint', 'gg_leveldown', 'attacker', attackerUserid)
    es.event('setstring', 'gg_leveldown', 'attackername', attackerName)
    es.event('fire', 'gg_leveldown')
    
# ==============================================================================
#   RESET GUNGAME --- WARNING: POWERFUL COMMAND
# ==============================================================================
def resetGunGame():
    # Reset the Leader Information Database in the dict_leaderInfo
    dict_leaderInfo.clear()
    dict_leaderInfo['currentLeaders'] = []
    dict_leaderInfo['oldLeaders'] = []
    dict_leaderInfo['leaderLevel'] = 1
    
    # Game is no longer over
    setGlobal('gameOver', 0)
    
    # Reset the player information dictionary
    dict_players.clear()
    
    # Add all players to the players dictionary
    for userid in es.getUseridList():
        gungamePlayer = getPlayer(userid)

def clearGunGame():
    # Clear the dict_leaderInfo
    dict_leaderInfo.clear()
    
    # Clear the dict_players
    dict_players.clear()
    
    # Clear the dict_weaponOrders
    dict_weaponOrders.clear()
    
    # Clear the dict_weaponOrderSettings
    dict_weaponOrderSettings.clear()
    dict_weaponOrderSettings['currentWeaponOrderFile'] = None
    
    # Reset the Leader Information Database in the dict_leaderInfo
    dict_leaderInfo.clear()
    dict_leaderInfo['currentLeaders'] = []
    dict_leaderInfo['oldLeaders'] = []
    dict_leaderInfo['leaderLevel'] = 1
    
    # Reset the Player Information dictionary
    dict_players.clear()
    
    # Reset the stored variables
    dict_variables.clear()
    
    # Clear the gungame globals
    dict_globals.clear()
    
def clearOldPlayers():
    # Loop through the players
    for userid in dict_players.copy():
        # Remove from dict_players if they aren't in the server
        if not clientInServer(userid): del dict_players[userid]

# ==============================================================================
#   WEAPON RELATED COMMANDS
# ==============================================================================
def getCurrentWeaponOrderFile():
    return dict_weaponOrderSettings['currentWeaponOrderFile']
    
def getWeaponOrderString():
    weaponOrderString = None
    currentWeaponOrder = dict_weaponOrderSettings['currentWeaponOrderFile']
    for level in dict_weaponOrders[currentWeaponOrder]:
        if not weaponOrderString:
            weaponOrderString = dict_weaponOrders[currentWeaponOrder][level][0]
        else:
            weaponOrderString = '%s,%s' %(weaponOrderString, dict_weaponOrders[currentWeaponOrder][level][0])
    return weaponOrderString
    
def getWeaponOrderList():
    currentWeaponOrder = dict_weaponOrderSettings['currentWeaponOrderFile']
    list_weaponOrder = [dict_weaponOrders[currentWeaponOrder][level][0] for level in dict_weaponOrders[currentWeaponOrder]]
    return list_weaponOrder
    
def getLevelWeapon(levelNumber):
    levelNumber = int(levelNumber)
    if dict_weaponOrders[dict_weaponOrderSettings['currentWeaponOrderFile']].has_key(levelNumber):
        return str(dict_weaponOrders[dict_weaponOrderSettings['currentWeaponOrderFile']][levelNumber][0])
    else:
        raise ValueError('Cannot get weapon information (%s): doesn\'t exist' % levelNumber)

def sendWeaponOrderMenu(userid):
    popuplib.send('gungameWeaponOrderMenu_page1', userid)

def weaponOrderMenuHandler(userid, choice, popupname):
    pass

# ==============================================================================
#   LEVEL RELATED COMMANDS
# ==============================================================================
def getTotalLevels():
    list_weaponOrderKeys = dict_weaponOrders[dict_weaponOrderSettings['currentWeaponOrderFile']].keys()
    return int(len(list_weaponOrderKeys))
    
def setPreventLevelAll(value):
    for userid in es.getUseridList():
        gungamePlayer = getPlayer(userid)
        gungamePlayer['preventlevel'] = int(value)

def getAverageLevel():
    averageLevel = 0
    averageDivider = 0
    
    for userid in es.getUseridList():
        if dict_players.has_key(userid):
            averageDivider += 1
            averageLevel += int(dict_players[userid]['level'])
    
    return int(round(averageLevel / averageDivider)) if averageDivider else 0

def getLevelUseridList(levelNumber):
    levelNumber = int(levelNumber)
    list_levelUserids = []
    
    for userid in dict_players:
        if dict_players[int(userid)]['level'] == levelNumber:
            list_levelUserids.append(userid)
    
    return list_levelUserids
    
def getLevelUseridString(levelNumber):
    levelNumber = int(levelNumber)
    levelUseridString = None
    
    for userid in dict_players:
        if dict_players[int(userid)]['level'] == levelNumber:
            if not levelUseridString:
                levelUseridString = userid
            else:
                levelUseridString = '%s,%s' %(levelUseridString, userid)
    
    return levelUseridString
    
def getLevelWeapon(levelNumber):
    levelNumber = int(levelNumber)
    
    if not levelExists(levelNumber):
        raise ValueError('Unable to retrieve weapon information: level \'%d\' does not exist' % levelNumber)
    
    return getLevelInfo(levelNumber)[0]

def sendWeaponOrderMenu(userid):
    popuplib.send('gungameWeaponOrderMenu_page1', userid)

def weaponOrderMenuHandler(userid, choice, popupname):
    pass

# ==============================================================================
#   LEVEL RELATED COMMANDS
# ==============================================================================
def getTotalLevels():
    list_weaponOrderKeys = dict_weaponOrders[dict_weaponOrderSettings['currentWeaponOrderFile']].keys()
    return len(list_weaponOrderKeys)
    
def setPreventLevelAll(value):
    value = clamp(value, 0, 1)
    
    for player in dict_players:
        player['preventlevel'] = value

def getAverageLevel():
    averageLevel = 0
    averageDivider = 0
    
    for userid in es.getUseridList():
        if dict_players.has_key(userid):
            averageDivider += 1
            averageLevel += int(dict_players[userid]['level'])
    
    if averageDivider:
        return int(round(averageLevel / averageDivider))
    else:
        return 0

def getLevelUseridList(levelNumber):
    levelNumber = int(levelNumber)
    list_levelUserids = []
    
    for userid in dict_players:
        if dict_players[int(userid)]['level'] == levelNumber:
            list_levelUserids.append(userid)
    
    return list_levelUserids
    
def getLevelUseridString(levelNumber):
    levelNumber = int(levelNumber)
    levelUseridString = None
    
    for userid in dict_players:
        if dict_players[int(userid)]['level'] == levelNumber:
            if not levelUseridString:
                levelUseridString = userid
            else:
                levelUseridString = '%s,%s' %(levelUseridString, userid)
    
    return levelUseridString

def levelExists(levelNumber):
    return dict_weaponOrders[dict_weaponOrderSettings['currentWeaponOrderFile']].has_key(levelNumber)

def getLevelInfo(levelNumber):
    # Does the level exist?
    if not levelExists(levelNumber):
        raise ValueError('Cannot get level info (%s): level does not exist!' % levelNumber)
    
    return dict_weaponOrders[dict_weaponOrderSettings['currentWeaponOrderFile']][levelNumber]

def getLevelMultiKill(levelNumber):
    if levelExists(levelNumber):
        return getLevelInfo(levelNumber)[1]
    
def createScoreList(keyGroupName=None):
    dict_gungameScores = {}
    
    for userid in dict_players:
        dict_gungameScores[userid] = dict_players[userid]['level']
    
    return sorted(dict_gungameScores.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    
# ==============================================================================
#   LEADER RELATED COMMANDS
# ==============================================================================
def getCurrentLeaderList():
    # Var prep
    leaders = []
    
    # Loop through the current leaders
    for userid in dict_leaderInfo['currentLeaders']:
        # Append to the leaders list if the player is in the server
        if clientInServer(userid): leaders.append(userid)
    
    # No leaders in the server?
    if len(leaders) == 0:
        # Get a list of players with the next highest level
        return getNewLeaderList()
    else:
        # Set current leader info
        dict_leaderInfo['oldLeaders'] = dict_leaderInfo['currentLeaders']
        dict_leaderInfo['currentLeaders'] = leaders
        
        # Return list of leaders as usual
        return leaders

def getOldLeaderList():
    return dict_leaderInfo['oldLeaders']

def getNewLeaderList():
    # Var prep
    highestLevel = 1
    players = []
    
    # Loop through the players
    for userid in dict_players:
        player = dict_players[userid]
        level = dict_players[userid]['level']
        
        # Is the player on the server?
        if not clientInServer(userid):
            continue
        
        # Is the players level higher than the highest level?
        if level > highestLevel:
            # Set list to them
            players = [userid]
            highestLevel = level
        elif level == highestLevel:
            # Append them to the current list
            players.append(userid)
    
    # Set current leaders
    dict_leaderInfo['oldLeaders'] = dict_leaderInfo['currentLeaders']
    dict_leaderInfo['currentLeaders'] = players
    dict_leaderInfo['leaderLevel'] = highestLevel
    
    # Return players
    return players

def removeLeader(userid):
    userid = int(userid)
    
    if userid in dict_leaderInfo['currentLeaders']:
        dict_leaderInfo['currentLeaders'].remove(userid)
        
        if len(dict_leaderInfo['currentLeaders']) == 0:
            leaderLevel = 1
            
            for userid in dict_players:
                if int(dict_players[userid]['level']) > leaderLevel:
                    dict_leaderInfo['currentLeaders'] = [userid]
                    leaderLevel = int(dict_players[userid]['level'])
                elif dict_players[userid]['level'] == leaderLevel:
                    dict_leaderInfo['currentLeaders'].append(userid)

def getCurrentLeaderString():
    currentLeaderString = None
    
    for userid in dict_leaderInfo['currentLeaders']:
        if not currentLeaderString:
            currentLeaderString = userid
        else:
            currentLeaderString = '%s,%s' % (currentLeaderString, userid)
    
    return currentLeaderString
    
def getOldLeaderString():
    oldLeaderString = None
    
    for userid in dict_leaderInfo['oldLeaders']:
        if not oldLeaderString:
            oldLeaderString = userid
        else:
            oldLeaderString = '%s,%s' %(oldLeaderString, userid)
    
    return oldLeaderString
    
def getLeaderLevel():
    return dict_leaderInfo['leaderLevel']
    
def getCurrentLeaderCount():
    return len(dict_leaderInfo['currentLeaders'])
    
def getOldLeaderCount():
    return len(dict_leaderInfo['oldLeaders'])
    
# ==============================================================================
#   CONFIG RELATED COMMANDS
# ==============================================================================
def variableExists(variableName):
    return dict_variables.has_key(variableName.lower())

def getVariable(variableName):
    variableName = variableName.lower()
    
    if not dict_variables.has_key(variableName):
        raise ValueError('Unable to get variable object (%s): not registered.' % variableName)
    
    return dict_variables[variableName]

def getVariableValue(variableName):
    variableName = variableName.lower()
    
    if not dict_variables.has_key(variableName):
        raise ValueError('Unable to get variable value (%s): not registered.' % variableName)
    
    variable = dict_variables[variableName]
    
    # Is numeric?
    if isNumeric(str(variable)):
        # Return number
        return int(variable)
    else:
        # Return string
        return str(variable)

def setVariableValue(variableName, value):
    variableName = variableName.lower()
    
    if not dict_variables.has_key(variableName):
        raise ValueError('Unable to set variable value (%s): not registered.' % variableName)
    
    # Set variable value
    dict_variables[variableName].set(value)
    
    # Fire server_cvar
    es.server.cmd('%s %s' % (variableName, value))

def getVariableList():
    return dict_variables.keys()
    
# ==============================================================================
#   SOUND RELATED COMMANDS
# ==============================================================================
def addDownloadableSounds():
    # Make sure we are in a map
    if not inMap():
        return
    
    # Loop through all the sounds
    for soundName in dict_sounds:
        if dict_sounds[soundName] != 0:
            es.stringtable('downloadables', 'sound/%s' % dict_sounds[soundName])

def getSound(soundName):
    if dict_sounds.has_key(soundName):
        return dict_sounds[soundName]
    else:
        raise SoundError('Cannot get sound (%s): sound file not found.' % soundName)

# ==============================================================================
#   WINNER RELATED COMMANDS
# ==============================================================================
def getWins(uniqueid):
    global dict_winners
    uniqueid = str(uniqueid)
    if dict_winners.has_key(uniqueid):
        return dict_winners[uniqueid]['wins']
    else:
        return 0

def addWin(uniqueid):
    gungameWinner = getWinner(uniqueid)
    gungameWinner['wins'] += 1
    
def updateTimeStamp(uniqueid):
    gungameWinner = getWinner(uniqueid)
    gungameWinner['timestamp'] = time.time()
    
def saveWinnerDatabase():
    global dict_winners
    
    # Set the winners database path to a variable
    winnersDataBasePath = es.getAddonPath('gungame') + '/data/winnersdata.db'
    
    # Dump to the file
    winnersDataBaseFile = open(winnersDataBasePath, 'w')
    cPickle.dump(dict_winners, winnersDataBaseFile)
    winnersDataBaseFile.close()
    
def loadWinnersDataBase():
    global dict_winners
    
    # Set a variable for the path of the winner's database
    winnersDataBasePath = es.getAddonPath('gungame') + '/data/winnersdata.db'
    
    # See if the file exists
    if not os.path.isfile(winnersDataBasePath):
        # Open the file
        winnersDataBaseFile = open(winnersDataBasePath, 'w')
        
        # Place the contents of dict_winners in
        cPickle.dump(dict_winners, winnersDataBaseFile)
        
        # Save changes
        winnersDataBaseFile.close()
    
    # Read the file
    winnersDataBaseFile = open(winnersDataBasePath, 'r')
    dict_winners = cPickle.load(winnersDataBaseFile)
    winnersDataBaseFile.close()
    
    # Set the global for having the database loaded
    setGlobal('winnersloaded', 1)
    
def cleanWinnersDataBase(days):
    global dict_winners
    
    daysInSeconds = float(days) * float(86400)
    currentTime = float(time.time())
    
    for steamid in dict_winners.copy():
        # Prune the player?
        if (currentTime - float(dict_winners[steamid]['timestamp'])) > daysInSeconds:
            del dict_winners[steamid]

# ==============================================================================
#   ADDON RELATED COMMANDS
# ==============================================================================
def registerAddon(addonName):
    if not dict_addons.has_key(addonName):
        dict_addons[addonName] = Addon(addonName)
        return dict_addons[addonName]
    else:
        raise AddonError('Cannot register addon (%s): already registered.' % addonName)

def getAddon(addonName):
    if dict_addons.has_key(addonName):
        return dict_addons[addonName]
    else:
        raise AddonError('Cannot get addon object (%s): not registered.' % addonName)

def unregisterAddon(addonName):
    if dict_addons.has_key(addonName):
        # Unregister commands
        dict_addons[addonName].unregisterCommands()
        
        del dict_addons[addonName]
    else:
        raise AddonError('Cannot unregister addon (%s): not registered.' % addonName)

def getAddonDisplayName(addonName):
    if addonName == 'gungame':
        return 'GunGame'
    elif dict_addons.has_key(addonName):
        return dict_addons[addonName].getDisplayName()
    else:
        raise AddonError('Cannot get display name (%s): not registered.' % addonName)

def addonRegistered(addonName):
    return dict_addons.has_key(addonName)

def getRegisteredAddonlist():
    return dict_addons.keys()

def getDependencyList():
    return dict_dependencies.keys()

def getDependencyValue(dependencyName):
    return dict_dependencies[dependencyName].dependencyValue

# ==============================================================================
#   GLOBALS RELATED COMMANDS
# ==============================================================================
def setGlobal(variableName, variableValue):
    '''Set a global variable (name case insensitive)'''
    variableName = variableName.lower()
    
    if isNumeric(variableValue):
        variableValue = int(variableValue)
    
    dict_globals[variableName] = variableValue

def getGlobal(variableName):
    '''Returns a global variable (name case insensitive)'''
    variableName = variableName.lower()
    
    if dict_globals.has_key(variableName):
        return dict_globals[variableName]
    else:
        return 0

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def isNumeric(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def getGameDir(dir):
    # Get game dir
    gamePath = str(es.ServerVar('eventscripts_gamedir'))
    
    # For linux...
    dir = dir.replace('\\', '/')
    
    # Return
    return '%s/%s' % (gamePath, dir)

def getAddonDir(addonName, dir):
    # Check addon exists
    if not addonExists(addonName):
        raise ValueError('Cannot get addon directory (%s): doesn\'t exist.' % addonName)
    
    # Get game dir
    addonPath = es.getAddonDir('gungame')
    
    # For linux...
    dir = dir.replace('\\', '/')
    
    # Return
    return '%s/%s/%s' % (addonPath, 'custom_addons' if getAddonType(addonName) else 'included_addons', dir)

def clientInServer(userid):
    return (not es.getplayername(userid) == 0) or es.exists('userid', userid)

def inMap():
    return (str(es.ServerVar('eventscripts_currentmap')) != '')

def getMapName():
    return str(es.ServerVar('eventscripts_currentmap'))

def isSpectator(userid):
    if not clientInServer(userid):
        return 0
    
    return (es.getplayerteam(userid) <= 1)

def hasEST():
    return str(es.ServerVar('est_version')) != '0'
    
def getESTVersion():
    if hasEST():
        return float(es.ServerVar('est_version'))
    else:
        return 0.000

def isDead(userid):
    return bool(int(es.getplayerprop(userid, 'CCSPlayer.baseclass.pl.deadflag')))
    
def getPlayerUniqueID(userid):
    userid = int(userid)
    return dict_uniqueIds[userid]
    
def playerExists(userid):
    userid = int(userid)
    return dict_players.has_key(userid)

def getAddonType(addonName):
    # Check addon exists
    if not addonExists(addonName):
        raise ValueError('Cannot get addon type (%s): doesn\'t exist.' % addonName)
    
    # Get addon type
    if os.path.isdir(getGameDir('addons/eventscripts/gungame/included_addons/%s' % addonName)):
        return 0
    else:
        return 1

def addonExists(addonName):
    return (os.path.isdir(getGameDir('addons/eventscripts/gungame/included_addons/%s' % addonName)) or os.path.isdir(getGameDir('addons/eventscripts/gungame/custom_addons/%s' % addonName)))

def formatArgs():
    return [es.getargv(x) for x in range(1, es.getargc())]

def removeReturnChars(playerName):
    playerName = playerName.strip('\n')
    playerName = playerName.strip('\r')
    
    return playerName

def clamp(value, low=False, high=False):
    if not isNumeric(value):
        raise TypeError('Cannot clamp (%s): value not numerical.' % value)
    
    # Make an integer
    value = int(value)
    
    # Clamp if too low
    if low != False:
        if value < low: value = low
    
    # Clamp if too high
    if high != False:
        if value > high: value = high
    
    # Return value
    return value