''' (c) 2008 by the GunGame Coding Team

    Title: gungamelib
    Version: 1.0.135
    Description:
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python Imports
import string
import random
import os
import ConfigParser

# EventScripts Imports
import es
import playerlib
import gamethread
import popuplib
import langlib
import usermsg

# ==============================================================================
#   GLOBAL DICTIONARIES
# ==============================================================================
dict_gungameCore = {}
dict_gungameWeaponOrders = {}
dict_weaponOrderSettings = {}
dict_weaponOrderSettings['currentWeaponOrderFile'] = None

dict_leaderInfo = {}
dict_leaderInfo['currentLeaders'] = []
dict_leaderInfo['oldLeaders'] = []
dict_leaderInfo['leaderLevel'] = 1

dict_cfgSettings = {}
dict_globals = {}

dict_gungameSounds = {}

dict_RegisteredAddons = {}
dict_registeredDependencies = {}

# ==============================================================================
#   GLOBAL LISTS
# ==============================================================================
list_validWeapons = ['glock','usp','p228','deagle','fiveseven',
                    'elite','m3','xm1014','tmp','mac10','mp5navy',
                    'ump45','p90','galil','famas','ak47','scout',
                    'm4a1','sg550','g3sg1','awp','sg552','aug',
                    'm249','hegrenade','knife']

# If any configs in this list are missing when they call the config, GunGame will unload                    
list_criticalConfigs = ['gg_en_config.cfg', 'gg_default_addons.cfg']

# ==============================================================================
#   GLOBAL VARIABLES
# ==============================================================================
weaponOrderINI = ConfigParser.ConfigParser()
gameDir = str(es.ServerVar('eventscripts_gamedir'))

# ==============================================================================
#   ERROR CLASSES
# ==============================================================================
class _GunGameLibError:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class UseridError(_GunGameLibError):
    pass
    
class PlayerError(_GunGameLibError):
    pass
    
class GunGameValueError(_GunGameLibError):
    pass
    
class TeamError(_GunGameLibError):
    pass
    
class DeadError(_GunGameLibError):
    pass
    
class FileError(_GunGameLibError):
    pass
    
class ArgumentError(_GunGameLibError):
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
    '''Class used in altering the GunGame Core Dictionary'''
    
    # Here, we define the __init__ method. This will execute every time the gungamelib.getPlayer() is called
    def __init__(self, playerID):
        try:
            # Here, we set self.userid to the userid they gave us
            self.userid = int(playerID)
            # Now, we check to see if the userid exists on the server
            if not es.exists('userid', self.userid):
                # When we "validate" the player, we are actually checking to see if they exist in the GunGame Core Dictionary
                if self.__validatePlayer():
                    # When players are kicked, or disconnect, the check for their userid will fail...however, they are still in the GunGame Core Dictionary
                    if dict_gungameCore.has_key(self.userid):
                        self.attributes = dict_gungameCore[self.userid]
                else:
                    # If we reach this code, someone has given us an invalid userid
                    raise UseridError,  '\'%s\' is an invalid userid: no matching userid found active on the server' %self.userid
            else:
                # We will now make sure that the player exists in the GunGame database
                # When we "validate" the player, we are actually checking to see if they exist in the GunGame Core Dictionary
                if not self.__validatePlayer():
                    # Since they do not yet exist, but they have a valid userid, we will create them in the dict_gungameCore to avoid errors
                    self.__createPlayer()
                else:
                    # We don't want to keep resetting the player's attributes to the default values, so we will pull them from the GunGame Core Dictionary
                    self.attributes = dict_gungameCore[self.userid]
        except TypeError, e:
            # If we reach this code, this means that they did not provide us a userid
            raise TypeError, 'gungamelib.getPlayer() expected a userid: no userid provided'
            
    def __getitem__(self, item):
        # We will be nice and convert the "item" to a lower-cased string
        item = str(item).lower()
        
        # Let's make sure that the item that they are trying to change exists
        if item in self.attributes:
            # Allowing the retrieving of attributes in the dictionary
            return self.attributes[item]
        else:
            raise PlayerError, 'Unable to retrieve the \'%s\' value: player attribute does not exist' %item
        
    def __setitem__(self, item, value):
        # We will be nice and convert the "item" to a lower-cased string
        item = str(item).lower()
        value == int(value)
        # Let's make sure that the item that they are trying to change exists
        if item in self.attributes:
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
                                self.attributes[item] = int(value)
                                
                                for userid in dict_gungameCore:
                                    if int(dict_gungameCore[userid]['level']) > leaderLevel:
                                        dict_leaderInfo['currentLeaders'] = [userid]
                                        leaderLevel = int(dict_gungameCore[userid]['level'])
                                        
                                    elif dict_gungameCore[userid]['level'] == leaderLevel:
                                        dict_leaderInfo['currentLeaders'].append(userid)
                                        
                                # Set the leader level to the new level
                                dict_leaderInfo['leaderLevel'] = leaderLevel
                                
                                # FIRE LEADER LOST LEVEL EVENT HERE event gg_leader_lostlevel
                                es.event('initialize', 'gg_leader_lostlevel')
                                es.event('setint', 'gg_leader_lostlevel', 'userid', self.userid)
                                es.event('fire', 'gg_leader_lostlevel')
                                
                    self.attributes[item] = int(value)
                else:
                    raise GunGameValueError, 'Level value must be greater than 0 or less than %d: given \'%i\'' %((getTotalLevels() + 1), value)
            # AFK ROUNDS
            elif item == 'afkrounds':
                if value > -1:
                    self.attributes[item] = int(value)
                else:
                    raise GunGameValueError, 'AFK Rounds value must be 0 or greater: given \'%i\'' %value
            # MULTIKILL
            elif item == 'multikill':
                if value > -1:
                    self.attributes[item] = int(value)
                else:
                    raise GunGameValueError, 'MultiKill value must be 0 or greater: given \'%i\'' %value
            # TRIPLE
            elif item == 'triple':
                if value > -1 and value < 4:
                    self.attributes[item] = value
                else:
                    raise GunGameValueError, 'Triple Level value must be between 0 and 3: given \'%i\'' %value
            # PREVENT LEVEL
            elif item == 'preventlevel':
                if value == 0 or value == 1:
                    self.attributes[item] = int(value)
                else:
                    raise GunGameValueError, 'PreventLevel must be either 0 or 1: given \'%i\'' %value
            else:
                # Allow the setting of attributes in the dictionary
                self.attributes[item] = int(value)
        else:
            raise PlayerError, 'Unable to set the \'%s\' value: player attribute does not exist' %item
        
    def __int__(self):
        # If the instance is used as an integer, return the player's userid
        return self.userid
        
    def __validatePlayer(self):
        # Here, we "validate" the player by making sure that they are in the dict_gungameCore
        if dict_gungameCore.has_key(self.userid):
            # We will return "True" if the player exists in the GunGame Core Dictionary
            return True
        else:
            # We will return "False" if the player does not exist in the GunGame Core Dictionary
            return False
            
    def __createPlayer(self):
        names = ['level', 'afkrounds', 'multikill',
                'triple', 'preventlevel', 'afkmathtotal',
                'steamid']
        values = [1, 0, 0, 0, 0, 0, playerlib.uniqueid(self.userid, 1)]
        self.attributes = dict(zip(names, values))

        # We now create the player in the GunGame Core Dictionary
        # NOTE: Any time the player's attributes change, so will the GunGame Core Dictionary
        dict_gungameCore[self.userid] = self.attributes
        
    def removePlayer(self):
        # Let's make sure that the player exists in the GunGame database before trying to remove them
        # When we "validate" the player, we are actually checking to see if they exist in the GunGame Core Dictionary
        if self.__validatePlayer():
            # Now that we have verified the player exists in the GunGame Core Dictionary, we need to make sure that they are no longer on the server
            # When we "validate" the player's connection, we are actually checking to see if their userid still exists on the server
            if not self.__validatePlayerConnection():
                # If the player is no longer on the server, we will allow their removal from the GunGame Core Dictionary
                del dict_gungameCore[self.userid]
            else:
                # If we reach this code, someone has tried deleting the player from the GunGame Core Dictionary while the player is still active on the server
                raise PlayerError,  'Unable to remove the userid \'%s\' from the GunGame Core Dictionary: player is still active on the server' %self.userid
            
    def __validatePlayerConnection(self):
        # Here, we see if the userid still exists on the server
        if es.exists('userid', self.userid):
            # If the userid still exists on the server, we return "True"
            return True
        else:
            # If the userid does not exist on the server, we return "False"
            return False
            
    def resetPlayer(self):
        # We are only creating a new method so that we can allow outside coders to reset the player in the GunGame Core Dictionary
        # No checks are necessary to see if the player exists, due to several checks above
        # This is the same code used in the method __createPlayer()
        self.__createPlayer()
        
    def resetPlayerLocation(self):
        # Make sure the player is on a team
        if int(es.getplayerteam(self.userid)) > 1:
            # Get the player's location, although this is not really a list...it returns a tuple
            list_playerlocation = es.getplayerlocation(self.userid)
            # Add necessary information about the player's location, excluding the "z" axis, as this is far too touchy
            afkMathTotal = int(sum(list_playerlocation)) - list_playerlocation[2] + int(es.getplayerprop(self.userid, 'CCSPlayer.m_angEyeAngles[0]')) + int(es.getplayerprop(self.userid, 'CCSPlayer.m_angEyeAngles[1]'))
            # Update the player's "afkmathtotal" attribute
            self.attributes['afkmathtotal'] = int(afkMathTotal)
        else:
            raise TeamError, 'AFK Message: Unable to reset the player\'s location: userid \'%s\' is not a team' %self.userid
            
    def playerNotAFK(self):
        # Make sure the player is on a team
        if int(es.getplayerteam(self.userid)) > 1:
            # Set the player's "afkmathtotal" attribute to 0
            # This is called when we definately know the player is not AFK
            self.attributes['afkmathtotal'] = 0
        else:
            raise TeamError, 'AFK Message: Unable to set the player to active status: userid \'%s\' is not a team' %self.userid
            
    def isPlayerAFK(self):
        # Make sure the player is on a team
        if int(es.getplayerteam(self.userid)) > 1:
            list_playerlocation = es.getplayerlocation(self.userid)
            afk_math_total = int(sum(list_playerlocation)) - list_playerlocation[2] + int(es.getplayerprop(self.userid,'CCSPlayer.m_angEyeAngles[0]')) + int(es.getplayerprop(self.userid,'CCSPlayer.m_angEyeAngles[1]'))
            if int(afk_math_total) == self.attributes['afkmathtotal']:
                return True
            else:
                return False
        else:
            raise TeamError, 'AFK Message: Unable to check player\'s AFK status: userid \'%s\' is not a team' %self.userid
            
    def teleportPlayer(self, x, y, z, eyeangle0=None, eyeangle1=None):
        # Make sure the player is on a team
        if int(es.getplayerteam(self.userid)) > 1:
            if not es.getplayerprop(self.userid, 'CCSPlayer.baseclass.pl.deadflag'):
                es.server.cmd('es_setpos %d %s %s %s' %(self.userid, x, y, z))
                if eyeangle0 or eyeangle1:
                    es.server.cmd('es_setang %d %s %s' %(self.userid, eyeangle0, eyeangle1))
                gamethread.delayed(0.6, self.resetPlayerLocation, ())
            else:
                raise DeadError, 'Unable to teleport player: userid \'%s\' is not alive' % self.userid
        else:
            raise TeamError, 'Unable to teleport player: userid \'%s\' is not a team' % self.userid
        
    def setPlayerEyeAngles(self, eyeAngle0, eyeAngle1):
        # Make sure the player is on a team
        if int(es.getplayerteam(self.userid)) > 1:
            if not es.getplayerprop(self.userid, 'CCSPlayer.baseclass.pl.deadflag'):
                es.server.cmd('es_setang %d %s %s' %(self.userid, eyeangle0, eyeangle1))
                gamethread.delayed(0.6, self.resetPlayerLocation, ())
            else:
                raise DeadError, 'Unable to set player\'s eyeangles: userid \'%s\' is not alive' %self.userid
        else:
            raise TeamError, 'Unable to set player\'s eyeangles: userid \'%s\' is not a team' %self.userid
            
    def stripPlayer(self):
        # Make sure the player is on a team
        if int(es.getplayerteam(self.userid)) > 1:
            if not es.getplayerprop(self.userid, 'CCSPlayer.baseclass.pl.deadflag'):
                playerlibPlayer = playerlib.getPlayer(self.userid)
                playerlibPrimary = playerlibPlayer.get('primary')
                playerlibSecondary = playerlibPlayer.get('secondary')
                if playerlibPrimary:
                    es.server.cmd('es_xremove %d' %int(playerlibPlayer.get('weaponindex', playerlibPrimary)))
                if playerlibSecondary:
                    es.server.cmd('es_xremove %d' %int(playerlibPlayer.get('weaponindex', playerlibSecondary)))
            else:
                raise DeadError, 'Unable to strip player: userid \'%s\' is not alive' %self.userid
        else:
            raise TeamError, 'Unable to strip player: userid \'%s\' is not a team' %self.userid
            
    def giveWeapon(self):
        if int(es.getplayerteam(self.userid)) > 1:
            if not es.getplayerprop(self.userid, 'CCSPlayer.baseclass.pl.deadflag'):
                playerWeapon = self.getWeapon()
                if playerWeapon != 'knife':
                    es.server.cmd('es_xdelayed 0.001 es_xgive %s weapon_%s' %(self.userid, playerWeapon))
                if playerWeapon == 'hegrenade' and 'BOT' in self.attributes['steamid']:
                    es.server.cmd('es_xdelayed 0.001 es_xsexec %s \"use weapon_%s\"' %(self.userid, playerWeapon))
        else:
            raise TeamError, 'Unable to give the player a weapon: userid \'%s\' is not a team' %self.userid
    
    def getWeapon(self):
        if dict_weaponOrderSettings['currentWeaponOrderFile'] != None:
            return dict_gungameWeaponOrders[dict_weaponOrderSettings['currentWeaponOrderFile']][self.attributes['level']][0]
    
    def getWins(self):
        # GET WINS
        # gungamePlayer.get('Wins')
        if dict_gungameWinners.has_key(self.attributes['steamid']):
            return dict_gungameWinners[steamid].int_wins
        else:
            return 0
            

# ==============================================================================
#   WEAPON ORDER CLASS
# ==============================================================================
class WeaponOrder:
    '''Class used in altering GunGame Weapon Order.'''
    
    def __init__(self, fileName):
        filePath = getGameDir('/cfg/gungame/weapon_order_files/%s' % fileName)
        self.fileName = fileName
        
        # Check to see if it has been registered before
        if not self.__isRegistered(fileName):
            self.__parse(fileName, filePath)
        else:
            echo('gungame', 0, 0, 'WeaponOrder:AlreadyRegistered', {'file': fileName})
    
    def __parse(self, fileName, filePath):
        try:
            # Create a dictionary to temporarily hold the weapon order
            dict_tempWeaponOrder = {}
            # Open the weapon order file for parsing
            weaponOrderFile = open(filePath, "r")
            # Set the level counter to 0
            levelCounter = 0
            # Loop through each line in the weapon order file
            for line in weaponOrderFile:
                # Remove spaces from the ends of the lines and convert characters to lower case
                line = line.strip().lower()
                
                # Make sure that the line contains some sort of text, and that the line does not begin with "//"
                if line and (not line.startswith('//')):
                    # Remove double spacing
                    while '  ' in line:
                        line = line.replace('  ', ' ')
                        
                    # We use the split() method on the line to separate weapon names from multikill values
                    list_splitLine = line.split(" ")
                    
                    # Just in case someone got space happy, we will loop through the list and remove any entries == ''
                    # Set the weapon name to the first index (0) in the split list
                    weaponName = str(list_splitLine[0])
                    if weaponName in list_validWeapons:
                        if len(list_splitLine) > 1:
                            if isNumeric(list_splitLine[1]):
                                multiKillValue = int(list_splitLine[1])
                                
                                # Make sure that the level counter comes AFTER the potential exception above
                                levelCounter += 1
                                list_splitLine[1] = int(list_splitLine[1])
                                
                                dict_tempWeaponOrder[levelCounter] = list_splitLine
                            else:
                                echo('gungame', 0, 0, 'WeaponOrder:MultikillNotNumeric', {'weapon': weaponName, 'to': list_splitLine[1]})
                                #es.dbgmsg(0, 'Unable to set multkill value for \'%s\': \'%s\' is not a numeric value...skipping' %(weaponName, list_splitLine[1]))
                        else:
                            levelCounter += 1
                            list_splitLine.append(1)
                            dict_tempWeaponOrder[levelCounter] = list_splitLine
                    else:
                        echo('gungame', 0, 0, 'WeaponOrder:InvalidWeapon', {'weapon': weaponName})
            
            # Close the weapon order file, since we are done parsing it
            weaponOrderFile.close()
            dict_tempWeaponOrderSettings = {}
            
            # Open the INI to find out the "Display Name" for this weapon order
            weaponOrderINI.read('%s/cfg/gungame/gg_weapon_orders.ini' %gameDir)
            
            # Loop through each section (the section name is the "Display Name") in the INI
            for weaponOrderDisplayName in weaponOrderINI.sections():
                # See if the "fileName" in the INI matches the current "file" we are working with
                if weaponOrderINI.get(weaponOrderDisplayName, 'fileName') == fileName:
                    # If the file name matches, we add the section name as the "displayName" in the weapon order settings dictionary
                    dict_tempWeaponOrderSettings['displayName'] = weaponOrderDisplayName
                    
            # Set the "weaponOrder" value to "#default" in the weapon order settings since this is the loaded default
            dict_tempWeaponOrderSettings['weaponOrder'] = '#default'
            
            # Save the temporary dictionarys to the persistent dictionarys
            dict_weaponOrderSettings[fileName] = dict_tempWeaponOrderSettings
            dict_gungameWeaponOrders[fileName] = dict_tempWeaponOrder
        except IOError:
            raise FileError, ('Unable to load weapon order file: \'%s\' does not exist' %fileName)
        
    def __isRegistered(self, fileName):
        if dict_gungameWeaponOrders.has_key(fileName):
            return True
        else:
            return False
        
    def echo(self):
        weaponOrder = dict_gungameWeaponOrders[self.fileName]
        
        es.dbgmsg(0, ' ')
        es.dbgmsg(0, 'Weapon Order File Name:    %s' %self.fileName)
        es.dbgmsg(0, 'Weapon Order Display Name: %s' %dict_weaponOrderSettings[self.fileName]['displayName'])
        es.dbgmsg(0, 'Weapon Order Type:         %s' %self.getWeaponOrderType())
        es.dbgmsg(0, ' ')
        es.dbgmsg(0, '+-------+-----------+----------------')
        es.dbgmsg(0, '| Level | MultiKill | Weapon         ')
        es.dbgmsg(0, '+-------+-----------+----------------')
        
        for level in dict_gungameWeaponOrders[self.fileName]:
            weaponName = dict_gungameWeaponOrders[self.fileName][level][0]
            multiKillValue = dict_gungameWeaponOrders[self.fileName][level][1]
            
            if level < 10:
                levelInfoText = '|  0%d   |     %d     | %s' %(level, multiKillValue, weaponName)
            else:
                levelInfoText = '|  %d   |     %d     | %s' %(level, multiKillValue, weaponName)
            
            es.dbgmsg(0, levelInfoText)
            
        es.dbgmsg(0, '+-------+-----------+----------------')
        es.dbgmsg(0, ' ')
        
    def setMultiKillOverride(self, value):
        dict_tempWeaponOrder = dict_gungameWeaponOrders[self.fileName]
        for level in dict_tempWeaponOrder:
            if dict_tempWeaponOrder[level][0] != 'knife' and (not 'hegrenade'):
                dict_tempWeaponOrder[level][1] = int(value)
                
        dict_gungameWeaponOrders[self.fileName] = dict_tempWeaponOrder
        
        msg('gungame', '#all', 'WeaponOrder:MultikillValuesChanged', {'to': value})
        es.server.cmd('mp_restartgame 2')
    
    def setMultiKillDefaults(self):
        filePath = '%s/cfg/gungame/weapon_order_files/%s' %(str(gameDir), self.fileName)
        self.__parse(self.fileName, filePath)
        
        msg('gungame', '#all', 'WeaponOrder:MultikillReset')
        es.server.cmd('mp_restartgame 2')
        
    def setWeaponOrderFile(self):
        if dict_weaponOrderSettings['currentWeaponOrderFile'] == self.fileName:
            return
        
        dict_weaponOrderSettings['currentWeaponOrderFile'] = self.fileName
        self.buildWeaponOrderMenu()
        
        msg('gungame', '#all', 'WeaponOrder:FileChanged', {'to': self.fileName})
        es.server.cmd('mp_restartgame 2')
    
    def getWeaponOrderType(self):
        return dict_weaponOrderSettings[self.fileName]['weaponOrder']
        
    def __setWeaponOrder(self, value):
        dict_weaponOrderSettings[self.fileName]['weaponOrder'] = str(value)
        es.server.cmd('mp_restartgame 2')
        
    def changeWeaponOrderType(self, weaponOrder):
        weaponOrder = str(weaponOrder.lower())
        if weaponOrder == '#random':
            dict_tempWeaponOrder = dict_gungameWeaponOrders[self.fileName]
            list_gungameLevels = dict_tempWeaponOrder.keys()
            random.shuffle(list_gungameLevels)
            list_gungameWeapons = dict_tempWeaponOrder.values()
            random.shuffle(list_gungameWeapons)
            weaponArrayNumber = 0
            for level in list_gungameLevels:
                dict_tempWeaponOrder[level] = list_gungameWeapons[weaponArrayNumber]
                weaponArrayNumber += 1
            dict_gungameWeaponOrders[self.fileName] = dict_tempWeaponOrder
            self.__setWeaponOrder('#random')
            
            msg('gungame', '#all', 'WeaponOrder:ChangedTo', {'to': '#random'})
        elif self.getWeaponOrderType() != str(weaponOrder):
            if weaponOrder == '#default':
                filePath = '%s/cfg/gungame/weapon_order_files/%s' %(str(gameDir), self.fileName)
                self.__parse(self.fileName, filePath)
                
                msg('gungame', '#all', 'WeaponOrder:ChangedTo', {'to': '#default'})
            elif weaponOrder == '#reversed':
                dict_tempWeaponOrder = dict_gungameWeaponOrders[self.fileName]
                list_gungameLevels = dict_tempWeaponOrder.keys()
                list_gungameWeapons = dict_tempWeaponOrder.values()
                list_gungameWeapons.reverse()
                weaponArrayNumber = 0
                for level in list_gungameLevels:
                    dict_tempWeaponOrder[level] = list_gungameWeapons[weaponArrayNumber]
                    weaponArrayNumber += 1
                dict_gungameWeaponOrders[self.fileName] = dict_tempWeaponOrder
                self.__setWeaponOrder('#reversed')
                
                msg('gungame', '#all', 'WeaponOrder:ChangedTo', {'to': '#reversed'})
            else:
                raise GunGameValueError, 'Invalid argument for changeWeaponOrder(): \'%s\'' %weaponOrder
        else:
            raise GunGameValueError, 'Unable to change the weapon order: \'%s\' is the current weapon order' %weaponOrder
    
    def buildWeaponOrderMenu(self):
        dict_tempWeaponOrder = dict_gungameWeaponOrders[self.fileName]
        
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
    '''Class for Registration of Configs used by GunGame.'''
    def __init__(self, configName):
        self.configName = configName
        self.configPath = '%s/cfg/gungame/%s' %(str(es.ServerVar('eventscripts_gamedir')), configName)
        
        # Check to see if it has been registered before
        if not self.__isLoaded():
            self.__load()
            
    def __isLoaded(self):
        if dict_cfgSettings.has_key(self.configName):
            return True
        else:
            return False
            
    def __load(self):
        try:
            # Open the Config
            gungameConfig = open(self.configPath, 'r')
            
            # Loop through each line in the Config
            for line in gungameConfig.readlines():
                # Strip the spaces from the begninning and end of each line
                line = line.strip().lower()
                
                # Make sure that the line doesn't begin with '//'
                if not line.startswith('//'):
                    # Change the text to lowercase and convert to a string
                    if line:
                        # Remove excess whitespace
                        while '  ' in line:
                            line = line.replace('  ', ' ')
                            
                        # Add the variables and values to dict_cfgSettings
                        list_variables = line.split()
                        
                        variableName = list_variables[0]
                        
                        # If the variable has not been added to the GunGame Variables Database
                        if not dict_cfgSettings.has_key(variableName):
                            variableValue = list_variables[1]
                            
                            # Add the variable and value to the GunGame Variables Database
                            dict_cfgSettings[variableName] = variableValue
                            
                            # Check to see if we can convert the value to an int
                            if self.isNumeric(variableValue):
                                # Add the variable and value to the GunGame Config Settings Database as an integer
                                dict_cfgSettings[variableName] = int(variableValue)
                                
                            else:
                                # Add the variable and value to the GunGame Config Settings Database as a string
                                dict_cfgSettings[variableName] = variableValue
                                
                            # Create console variables
                            es.ServerVar(variableName).set(variableValue)
                            
                            # Set the notify flag so that changing the variable's value will trigger the server_cvar event
                            es.ServerVar(variableName).addFlag('notify')
                            
                            # Use a server command to fire the server_cvar event
                            es.server.cmd('%s %s' %(variableName, variableValue))
                            
                        else:
                            echo('gungame', 0, 2, 'Config:AlreadyAdded', {'name': variableName})
            
            echo('gungame', 0, 0, 'Config:Loaded', {'name': self.configPath})
        except IOError:
            if not configName.lower() in list_criticalConfigs:
                raise FileError, 'Unable to load the Config: \'%s\': File does not exist.' %configPath
            else:
                es.server.queuecmd('es_xunload gungame')
                raise FileError, 'Unable to load the Config: \'%s\': File does not exist... unloading GunGame.' %configPath
                
    def isNumeric(self, string):
        try:
            test = int(string)
        except ValueError:
            return False
        else:
            return True
            
            
# ==============================================================================
#   SOUND CLASS
# ==============================================================================
class InvalidSoundPack(_GunGameLibError):
    pass

class Sounds:
    '''Class that stores GunGame Sounds.'''
    def __init__(self, soundPackName):
        self.soundPackName = soundPackName
        
        # Set up the sound pack path
        if '.ini' in soundPackName:
            self.soundPackPath = '%s/cfg/gungame/sound_packs/%s' %(gameDir, soundPackName)
        else:
            self.soundPackPath = '%s/cfg/gungame/sound_packs/%s.ini' %(gameDir, soundPackName)
        
        # Make sure that the sound pack INI exists
        if self.__checkSoundPack():
            self.__readSoundPack()
        else:
            raise InvalidSoundPack('The soundpack %s doesn\'t exist.')
            
    def __readSoundPack(self):
        # Open the INI file
        soundPackINI = ConfigParser.ConfigParser()
        soundPackINI.read(self.soundPackPath)

        # Loop through each section (should only be 1) in the soundpack INI
        for section in soundPackINI.sections():
            # Loop through each option in the soundpack INI
            for option in soundPackINI.options(section):
                soundFile = soundPackINI.get(section, option)
                # Check to make sure they don't have the option set to "0" ... this means they want no sound for whatever event triggers it
                if soundPackINI.get(section, option) != '0':
                    # Check to make sure that the sound file exists
                    if self.__checkSound(soundFile):
                        # Add sound here
                        dict_gungameSounds[option] = soundFile
                    else:
                        # The sound may not exist, so we warn them that we were unable to locate it
                        echo('gungame', 0, 0, 'Sounds:CannotAdd', {'file': soundFile})
                        
                        # Add it anyway
                        dict_gungameSounds[option] = soundFile
                else:
                    # They have the sound disabled for this option. We'll set it to "0" in the gg_sounds dictionary
                    dict_gungameSounds[option] = 0
        
        # Add downloadables
        addDownloadableSounds()
    
    def __checkSoundPack(self):
        es.msg(self.soundPackPath)
        
        if os.path.isfile(self.soundPackPath):
            return True
        else:
            return False
        
    def __checkSound(self, soundFile):
        soundPath = '%s/sound/%s' %(gameDir, soundFile)
        if os.path.isfile(soundPath):
            return True
        else:
            return False

# ==============================================================================
#   ADDON CLASS
# ==============================================================================
class AddonError(_GunGameLibError):
    pass
    
class Addon:
    def __init__(self, addonName):
        self.addon = str(addonName)
        if self.validateAddon():
            # Set up default attributes for this addon
            self.menuText = ''
            self.dependencies = []
            echo('gungame', 0, 0, 'Addon:Registered', {'name': addonName})
        else:
            raise AddonError('%s is not an included or custom addon' % addonName)

    def __del__(self):
        for dependency in self.dependencies:
            # Remove dependency
            dict_registeredDependencies[dependency].delDependent(self.addon)
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
        
    def setMenuText(self, menuText):
        # Set menu text (test!)
        self.menuText = str(menuText)
        
    def addDependency(self, dependencyName, value):
        # Check if dependency already exists
        if not dict_registeredDependencies.has_key(dependencyName):
            # Check if dependency is a valid gungame variable
            if dict_cfgSettings.has_key(dependencyName):
                if self.isNumeric(value):
                    value = int(value)
                # Add dependency and original value to addon attributes
                self.dependencies.append(dependencyName)
                # Create dependency class
                dict_registeredDependencies[dependencyName] = addonDependency(dependencyName, value, self.addon)
                # Set GunGame variable to dependents value
                setVariableValue(dependencyName, value)
            else:
                raise AddonError('%s is not a valid dependency' % dependencyName)
        # Dependent is already registered
        else:
            # Add dependency and original value to addon attributes
            self.dependencies.append(dependencyName)
            # Add dependent to existing dependency
            dict_registeredDependencies[dependencyName].addDependent(value, self.addon)
    
    def delDependency(self, dependencyName):
        # Check if dependency exists first
        if dict_registeredDependencies.has_key(dependencyName):
            # Delete dependency
            dict_registeredDependencies[dependencyName].delDependent(self.addon)
        else:
            raise AddonError('%s is not a registered dependency!' % dependencyName)
    
    def isNumeric(self, string):
        try:
            test = int(string)
        except ValueError:
            return False
        else:
            return True
    
class addonDependency:
    def __init__(self, dependencyName, value, dependentName):
        # setup dependency class vars
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
            if dict_RegisteredAddons[dependentName].addonType == 'included':
                setVariableValue(dependentName, 0)
            else:
                es.unload('gungame/custom_addons/%s' %dependentName)
            echo('gungame', 0, 0, 'Dependency:Failed', {'name': self.dependency})
            
    def delDependent(self, dependentName):
        # Remove dependent from dependents list
        if dependentName in self.dependentList:
            self.dependentList.remove(dependentName)
            echo('gungame', 0, 1, 'Dependency:Unregistered', {'name': self.dependency})
            
            # Check if there are any more dependencies
            if not self.dependentList:
                if dict_cfgSettings:
                    # Set Variable back to it's original value
                    setVariableValue(self.dependency, self.dependencyOriginalValue)
                    
                # Delete depdency
                del dict_registeredDependencies[self.dependency]

                
# ==============================================================================
#   MESSAGE CLASS
# ==============================================================================
class Message:
    def __init__(self, addonName, filter):
        self.filter = filter
        self.addonName = addonName
        self.strings = None

    def __loadStrings(self):
        # Does the language file exist?
        if os.path.isfile(getGameDir('cfg/gungame/language_files/%s.ini' % self.addonName)):
            self.strings = langlib.Strings(getGameDir('cfg/gungame/language_files/%s.ini' % self.addonName))
        else:
            raise FileError('No string file exists for: %s' % self.addonName)
    
    def __cleanString(self, string):
        string = string.replace('\3', '').replace('\4', '').replace('\1', '')
        return string
    
    def __formatString(self, string, tokens, player = None):
        # Parse the string
        try:
            # Get the string
            rtnStr = self.strings(string, tokens, player.get('lang'))
        except:
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
            message = '\4[%s]\1 ' % (self.addonName)
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
            message = '\4[%s]\1 ' % (self.addonName)
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
            message = '[%s] ' % (self.addonName)
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

# ==============================================================================
#  MESSAGE FUNCTIONS
# ==============================================================================
def msg(addon, filter, string, tokens={}, showPrefix=True):
    Message(addon, filter).msg(string, tokens, showPrefix)
    
def echo(addon, filter, level, string, tokens={}, showPrefix=True):
    Message(addon, filter).echo(level, string, tokens, showPrefix)

def saytext2(addon, filter, index, string, tokens={}, showPrefix=True):
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
    
    # Reset the Player Information Database in the dict_gungameCore
    dict_gungameCore.clear()
    for userid in es.getUseridList():
        gungamePlayer = getPlayer(userid)
        
def clearGunGame():
    # Clear the dict_leaderInfo
    dict_leaderInfo.clear()
    
    # Clear the dict_gungameCore
    dict_gungameCore.clear()
    
    # Clear the dict_gungameWeaponOrders
    dict_gungameWeaponOrders.clear()
    
    # Clear the dict_weaponOrderSettings
    dict_weaponOrderSettings.clear()
    dict_weaponOrderSettings['currentWeaponOrderFile'] = None
    
    # Reset the Leader Information Database in the dict_leaderInfo
    dict_leaderInfo.clear()
    dict_leaderInfo['currentLeaders'] = []
    dict_leaderInfo['oldLeaders'] = []
    dict_leaderInfo['leaderLevel'] = 1
    
    # Reset the Player Information Database in the dict_gungameCore
    dict_gungameCore.clear()
    
    # Reset the Player Information Database in the dict_cfgSettings
    dict_cfgSettings.clear()
    
    # Clear the gungame globals
    dict_globals.clear()

# ==============================================================================
#   WEAPON RELATED COMMANDS
# ==============================================================================
def getCurrentWeaponOrderFile():
    return dict_weaponOrderSettings['currentWeaponOrderFile']
    
def getWeaponOrderString():
    weaponOrderString = None
    currentWeaponOrder = dict_weaponOrderSettings['currentWeaponOrderFile']
    for level in dict_gungameWeaponOrders[currentWeaponOrder]:
        if not weaponOrderString:
            weaponOrderString = dict_gungameWeaponOrders[currentWeaponOrder][level][0]
        else:
            weaponOrderString = '%s,%s' %(weaponOrderString, dict_gungameWeaponOrders[currentWeaponOrder][level][0])
    return weaponOrderString
    
def getWeaponOrderList():
    currentWeaponOrder = dict_weaponOrderSettings['currentWeaponOrderFile']
    list_weaponOrder = [dict_gungameWeaponOrders[currentWeaponOrder][level][0] for level in dict_gungameWeaponOrders[currentWeaponOrder]]
    return list_weaponOrder
    
def getLevelWeapon(levelNumber):
    levelNumber = int(levelNumber)
    if dict_gungameWeaponOrders[dict_weaponOrderSettings['currentWeaponOrderFile']].has_key(levelNumber):
        return str(dict_gungameWeaponOrders[dict_weaponOrderSettings['currentWeaponOrderFile']][levelNumber][0])
    else:
        raise GunGameValueError, 'Unable to retrieve weapon information: level \'%d\' does not exist' %levelNumber
        
def sendWeaponOrderMenu(userid):
    popuplib.send('gungameWeaponOrderMenu_page1', userid)

def weaponOrderMenuHandler(userid, choice, popupname):
    pass

# ==============================================================================
#   LEVEL RELATED COMMANDS
# ==============================================================================
def getTotalLevels():
    list_weaponOrderKeys = dict_gungameWeaponOrders[dict_weaponOrderSettings['currentWeaponOrderFile']].keys()
    return int(len(list_weaponOrderKeys))
    
def setPreventLevelAll(value):
    for userid in es.getUseridList():
        gungamePlayer = getPlayer(userid)
        gungamePlayer['preventlevel'] = int(value)

def getAverageLevel():
    averageLevel = 0
    averageDivider = 0
    for userid in dict_gungameCore:
        averageDivider += 1
        averageLevel += int(dict_gungameCore[userid]['level'])
    if averageDivider:
        return int(round(averageLevel / averageDivider))
    else:
        return 0
        
def getLevelUseridList(levelNumber):
    levelNumber = int(levelNumber)
    list_levelUserids = []
    for userid in dict_gungameCore:
        if dict_gungameCore[int(userid)]['level'] == levelNumber:
            list_levelUserids.append(userid)
    return list_levelUserids
    
def getLevelUseridString(levelNumber):
    levelNumber = int(levelNumber)
    levelUseridString = None
    for userid in dict_gungameCore:
        if dict_gungameCore[int(userid)]['level'] == levelNumber:
            if not levelUseridString:
                levelUseridString = userid
            else:
                levelUseridString = '%s,%s' %(levelUseridString, userid)
    return levelUseridString
    
def getLevelMultiKill(levelNumber):
    if dict_gungameWeaponOrders[dict_weaponOrderSettings['currentWeaponOrderFile']].has_key(levelNumber):
        return dict_gungameWeaponOrders[dict_weaponOrderSettings['currentWeaponOrderFile']][levelNumber][1]
    
def createScoreList(keyGroupName=None):
    dict_gungameScores = {}
    for userid in dict_gungameCore:
        dict_gungameScores[userid] = dict_gungameCore[userid]['level']
    if keyGroupName:
        list_sortedScores = sorted(dict_gungameScores.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        for useridLevelTuple in list_sortedScores:
            # <-- TO DO -->
            es.msg('keygroup %s created' %keyGroupName)
    else:
        return sorted(dict_gungameScores.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    
# ==============================================================================
#   LEADER RELATED COMMANDS
# ==============================================================================
def getCurrentLeaderList():
    return dict_leaderInfo['currentLeaders']
    
def getOldLeaderList():
    return dict_leaderInfo['oldLeaders']
    
def removeLeader(userid):
    userid = int(userid)
    if userid in dict_leaderInfo['currentLeaders']:
        dict_leaderInfo['currentLeaders'].remove(userid)
    
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
def getVariableValue(variableName):
    variableName = variableName.lower()
    if es.exists('variable', variableName):
        if dict_cfgSettings.has_key(variableName):
            return dict_cfgSettings[variableName]
        else:
            raise GunGameValueError, 'Unable to retrieve the variable value: The variable \'%s\' has not been registered with GunGame' %variableName
    else:
        raise GunGameValueError, 'Unable to retrieve the variable value: The variable \'%s\' has not been set as a console variable' %variableName

def setVariableValue(variableName, value):
    variableName = variableName.lower()
    if es.exists('variable', variableName):
        if dict_cfgSettings.has_key(variableName):
            if isNumeric(value):
                value = int(value)
            if es.ServerVar(variableName) != str(value):
                es.server.cmd('%s %s' %(variableName, value))
            if getVariableValue(variableName) != value:
                dict_cfgSettings[variableName] = value    
        else:
            raise GunGameValueError, 'Unable to set the variable value: The variable \'%s\' has not been registered with GunGame' %variableName
    else:
        raise GunGameValueError, 'Unable to set the variable value: The variable \'%s\' has not been set as a console variable' %variableName

def getVariableList():
    return dict_cfgSettings.keys()
    
# ==============================================================================
#   SOUND RELATED COMMANDS
# ==============================================================================
def addDownloadableSounds():
    for soundName in dict_gungameSounds:
        if dict_gungameSounds[soundName] != 0:
            es.stringtable('downloadables', 'sound/%s' %dict_gungameSounds[soundName])
            
def getSound(soundName):
    if dict_gungameSounds.has_key(soundName):
        if dict_gungameSounds[soundName] == '0':
            return 0
        else:
            return dict_gungameSounds[soundName]
    else:
        raise SoundError, 'The sound does not exist.'
    
# ==============================================================================
#   ADDON RELATED COMMANDS
# ==============================================================================
def registerAddon(addonName):
    if not dict_RegisteredAddons.has_key(addonName):
        dict_RegisteredAddons[addonName] = Addon(addonName)
        return dict_RegisteredAddons[addonName]
    else:
        raise AddonError('%s has already been registered.' % addonName)

def getAddon(addonName):
    if dict_RegisteredAddons.has_key(addonName):
        return dict_RegisteredAddons[addonName]
    else:
        raise AddonError('Cannot getAddon: %s doesn\'t exist!' % addonName)

def unregisterAddon(addonName):
    if dict_RegisteredAddons.has_key(addonName):
        del dict_RegisteredAddons[addonName]
    else:
        raise AddonError('%s has not been previously registered.' % addonName)

def getRegisteredAddonlist():
    return dict_RegisteredAddons.keys()
    
def getDependencyList():
    return dict_registeredDependencies.keys()
    
def getDependencyValue(dependencyName):
    return dict_registeredDependencies[dependencyName].dependencyValue
    
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
    '''Check to see if a string is an integer.'''
    try:
        int(string)
    except ValueError:
        return False
    
    return True

def getGameDir(dir):
    # Get game dir
    gamePath = str(es.ServerVar('eventscripts_gamedir'))
    
    # Fix for linux
    dir = dir.replace('\\', '/')
    
    # Return
    return '%s/%s' % (gamePath, dir)

def clientInServer(userid):
    return es.exists('userid', userid)

def inLevel():
    return (str(es.ServerVar('eventscripts_currentmap')) != '0')

def getLevelName():
    return str(es.ServerVar('eventscripts_currentmap'))

def isSpectator(userid):
    if not clientInServer(userid):
        return 0
    return (es.getplayerteam(userid) <= 1)

def hasEST():
    if str(es.ServerVar('est_version')) != '0':
        return True
    else:
        return False
    
def getESTVersion():
    if hasEST():
        return float(es.ServerVar('est_version'))
    else:
        return 0.000

def isDead(userid):
    return bool(int(es.getplayerprop(userid, 'CCSPlayer.baseclass.pl.deadflag')))