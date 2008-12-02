'''!
@package gungamelib
@version 5.0.559

Copyright (c) 2008, the GunGame Coding Team
Core GunGame Library
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python Imports
import string
import random
import os
import sys
import inspect
import time
import math
import cPickle
import wave
import mp3lib

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
dict_weaponOrderInstances = {}
dict_players = {}
dict_variables = {}
dict_globals = {}
dict_cfgSettings = {}
dict_sounds = {}
dict_addons = {}
dict_dependencies = {}
dict_addonLang = {}
dict_winners = {}
dict_weaponLists = {}

# Primary weapons
dict_weaponLists['primary'] =  ['awp', 'scout', 'aug', 'mac10', 'tmp',
                                'mp5navy', 'ump45', 'p90', 'galil', 'famas',
                                'ak47', 'sg552', 'sg550', 'g3sg1', 'm249',
                                'm3', 'xm1014', 'm4a1']

# Secondary weapons
dict_weaponLists['secondary'] =  ['glock', 'usp', 'p228', 'deagle', 'elite',
                                  'fiveseven']

# All weapon
dict_weaponLists['all'] =  dict_weaponLists['primary'] + \
                           dict_weaponLists['secondary'] + \
                           ['hegrenade', 'flashbang', 'smokegrenade']

# Valid weapon lists
dict_weaponLists['valid'] =  dict_weaponLists['primary'] + \
                             dict_weaponLists['secondary'] + \
                             ['hegrenade', 'knife']

list_criticalConfigs = ('gg_en_config.cfg', 'gg_default_addons.cfg')
list_configs = []
list_usedRandomSounds = []
currentWeaponOrder = None
osType = os.name
gamePath = str(es.ServerVar('eventscripts_gamedir'))
gamePath = gamePath.replace('\\', '/')

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

class InvalidSoundPack(Exception):
    pass

class SoundError(Exception):
    pass

class AddonError(Exception):
    pass

# ==============================================================================
#   CONVARS
# ==============================================================================
gungameDebugLevel = es.ServerVar('gg_debuglevel')
gungameDebugLevel.makepublic()

# ==============================================================================
#   PLAYER CLASS
# ==============================================================================
class Player(object):
    '''Player class, holds all a players information and attributes.'''
   
    __slots__ = ['userid', 'name', 'team', 'level', 'afkrounds', 'multikill',
                 'multilevel', 'preventlevel', 'afkmathtotal', 'steamid',
                 'index', 'language', 'isbot', 'stripexceptions']
    
    def __init__(self, userid):
        '''Called everytime getPlayer() is called, and all the attributes are
        refreshed.'''
        
        # Make userid an int
        self.userid = int(userid)
        
        if not es.exists('userid', self.userid):
            raise UseridError('Cannot get player (%s): not on the server.' % self.userid)
        
        self.__createPlayer()
    
    def __getitem__(self, item):
        # Lower-case the item
        item = str(item).lower()
        
        # Redirect to __getattribute__
        return object.__getattribute__(self, item)
    
    def __setitem__(self, item, value):
        # Redirect to __setattr__
        self.__setattr__(item, value)
    
    def __int__(self):
        '''Returns the players userid.'''
        return self.userid
    
    def __getattr__(self, item):
        # Lower-case the item
        item = str(item).lower()
        
        # Redirect to __getattribute__
        return object.__getattribute__(self, item)
    
    def __setattr__(self, item, value):
        # Format the item and value
        item = str(item).lower()
        
        if item not in ('name', 'steamid', 'preventlevel', 'language', 'stripexceptions'):
            value = int(value)
        
        # LEVEL
        if item == 'level':
            # Value check...
            if value < 0 and value > getTotalLevels():
                raise ValueError('Invalid value (%s): level value must be greater than 0 and less than %s.' % (value, getTotalLevels() + 1))
            
            # Preventlevel check
            # NOTE: No errors are raised if a level is attempted to be changed
            #       but prevent level is set! Ensure you check prevent level
            #       before changing a players level if the level requires to be
            #       changed.
            if len(self.preventlevel):
                return
            
            if hasattr(self, 'level'):
                # Get current leader
                currentLevel = self.level
            else:
                currentLevel = 1
            
            object.__setattr__(self, item, value)
            
            # Set multikill to 0
            self.multikill = 0
            
            # Levelling up...
            if value > currentLevel:
                leaders.addLeader(self.userid)
            
            # Levelling down
            elif value < currentLevel:
                leaders.removeLeader(self.userid)
            
            return
        
        # AFK ROUNDS
        elif item == 'afkrounds':
            # Value check...
            if value < 0:
                raise ValueError('Invalid value (%s): AFK Rounds value must be a positive number.' % value)
        
        # MULTIKILL
        elif item == 'multikill':
            if value < 0:
                raise ValueError('Invalid value (%s): multikill value must be a positive number.' % value)
        
        # MULTILEVEL
        elif item == 'multilevel':
            if value < 0 and value > 3:
                raise ValueError('Invalid value (%s): triple level value must be between 0 and 3.' % value)
                
        object.__setattr__(self, item, value)
    
    def __createPlayer(self):
        '''Reset all this players variables.'''
        
        self.name = es.getplayername(self.userid)
        self.team = es.getplayerteam(self.userid)
        self.preventlevel = []
        self.level = 1
        self.afkrounds = 0
        self.multikill = 0
        self.multilevel = 0
        self.afkmathtotal = 0
        self.steamid = playerlib.uniqueid(str(self.userid), 1)
        playerlibPlayer = playerlib.getPlayer(self.userid)
        self.index = int(playerlibPlayer.attributes['index'])
        self.language = playerlibPlayer.get('lang')
        self.isbot = es.isbot(self.userid)
        self.stripexceptions = []
    
    def resetPlayer(self):
        '''Reset the players attributes.'''
        
        self.__createPlayer()
    
    def resetPlayerLocation(self):
        '''Resets a players AFK math total.'''
        # Check the player exists
        if not es.exists('userid', self.userid):
            return
        
        # Get the player's location
        x, y, z = es.getplayerlocation(self.userid)
        
        # Get the AFK math total
        afkMathTotal = int(int(x) + int(y) + int(es.getplayerprop(self.userid, 'CCSPlayer.m_angEyeAngles[0]')) + int(es.getplayerprop(self.userid, 'CCSPlayer.m_angEyeAngles[1]')))
        
        # Update the AFK math total
        self.afkmathtotal = int(afkMathTotal)
    
    def playerNotAFK(self):
        '''Makes a player not AFK.'''
        # Make sure player is on a team
        if isSpectator(self.userid):
            raise TeamError('Unable to make player active (%s): not on a team.' % self.userid)
        
        # Reset player math total
        self.afkmathtotal = 0
        self.afkrounds = 0
    
    def isPlayerAFK(self):
        '''Checks a player is AFK.'''
        # Make sure player is on a team
        if isSpectator(self.userid):
            raise TeamError('Unable to check player AFK status (%s): not on a team.' % self.userid)
        
        # Get the player's location
        x, y, z = es.getplayerlocation(self.userid)
        
        # Get AFK math total
        afkMathTotal = int(int(x) + int(y) + int(es.getplayerprop(self.userid, 'CCSPlayer.m_angEyeAngles[0]')) + int(es.getplayerprop(self.userid, 'CCSPlayer.m_angEyeAngles[1]')))
        
        return afkMathTotal == self.afkmathtotal
    
    def afkPunish(self):
        '''Punishes a player if they have been AFK for too long.
        
        TODO: Use this instead of afkPunishCheck in gungame.py'''
        # Check if we are AFK.
        if not self.isPlayerAFK():
            return
        
        afkMaxAllowed = gungamelib.getVariableValue('gg_afk_rounds')
        
        # Is AFK punishment enabled?
        if afkMaxAllowed <= 0:
            return
        
        # Increment the afk round attribute
        gungamePlayer['afkrounds'] += 1
        
        # Have been AFK for too long
        if gungamePlayer['afkrounds'] < afkMaxAllowed:
            return
        
        # Kick the player
        if gungamelib.getVariableValue('gg_afk_action') == 1:
            es.server.queuecmd('kickid %s "You were AFK for too long."' % self.userid)
        
        # Show menu
        elif gungamelib.getVariableValue('gg_afk_action') == 2:
            # Send them to spectator
            es.server.queuecmd('es_xfire %d !self SetTeam 1' % self.userid)
            
            # Send a popup saying they were switched
            menu = popuplib.create('gungame_afk')
            menu.addline(gungamelib.lang('gungame', 'SwitchedToSpectator'))
            menu.send(userid)
        
        # Reset the AFK status
        self.playerNotAFK()
    
    def teleportPlayer(self, x, y, z, eyeangle0=0, eyeangle1=0):
        '''Teleport a player.'''
        # Make sure player is on a team
        if isSpectator(self.userid):
            raise TeamError('Unable to teleport player (%s): not on a team.' % self.userid)
        
        # Make sure the player is alive
        if isDead(self.userid):
            raise DeadError('Unable to teleport player (%s): not alive.' % self.userid)
        
        # Set position
        es.server.queuecmd('es_xsetpos %d %s %s %s' % (self.userid, x, y, z))
        
        # Set eye angles
        if eyeangle0 != 0 or eyeangle1 != 0:
            es.server.queuecmd('es_xsetang %d %s %s' % (self.userid, eyeangle0, eyeangle1))
        
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
        es.server.queuecmd('es_xsetang %d %s %s' % (self.userid, eyeangle0, eyeangle1))
        
        # Reset player AFK status
        gamethread.delayed(0.1, self.resetPlayerLocation, ())
    
    def stripPlayer(self):
        '''Strips the player of his primary and secondary weapon.'''
        # Get player handle
        playerHandle = es.getplayerhandle(self.userid)
        
        # Strip primary weapon
        for weaponType in ('primary', 'secondary'):
            weaponIndex = self.getWeaponIndex(playerHandle, weaponType)
            if weaponIndex:
                es.server.queuecmd('es_xremove %i' % weaponIndex)
                
        if self.getWeapon() in ['knife', 'hegrenade']:
            es.sexec(self.userid, 'use weapon_%s' %self.getWeapon())
    
    def getWeaponIndex(self, playerHandle, flag):
        for weapon in getWeaponList(flag):
            for weaponIndex in es.createentitylist('weapon_%s' % weapon):
                # Check the owner against the handle
                if es.getindexprop(weaponIndex, 'CBaseEntity.m_hOwnerEntity') == playerHandle:
                    return weaponIndex
    
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
        
        # Switch to their knife
        if playerWeapon == 'knife':
            es.sexec(self.userid, 'use weapon_knife')
        
        # Give and switch to their weapon
        else:
            es.delayed(0, 'es_xgive %s weapon_%s; es_xsexec %s "use weapon_%s"' % (self.userid, playerWeapon, self.userid, playerWeapon))
    
    def getWeapon(self):
        '''Returns the weapon for the players level.'''
        return getCurrentWeaponOrder().order[self.level][0]
    
    def give(self, weapon, useWeapon=0):
        ''' Gives a player the specified weapon.
            Weapons givin by this method will not be stripped by gg_dead_strip'''
        # Check if the weapon is valid
        weaponFormat = weapon.replace('weapon_', '')
        if weaponFormat not in getWeaponList('valid') + ['flashbang', 'smokegrenade']:
            raise PlayerError('Unable to give (%s): is not a valid weapon' % weapon)
        
        # Add weapon to strip exceptions so gg_dead_strip will not strip the weapon
        self.stripexceptions.append(weaponFormat)
        gamethread.delayed(0.01, self.stripexceptions.remove, (weaponFormat))
        
        # Give the player the weapon
        giveWeaponFormat = 'es_xgive %i weapon_%s' % (self.userid, weaponFormat)
        if useWeapon:
            giveWeaponFormat += '; es_xsexec %i "use weapon_%s"' % (self.userid, weaponFormat)
        es.server.queuecmd(giveWeaponFormat)
    
    def levelup(self, levelsAwarded, victim=0, reason=''):
        '''Formerly gungamelib.triggerLevelUpEvent
        
        This player should be the attacker (the player that is levelling up)
        '''
        # Return false if we can't level up
        if len(self.preventlevel):
            return False
        
        # Set old level and the new level
        oldLevel = self.level
        newLevel = self.level + int(levelsAwarded)
        self.level = clamp(newLevel, 1, getTotalLevels())
        
        # Fire the event
        es.event('initialize', 'gg_levelup')
        es.event('setint', 'gg_levelup', 'attacker', self.userid)
        es.event('setint', 'gg_levelup', 'leveler', self.userid)
        es.event('setint', 'gg_levelup', 'old_level', oldLevel)
        es.event('setint', 'gg_levelup', 'new_level', newLevel)
        es.event('setint', 'gg_levelup', 'userid', victim)
        es.event('setstring', 'gg_levelup', 'reason', reason)
        es.event('fire', 'gg_levelup')
        
        return True
    
    def leveldown(self, levelsTaken, attacker=0, reason=''):
        '''Formerly gungamelib.triggerLevelDownEvent
        
        This player should be the victim (the player that is levelling down)
        '''
        # Return false if we can't level down
        if len(self.preventlevel):
            return False
        
        # Set old level and the new level
        oldLevel = self.level
        self.level = clamp(self.level - int(levelsTaken), 1)
        
        # Fire the event
        es.event('initialize', 'gg_leveldown')
        es.event('setint', 'gg_leveldown', 'userid', self.userid)
        es.event('setint', 'gg_leveldown', 'leveler', self.userid)
        es.event('setint', 'gg_leveldown', 'old_level', oldLevel)
        es.event('setint', 'gg_leveldown', 'new_level', self.level)
        es.event('setint', 'gg_leveldown', 'attacker', attacker)
        es.event('setstring', 'gg_leveldown', 'reason', reason)
        es.event('fire', 'gg_leveldown')
        
        return True
    
    def setPreventLevel(self, value, addon, debug=False):
        '''Controls the setting of the "preventlevel" attribute.
        
        @remarks This must be used instead of setting the \c preventlevel attribute. This method prevents one addon from setting the preventlevel attribute to 0, while other addons still have it set to 1.'''
        
        value = int(value)
        
        # The value must be BOOL
        if value != 0 and value != 1:
            raise ValueError('Unable to set PreventLevel value (%s): must be 0 or 1.' % value)
        
        # See if the value is 0
        if not value:
            # If the addon is in the preventlevel list, remove it
            if addon in self.preventlevel:
                self.preventlevel.remove(addon)
            
            # Debug?
            if debug and self.getPreventLevel():
                # Display a list of addons still using preventlevel
                for addonName in self.preventlevel:
                    es.dbgmsg(0, 'PreventLevel is still set by addons: %s' % addonName)    
        else:
            # Require the addon to be registered to set the value to 1
            if addon not in getRegisteredAddonList():
                raise ValueError('Unable to set PreventLevel value (%s): addon (%s) must be registered to set the PreventLevel value to 1.' % (value, addon))
            
            if addon not in self.preventlevel:
                self.preventlevel.append(addon)
    
    def getPreventLevel(self):
        '''Returns the number of addons that have preventlevel set to 1.'''
        return len(self.preventlevel)
        
    def getAddonPreventLevel(self, addon):
        '''Retrieves the value of the preventlevel attribute for this particular addon.'''
        # Require the addon to be registered
        if addon not in dict_addons:
            raise AddonError('Unable to retrieve PreventLevel value for (%s): addon (%s) must be registered with GunGame.' %addon)
        
        # No information in the preventlevel dictionary
        if addon not in self.preventlevel:
            return 0
        
        return 1


# ==============================================================================
#   WEAPON ORDER CLASS
# ==============================================================================
class WeaponOrder(object):
    '''Parses weapon order files.'''
    
    def __init__(self, fileName):
        '''Initializes the WeaponOrder class.'''
        # Remove the extension from the file
        fileName = os.path.splitext(fileName)[0]
        
        # Set the filepath and name
        self.filepath = getGameDir('cfg/gungame5/weapon_orders/%s.txt' % fileName)
        self.filename = fileName
        
        # Initialise other variables
        self.displayname = None
        self.ordertype = None
        self.order = {}
        
        # Parse the file
        self.__parse()
    
    def __parse(self, override=False):
        '''Parses the weapon file.'''
        # Try to open the file
        try:
            weaponOrderFile = open(self.filepath, 'r')
        except IOError, e:
            raise FileError('Cannot parse weapon order file (%s): IOError: %s' % (self.filename, e))
        
        # Variable preparation
        levelCounter = 0
        
        # Clean and format the lines
        lines = [x.strip() for x in weaponOrderFile.readlines()]
        lines = filter(lambda x: x and (not x.startswith('//')), lines)
        
        # Close the file, we have the lines
        weaponOrderFile.close()
        
        # Loop through each line
        for line in lines:
            # Remove double spacing
            while '  ' in line:
                line = line.replace('  ', ' ')
            
            if line.startswith('=>'):
                # Set display name
                self.displayname = line[2:].strip()
                
                continue
            
            # Make the line lower-case
            line = line.lower()
            
            # Split line
            list_splitLine = line.split()
            
            # Check the weapon name
            weaponName = str(list_splitLine[0])
            if weaponName not in getWeaponList('valid'):
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
            
            if override:
                # Find level values
                for level in self.order:
                    if weaponName in self.order[level]:
                        self.order[level] = list_splitLine
            else:
                # Set level values
                self.order[levelCounter] = list_splitLine
        
        # Do we have a display name?
        if not self.displayname:
            echo('gungame', 0, 0, 'WeaponOrder:MissingDisplayName', {'name': self.filename})
            self.displayname = 'No display name set for this weapon order.'
    
    def echo(self):
        '''Prints out the current weapon order to console.'''
        echo('gungame', 0, 0, 'WeaponOrder:Echo:FileName', {'file': self.filename})
        echo('gungame', 0, 0, 'WeaponOrder:Echo:DisplayName', {'name': self.displayname})
        echo('gungame', 0, 0, 'WeaponOrder:Echo:Order', {'order': getVariableValue('gg_weapon_order_type')})
        es.dbgmsg(0, '[GunGame] ')
        es.dbgmsg(0, '[GunGame] +-------+-----------+---------------+')
        echo('gungame', 0, 0, 'WeaponOrder:Echo:TableColumns')
        es.dbgmsg(0, '[GunGame] +-------+-----------+---------------+')
        
        # Loop through each level
        for level in self.order:
            # Set variables
            weaponName = self.order[level][0]
            multiKillValue = self.order[level][1]
            
            # Print to console
            es.dbgmsg(0, '[GunGame] |  %2s   |     %d     | %13s |' % (level, multiKillValue, weaponName))
        
        es.dbgmsg(0, '[GunGame] +-------+-----------+---------------+')
    
    def setMultiKillOverride(self, value):
        '''Sets the multikill override.'''
        value = int(value)
        
        # Loop through the weapon order dictionary
        for level in self.order:
            # Set multikill if its not a knife or a hegrenade
            if self.order[level][0] != 'knife' and self.order[level][0] != 'hegrenade':
                self.order[level][1] = value
        
        # Rebuild weapon order menu
        self.buildWeaponOrderMenu()
        
        # Tell players the multikill value changed
        msg('gungame', '#all', 'WeaponOrder:MultikillValuesChanged', {'to': value})
        es.server.queuecmd('mp_restartgame 2')
    
    def setMultiKillDefaults(self):
        '''Sets the multikill values back to their default values.'''
        # Re-parse the file
        self.__parse(override=True)
        
        # Tell players the multikill values have been reset
        msg('gungame', '#all', 'WeaponOrder:MultikillReset')
        es.server.queuecmd('mp_restartgame 2')
    
    def setWeaponOrderFile(self, type):
        '''Sets the current weapon order file to this.'''
        # Set the current weapon order file
        # UNDO: getCurrentWeaponOrder() would not work without this if the
        #       variable gg_weapon_order_file was changed, then this function
        #       was called.
        if getVariableValue('gg_weapon_order_file') != self.filename:
            setVariableValue('gg_weapon_order_file', self.filename)
        
        # Tell players the weapon order file has changed
        msg('gungame', '#all', 'WeaponOrder:FileChanged', {'to': self.filename})
        
        # Set the weapon order type
        self.setWeaponOrderType(type)
    
    def getWeaponOrderType(self):
        '''Returns the weapon order type.'''
        return self.ordertype    

    def setWeaponOrderType(self, type):
        '''Changes the order of which the levels go.'''
        type = str(type).lower()
        
        if type not in ['#default', '#reversed', '#random']:
            raise ValueError('Unable to set weapon order type: %s is not a valid argument.' %type)
        
        # If the type is the same, do nothing
        if self.ordertype == type and type != '#random':
            return
        
        # Shuffled
        if type == '#random':
            # Get weapons
            weapons = self.order.values()
            
            # Setup variables
            knifeData = None
            nadeData = None
            
            # Get knife and grenade data
            for weapon in weapons[:]:
                if weapon[0] == 'knife':
                    # Get data
                    knifeData = weapon
                    
                    # Remove
                    weapons.remove(weapon)
                
                elif weapon[0] == 'hegrenade':
                    # Get data
                    nadeData = weapon
                    
                    # Remove
                    weapons.remove(weapon)
            
            # Shuffle
            random.shuffle(weapons)
            
            # Set weapon order
            self.order = dict(zip(range(1, len(weapons)+1), weapons))
            
            # Re-add knife and grenade to the end
            if nadeData != None:
                self.order[len(self.order)+1] = nadeData
            
            if knifeData != None:
                self.order[len(self.order)+1] = knifeData
        
        # Default
        elif type == '#default':
            # Re-parse the file
            self.__parse()
        
        # Reversed
        elif type == '#reversed':
            # Get weapons
            weapons = self.order.values()
            
            # Setup variables
            knifeData = None
            nadeData = None
            
            # Get knife and grenade data
            for weapon in weapons[:]:
                if weapon[0] == 'knife':
                    # Get data
                    knifeData = weapon
                    
                    # Remove
                    weapons.remove(weapon)
                
                elif weapon[0] == 'hegrenade':
                    # Get data
                    nadeData = weapon
                    
                    # Remove
                    weapons.remove(weapon)
            
            # Reverse
            weapons.reverse()
            
            # Set weapon order
            self.order = dict(zip(range(1, len(weapons)+1), weapons))
            
            # Re-add knife and grenade to the end
            if nadeData != None:
                self.order[len(self.order)+1] = nadeData
            
            if knifeData != None:
                self.order[len(self.order)+1] = knifeData
        
        # Set the new order type
        self.ordertype = type
        
        # Tell the players the weapon order has changed
        msg('gungame', '#all', 'WeaponOrder:ChangedTo', {'to': type[1:]})
        
        # Rebuild the menu
        self.buildWeaponOrderMenu()
        
        es.server.queuecmd('mp_restartgame 2')
    
    def buildWeaponOrderMenu(self):
        menu = OrderedMenu('weapon_order', [], 10, prepWeaponOrderMenu)
        menu.setTitle('GunGame: Weapon Order')
        [menu.addItem('[%s] %s' % (x[1], x[0])) for x in self.order.values()]
        menu.buildMenu()


# ==============================================================================
#   CONFIG CLASS
# ==============================================================================
class Config(object):
    '''Class for registration of config files used by GunGame.'''
    
    def __init__(self, name):
        '''Sets the class's variables.'''
        self.name = name
        self.path = getGameDir('cfg/gungame5/%s' % name)
        
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
            if not self.name in list_criticalConfigs:
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
            if line.count(' ') < 1:
                echo('gungame', 0, 0, 'Config:MissingValue', {'variable': line.split(' ')[0], 'name': self.name})
                continue
            
            variableName, variableValue = line.split(' ', 1)
            
            # Don't re-add variables, but change the value instead
            if variableName in dict_variables:
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
            if self.name in dict_cfgSettings:
                dict_cfgSettings[self.name].append(variableName)
                continue
            
            # Make the CFG setting for this config
            dict_cfgSettings[self.name] = [variableName]
        
        # Print config loaded
        echo('gungame', 0, 0, 'Config:Loaded', {'name': self.name})


# ==============================================================================
#   SOUND CLASS
# ==============================================================================
class Sounds(object):
    '''Soundpack class, adds sounds from a soundpack.'''
    
    def __init__(self, soundPackName):
        '''Initializes the Sound class.'''
        self.soundPackName = soundPackName
        
        # Set up the sound pack path
        if '.ini' in soundPackName:
            self.soundPackPath = getGameDir('cfg/gungame5/sound_packs/%s' % soundPackName)
        else:
            self.soundPackPath = getGameDir('cfg/gungame5/sound_packs/%s.ini' % soundPackName)
        
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
                if soundFile == '0':
                    dict_sounds[option] = 0
                    continue
                
                # Warn that we cannot find the sound
                if (not self.__checkSound(soundFile)) and (soundFile != '@random') and (',' not in soundFile):
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
class Addon(object):
    def __init__(self, addonName):
        self.addon = str(addonName)
        
        # Make sure the addon exists
        if not self.validateAddon() and addonName != 'gungame':
            raise AddonError('Cannot create addon (%s): addon folder doesn\'t exist.' % addonName)
        
        # Set up default attributes for this addon
        self.displayName = 'Untitled Addon'
        self.commands = {}
        self.publicCommands = {}
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
        if not addonExists(self.addon):
            return False
        
        if getAddonType(self.addon) == 0:
            self.addonType = 'custom'
        else:
            self.addonType = 'included'
        
        return True
    
    '''Command options:'''
    def registerPublicCommand(self, command, function, syntax='', console=True):
        if not callable(function):
            raise TypeError('Cannot register command (%s): callback is not callable.' % command)
        
        self.publicCommands[command] = function, syntax
        
        # Register block
        es.addons.registerBlock('gungamelib', command, self.__publicCommandCallback)
        
        # Register command if it isn't already registered
        if not es.exists('command', 'gg_%s' % command):
            es.regclientcmd('gg_%s' % command, 'gungamelib/%s' % command, 'Syntax: %s' % syntax)
            es.regsaycmd(getSayCommandName(command), 'gungamelib/%s' % command)
            
            # Register console command
            if console:
                es.regcmd('gg_%s' % command, 'gungamelib/%s' % command, 'Syntax: %s' % syntax)
    
    def registerAdminCommand(self, command, function, syntax='', console=True, log=True):
        if not callable(function):
            raise TypeError('Cannot register command (%s): callback is not callable.' % command)
        
        # Add command to commands dictionary
        self.commands[command] = function, syntax, console, log
        
        # Register console command (set console to False if you are getting conflicts)
        if console:
            # Register block
            es.addons.registerBlock('gungamelib', command, self.__adminCommandCallback)
            
            # Register command if its not already registered
            if not es.exists('command', 'gg_%s' % command):
                es.regcmd('gg_%s' % command, 'gungamelib/%s' % command, 'Syntax: %s' % syntax)
    
    def unregisterCommands(self):
        # Unregister admin commands
        for command in filter(lambda x: x[2], self.commands):
            es.addons.unregisterBlock('gungamelib', command)
        
        # Unregister public commands
        for command in filter(lambda x: x[2], self.publicCommands):
            es.addons.unregisterBlock('gungamelib', command)
    
    def __publicCommandCallback(self):
        # Get variables
        command = removeCommandPrefix(es.getargv(0))
        userid = es.getcmduserid()
        arguments = formatArgs()
        
        # Get command info
        callback, syntax = self.publicCommands[command]
        
        # Check the amount of arguments is correct
        if not inFunctionArgumentRange(callback, len(arguments)+1):
            message = 'NoParameters' if getMaximumFuncArgs(callback)-1 == 0 else 'InvalidSyntax'
            msg('gungame', userid, message, {'cmd': command, 'syntax': syntax})
            return
        
        # Try to call the function
        try:
            callback(userid, *arguments)
        
        # Report the error
        except:
            # Tell them an internal error occured
            msg('gungame', userid, 'InternalError', {'cmd': command})
            logException('Public command call. "%s" was called by "%s".' % (command, es.getplayersteamid(userid) if userid else 'CONSOLE'))
    
    def __adminCommandCallback(self):
        # Call command
        self.callCommand(removeCommandPrefix(es.getargv(0)), 0, formatArgs())
    
    def callCommand(self, command, userid, arguments):
        if command not in self.commands:
            raise AddonError('Cannot call command (%s): not registered.' % command)
        
        # Clean up the variables
        userid = int(userid)
        arguments = list(arguments)
        
        # Get details of the admin who called the command
        if userid: gungamePlayer = getPlayer(userid)
        adminIndex = gungamePlayer.index if userid else -1
        name = gungamePlayer.name if userid else 'CONSOLE'
        steamid = es.getplayersteamid(userid) if userid else 'CONSOLE'
        
        # Get command info
        callback, syntax, console, log = self.commands[command]
        
        # Check the amount of arguments is correct
        if not inFunctionArgumentRange(callback, len(arguments)+1):
            message = 'NoParameters' if getMaximumFuncArgs(callback)-1 == 0 else 'InvalidSyntax'
            msg('gungame', userid, message, {'cmd': command, 'syntax': syntax})
            return
        
        # Try to call the function
        try:
            callback(userid, *arguments)
        
        # Report the error
        except:
            # Tell them an internal error occured
            msg('gungame', userid, 'InternalError', {'cmd': command})
            logException('Admin command call. "%s" was called by "%s".' % (command, es.getplayersteamid(userid) if userid else 'CONSOLE'))
        
        # Log the command
        finally:
            # Tell everyone about what the admin ran
            if log:
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
        return command in self.commands or command in self.publicCommands
    
    def getCommandSyntax(self, command):
        if not self.hasCommand(command):
            raise AddonError('Cannot get command syntax (%s): not registered.' % command)
        
        if command in self.commands:
            return self.commands[command][1]
        else:
            return self.publicCommands[command][1]
    
    '''Menu options:'''
    def createMenu(self, selectfunc):
        self.menu = popuplib.easymenu(self.addon, None, selectfunc)
        self.menu.settitle(self.displayName)
    
    def setDescription(self, description):
        if not self.hasMenu():
            raise AddonError('Cannot set menu description (%s): menu hasn\'t been created.' % self.addon)
        
        self.menu.setdescription('%s\n * %s' % (self.menu.c_beginsep, description))
    
    def hasMenu(self):
        return (self.menu != None)
    
    def sendMenu(self, userid):
        if not self.hasMenu():
            raise AddonError('Cannot show menu (%s): menu hasn\'t been created.' % self.addon)
        
        self.menu.send(userid)
    
    '''Display name options:'''
    def setDisplayName(self, name):
        self.displayName = name
        
        # Set menu title (if created)
        if self.hasMenu():
            self.menu.settitle(name)
    
    def getDisplayName(self):
        return self.displayName
    
    '''Language options:'''
    def loadTranslationFile(self):
        # Set up Translation Files
        loadTranslations(self.addon)
    
    '''Dependency options:'''
    def addDependency(self, dependencyName, value):
        if isNumeric(value):
            value = int(value)
        
        # Check if dependency already exists
        if dependencyName not in dict_dependencies:
            # Check if dependency is a valid gungame variable
            if dependencyName not in dict_variables:
                raise AddonError('Cannot add dependency (%s): variable not registered.' % dependencyName)
            
            # Add dependency and original value to addon attributes
            self.dependencies.append(dependencyName)
            
            # Create dependency class
            dict_dependencies[dependencyName] = AddonDependency(dependencyName, value, self.addon)
            
            # Set GunGame variable to dependents value
            setVariableValue(dependencyName, value)
        # Dependent is already registered
        else:
            # Add dependency and original value to addon attributes
            self.dependencies.append(dependencyName)
            
            # Add dependent to existing dependency
            dict_dependencies[dependencyName].addDependent(value, self.addon)
    
    def delDependency(self, dependencyName):
        # Check if dependency exists first
        if dependencyName in dict_dependencies:
            # Delete dependency
            dict_dependencies[dependencyName].delDependent(self.addon)
        else:
            raise AddonError('Cannot delete dependency (%s): not registered.' % dependencyName)


# ==============================================================================
#   ADDON DEPENDENCY CLASS
# ==============================================================================
class AddonDependency(object):
    def __init__(self, dependencyName, value, dependentName):
        # Setup dependency class vars
        self.dependency = dependencyName
        self.dependencyValue = value
        self.dependencyOriginalValue = getVariableValue(dependencyName)
        self.dependentList = [dependentName]
        
        echo('gungame', 0, 2, 'Dependency:Registered', {'name': self.dependency})
    
    def addDependent(self, value, dependentName):
        # Dependant value the same?
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
class Message(object):
    '''Message class is used to broadcast linguistic messages around the server,
    with the use of translation files.'''
    
    def __init__(self, addonName):
        '''Initializes the class.'''
        self.addonName = addonName
        self.strings = None
        
        self.__loadStrings()
        
    def __formatFilter(self, filter):
        # Format filter
        filter = str(filter)
        if filter.isdigit():
            self.filter = int(filter)
        else:
            self.filter = filter
    
    def __loadStrings(self):
        '''Loads the Strings instance into the class.'''
        # Does the language file exist?
        if os.path.isfile(getGameDir('cfg/gungame5/translations/%s.ini' % self.addonName)):
            self.strings = langlib.Strings(getGameDir('cfg/gungame5/translations/%s.ini' % self.addonName))
        else:
            raise IOError('Cannot load strings (%s): no string file exists.' % self.addonName)
    
    def __cleanString(self, string):
        '''Cleans the string for output to the console.'''
        return string.replace('\3', '').replace('\4', '').replace('\1', '')
    
    def __formatString(self, string, tokens, player=None):
        '''Retrieves and formats the string.'''
        # Try to get string
        try:
            rtnStr = self.strings(string, tokens, player.language)
        except (KeyError, AttributeError):
            rtnStr = self.strings(string, tokens)
        
        # Format it
        rtnStr = rtnStr.replace('#lightgreen', '\3').replace('#green', '\4').replace('#default', '\1')
        
        # Windows string escaping
        if getOS() == 'nt':
            rtnStr = rtnStr.decode('string_escape')
        
        # Other OS string escaping
        else:
            rtnStr = rtnStr.replace('\\x01', '\x01').replace('\\x03', '\x03').replace('\\x04', '\x04')
            rtnStr = rtnStr.replace('\\1', '\x01').replace('\\3', '\x03').replace('\\4', '\x04')
            rtnStr = rtnStr.replace('\\n', '\n')
            rtnStr = rtnStr.replace('\\r', '\r')
            rtnStr = rtnStr.replace('\\t', '\t')
            rtnStr = rtnStr.replace('\\b', '\b')
            rtnStr = rtnStr.replace('\\v', '\v')
        
        # Crash prevention
        # !! DO NOT REMOVE !!
        rtnStr += ' '
        
        # Return the string
        return rtnStr
    
    def lang(self, string, tokens={}):
        return self.__formatString(string, tokens)
    
    def msg(self, filter, string, tokens, showPrefix = False):
        # Setup filter
        self.__formatFilter(filter)
        
        # Format the message
        if showPrefix:
            message = '\4[%s]\1 ' % getAddonDisplayName(self.addonName)
        else:
            message = ''
        
        # Loop through the players in the filter
        if isinstance(self.filter, int):
            # Get player object
            player = getPlayer(self.filter)
            
            # Send message
            es.tell(self.filter, '#multi', '%s%s' % (message, self.__formatString(string, tokens, player)))
        else:
            # Send message
            for player in playerlib.getPlayerList(self.filter):
                es.tell(int(player), '#multi', '%s%s' % (message, self.__formatString(string, tokens, player)))
        
        # Show in console
        if self.filter == '#all':
            self.echo(0, 0, string, tokens, showPrefix)
    
    def toptext(self, filter, duration, color, string, tokens):
        # Setup filter
        self.__formatFilter(filter)
        
        # Loop through the players in the filter
        if isinstance(self.filter, int):
            # Get player object
            player = getPlayer(self.filter)
            
            # Send message
            es.toptext(int(player), duration, color, self.__formatString(string, tokens, player))
        else:
            # Send message
            for player in playerlib.getPlayerList(self.filter):
                es.toptext(int(player), duration, color, self.__formatString(string, tokens, player))
    
    def hudhint(self, filter, string, tokens):
        # Setup filter
        self.__formatFilter(filter)
        
        # Loop through the players in the filter
        if isinstance(self.filter, int):
            # Get player object
            player = getPlayer(self.filter)
            
            # Send message
            usermsg.hudhint(int(player), self.__formatString(string, tokens, player))
        else:
            # Send message
            for player in playerlib.getPlayerList(self.filter):
                usermsg.hudhint(int(player), self.__formatString(string, tokens, player))
    
    def saytext2(self, filter, index, string, tokens, showPrefix = False):
        # Setup filter
        self.__formatFilter(filter)
        
        # Format the message
        if showPrefix:
            message = '\4[%s]\1 ' % getAddonDisplayName(self.addonName)
        else:
            message = ''
        
        # Loop through the players in the filter
        if isinstance(self.filter, int):
            # Get player object
            player = getPlayer(self.filter)
            
            # Send message
            usermsg.saytext2(int(player), index, '\1%s%s' % (message, self.__formatString(string, tokens, player)))
        
        else:
            # Send message
            for player in playerlib.getPlayerList(self.filter):
                usermsg.saytext2(int(player), index, '\1%s%s' % (message, self.__formatString(string, tokens, player)))
        
        # Show in console
        if self.filter == '#all':
            self.echo(0, 0, string, tokens, showPrefix)
    
    def centermsg(self, filter, string, tokens):
        # Setup filter
        self.__formatFilter(filter)
        
        # Loop through the players in the filter
        if isinstance(self.filter, int):
            # Get player object
            player = getPlayer(self.filter)
            
            # Send message
            usermsg.centermsg(int(player), self.__formatString(string, tokens, player))
        else:
            # Send message
            for player in playerlib.getPlayerList(self.filter):
                usermsg.centermsg(int(player), self.__formatString(string, tokens, player))
    
    def echo(self, filter, level, string, tokens, showPrefix = False):
        # Setup filter
        self.__formatFilter(filter)
        
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
            player = getPlayer(self.filter)
            
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
            for player in playerlib.getPlayerList(self.filter):
                # Get clean string
                cleanStr = self.__cleanString(self.__formatString(string, tokens, player))
                
                # Send message
                usermsg.echo(int(player), '%s%s' % (message, cleanStr))


# ==============================================================================
#   EASYINPUT CLASS
# ==============================================================================
class EasyInput(object):
    '''Makes "Esc"-style input boxes quickly and simply.
    
    Inspired by:
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
        # Set timeout
        self.timeout = clamp(timeout, 10, 199)
    
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
class Winners(object):
    '''Class used for tracking and storing Winners'''
    
    def __init__(self, uniqueid):
        self.uniqueid = str(uniqueid)
        
        # Load database
        if not getGlobal('winnersloaded'):
            loadWinnerDatabase()
        
        if self.uniqueid not in dict_winners:
            self.attributes = {'wins': 0, 'timestamp': time.time(), 'name': '<UNKNOWN>'}
            dict_winners[self.uniqueid] = self.attributes
        else:
            self.attributes = dict_winners[self.uniqueid]
    
    def __getitem__(self, item):
        # Make the item a lower-case string
        item = str(item).lower()
        
        # Does the attribute exist?
        if item not in self.attributes:
            raise KeyError(item)
        
        return self.attributes[item]
    
    def __setitem__(self, item, value):
        # Make the item a lower-case string
        item = str(item).lower()
        
        # Does the attribute exist?
        if item not in self.attributes:
            return
        
        if item == 'wins':
            self.attributes[item] = int(value)
        elif item == 'timestamp':
            self.attributes[item] = float(value)
        else:
            self.attributes[item] = value

            
# ==============================================================================
#  LEADER MANAGER CLASS
# ==============================================================================
class LeaderManager(object):
    '''Manages all the leaders.'''
    def __init__(self):
        # Set variables
        self.leaderLevel = 1
        self.leaders = []
        self.oldLeaders = []
        
        # Get leaders
        self.getNewLeaders()
    
    def __leaderTied(self, userid):
        '''Private function: Sets <userid> as a leader.'''
        # Set old leaders
        self.oldLeaders = self.leaders[:]
        
        # Add to leader list
        self.leaders.append(userid)
        
        # Tied leader messaging
        leaderCount = len(self.leaders)
        gungamePlayer = getPlayer(userid)
        if leaderCount == 2:
            saytext2('gungame', '#all', gungamePlayer.index, 'TiedLeader_Singular', {'player': gungamePlayer.name, 'level': self.leaderLevel}, False)
        else:
            saytext2('gungame', '#all', gungamePlayer.index, 'TiedLeader_Plural', {'count': leaderCount, 'player': gungamePlayer.name, 'level': self.leaderLevel}, False)
        
        # Fire gg_tied_leader
        es.event('initialize', 'gg_tied_leader')
        es.event('setint', 'gg_tied_leader', 'userid', userid)
        es.event('fire', 'gg_tied_leader')
    
    def __setLeader(self, userid):
        '''Private function: Sets <userid> as the leader.'''
        # Set old leaders
        self.oldLeaders = self.leaders[:]
        
        # Set leader vars
        self.leaders = [userid]
        self.leaderLevel = getPlayer(userid)['level']
        
        # Message about new leader
        gungamePlayer = getPlayer(userid)
        saytext2('gungame', '#all', gungamePlayer.index, 'NewLeader', {'player': gungamePlayer.name, 'level': self.leaderLevel}, False)
        
        # Fire gg_new_leader
        es.event('initialize', 'gg_new_leader')
        es.event('setint', 'gg_new_leader', 'userid', userid)
        es.event('fire', 'gg_new_leader')
    
    def addLeader(self, userid):
        '''Adds a new leader to the leader list.'''
        if not clientInServer(userid):
            raise ValueError('Cannot add leader (%s): client not in server.' % userid)
        
        # Get player object
        playerObj = getPlayer(userid)
        
        # Is already a leader?
        if self.isLeader(userid):
            # Set new leader
            if self.leaderLevel < playerObj['level']:
                self.__setLeader(userid)
        
        # Leader tied
        elif self.leaderLevel == playerObj['level']:
            self.__leaderTied(userid)
        
        # New leader
        elif self.leaderLevel < playerObj['level']:
            self.__setLeader(userid)
    
    def removeLeader(self, userid):
        '''Removes a leader from the leader list.'''
        # Is the leader not already here?
        if not self.isLeader(userid):
            return
        
        # Set old leaders
        self.oldLeaders = self.leaders[:]
        
        # Remove leader
        self.leaders.remove(userid)
        
        # Fire gg_leader_lostlevel
        es.event('initialize', 'gg_leader_lostlevel')
        es.event('setint', 'gg_leader_lostlevel', 'userid', userid)
        es.event('fire', 'gg_leader_lostlevel')
        
        # Need new leaders?
        if self.getLeaderCount() == 0:
            self.getNewLeaders()
    
    def getNewLeaders(self):
        '''Finds new leaders from the players available.'''
        # Var prep
        self.leaderLevel = 1
        self.leaders = []
        
        # Loop through the players
        for userid in dict_players:
            # Get player info
            playerObj = dict_players[userid]
            level = playerObj['level']
            
            # Is the player on the server?
            if not clientInServer(userid):
                continue
            
            # Create new leader variable and set new level
            if level > self.leaderLevel:
                self.leaders = [userid]
                self.leaderLevel = level
            
            # Another leader
            elif level == self.leaderLevel:
                self.leaders.append(userid)
        
        # 1 new leader
        if self.getLeaderCount() == 1:
            # Message about new leader
            saytext2('gungame', '#all', getPlayer(self.leaders[0])['index'], 'NewLeader', {'player': getPlayer(self.leaders[0])['name'], 'level': self.leaderLevel}, False)
            
            # Fire gg_new_leader
            es.event('initialize', 'gg_new_leader')
            es.event('setint', 'gg_new_leader', 'userid', userid)
            es.event('fire', 'gg_new_leader')
        
        # Set old leaders, if they have changed
        if self.leaders[:] != self.oldLeaders[:]:
            self.oldLeaders = self.leaders[:]
    
    def isLeader(self, userid):
        '''Checks if <userid> is a leader.'''
        return (userid in self.leaders)
    
    def __cleanupLeaders(self):
        '''Removes any old leaders.'''
        for x in self.leaders[:]:
            if not clientInServer(x):
                self.leaders.remove(x)
        
        if self.getLeaderCount() < 1:
            self.getNewLeaders()
    
    def getLeaderCount(self):
        '''Returns the amount of leaders.'''
        return len(self.leaders)
    
    def getOldLeaderList(self):
        '''Returns the userids of the old leader(s).'''
        return self.oldLeaders[:]
    
    def getLeaderList(self):
        '''Returns the userids of the current leader(s).'''
        self.__cleanupLeaders()
        
        return self.leaders[:]
    
    def getLeaderNames(self):
        '''Returns the names of the current leader(s).'''
        return [removeReturnChars(getPlayer(x)['name']) for x in self.getLeaderList()]
    
    def getLeaderLevel(self):
        '''Returns the current leader level.'''
        return self.leaderLevel

leaders = LeaderManager()


# ==============================================================================
#  ORDEREDMENU CLASS
# ==============================================================================
class OrderedMenu(object):
    '''This does basically the same as popuplib's EasyList, but the numbering
    schema continues throughout the pages.
    
    Example:
     * EasyList does:    1-10, 1-10, 1-10 on each page.
     * OrderedMenu does: 1-10, 11-20, 21-30'''
    
    def __init__(self, menu, items=[], options=10, prepUser=None):
        '''Initialize the class.'''
        # Set variables
        self.title = 'Untitled List'
        self.menu = menu
        self.items = items
        self.options = options
        self.prepUser = prepUser
    
    def setTitle(self, title):
        self.title = title
    
    def addItem(self, item):
        self.items.append(item)
    
    def buildMenu(self):
        # Set variables
        totalPageCount = math.ceil(float(len(self.items) / float(self.options)))
        pageCount = 1
        formattedTitle = '%s%s' % (self.title, ' ' * (50-len(self.title)))
        itemCount = 0
        itemPageCount = 0
        
        while pageCount <= totalPageCount:
            # Create menu variables
            menuName = 'OrderedMenu_%s:%s' % (self.menu, pageCount)
            lastMenuName = 'OrderedMenu_%s:%s' % (self.menu, pageCount-1)
            nextMenuName = 'OrderedMenu_%s:%s' % (self.menu, pageCount+1)
            itemPageCount = 0
            
            # Delete the menu, then create it
            if popuplib.exists(menuName):
                popuplib.unsendname(menuName, es.getUseridList())
                popuplib.delete(menuName)
            menu = popuplib.create(menuName)
            
            # Add title bar
            menu.addline('%s(%d/%d)' % (formattedTitle, pageCount, totalPageCount))
            menu.addline('-----------------------------')
            
            # Add items for this page
            while self.options > itemPageCount:
                if itemCount == len(self.items):
                    break
                
                itemCount += 1
                itemPageCount += 1
                
                menu.addline('%d. %s' % (itemCount, self.items[itemCount-1]))
            
            # Add blank lines
            while itemPageCount < self.options:
                itemPageCount += 1
                menu.addline(' ')
            
            # Add end seperator
            menu.addline('----------------------------')
            
            # First page
            if pageCount == 1:
                menu.addline(' ')
                
                # Is the last page?
                if pageCount != totalPageCount:
                    menu.addline('->9. Next')
                    menu.submenu(9, nextMenuName)
                
                # Is the first and final page
                else:
                    menu.addline(' ')
            
            # Last page
            elif pageCount == totalPageCount:
                menu.addline('->8. Back')
                menu.addline(' ')
                menu.submenu(8, lastMenuName)
            
            # Just a normal page
            else:
                menu.addline('->8. Back')
                menu.addline('->9. Next')
                menu.submenu(8, lastMenuName)
                menu.submenu(9, nextMenuName)
            
            # Finalize
            menu.addline('0. Exit')
            menu.displaymode = 'sticky'
            menu.select(10, lambda *args: True)
            
            # Prepuser?
            if self.prepUser:
                menu.prepuser = self.prepUser
            
            # Increment the page count
            pageCount += 1
    
    def rebuildMenu(self):
        #set variables
        totalPageCount = math.ceil(float(len(self.items) / float(self.options)))
        pageCount = 1
        itemCount = 0
        itemPageCount = 0
        
        while pageCount <= totalPageCount:
            # Create menu variables
            menuName = 'OrderedMenu_%s:%s' % (self.menu, pageCount)
            itemPageCount = 2
            
            # Delete the menu, then create it
            menu = popuplib.find(menuName)
            if not menu:
                return
            
            # Add items for this page
            while self.options > itemPageCount - 2:
                if itemCount == len(self.items):
                    break
                
                itemCount += 1
                itemPageCount += 1
                
                menu.modline(itemPageCount, '%d. %s' % (itemCount, self.items[itemCount-1]))
            
            # Increment the page count
            pageCount += 1
    
    def send(self, users):
        popuplib.send('OrderedMenu_%s:1' % (self.menu), users)


# ==============================================================================
#  CLASS WRAPPERS
# ==============================================================================
def getPlayer(userid):
    userid = int(userid)
    
    # Client already exists, return their instance
    if userid in dict_players:
        return dict_players[userid]
    
    # Check the client exists
    if not clientInServer(userid):
        raise UseridError('Cannot get player (%s): not on the server.' % userid)
    
    uniqueid = playerlib.uniqueid(str(userid), 1)
    
    for player in dict_players.copy():
        # SteamID match?
        if uniqueid not in dict_players[player]['steamid']:
            continue
        
        # Create a new instance and copy over certain attributes
        dict_players[userid] = Player(userid)
        
        # Set the "multikill" and "level" attributes to their old values
        for attribute in ['multikill', 'level']:
            # Set the attribute
            dict_players[userid][attribute] = dict_players[player][attribute]
        
        # Delete the old player instance and return the new
        del dict_players[player]
        return dict_players[userid]
    
    # The player didn't exist previously, so we will create a new instance
    dict_players[userid] = Player(userid)
    return dict_players[userid]

def getConfig(configName):
    return Config(configName)

def getSoundPack(soundPackName):
    return Sounds(soundPackName)

def getWinner(uniqueid):
    return Winners(uniqueid)
    
def getWeaponOrder(file):
    if file.endswith('.txt'):
        file = file[:-4]
    
    if file not in dict_weaponOrderInstances:
        dict_weaponOrderInstances[file] = WeaponOrder(file)
    
    return dict_weaponOrderInstances[file]

def getCurrentWeaponOrder():
    file = getVariableValue('gg_weapon_order_file')
    
    # Remove .txt ending
    if file.endswith('.txt'):
        file = file[:-4]
    
    return dict_weaponOrderInstances[file]

# ==============================================================================
#   MESSAGE FUNCTIONS
# ==============================================================================
def loadTranslations(addon):
    # Check the translations exist
    if not os.path.isfile(getGameDir('cfg/gungame5/translations/%s.ini' % addon)):
        raise IOError('Cannot load strings (%s): no string file exists.' % addon)
    
    dict_addonLang[addon] = Message(addon)

def lang(addon, string, tokens={}):
    return dict_addonLang[addon].lang(string, tokens)

def msg(addon, filter, string, tokens={}, showPrefix=True):
    if filter == 0:
        echo(addon, 0, 0, string, tokens, showPrefix)
    else:
        dict_addonLang[addon].msg(filter, string, tokens, showPrefix)

def toptext(addon, filter, duration, color, string, tokens={}):
    dict_addonLang[addon].toptext(filter, duration, color, string, tokens)
    
def echo(addon, filter, level, string, tokens={}, showPrefix=True):
    dict_addonLang[addon].echo(filter, level, string, tokens, showPrefix)

def saytext2(addon, filter, index, string, tokens={}, showPrefix=True):
    if filter == 0:
        echo(addon, 0, 0, string, tokens, filter, showPrefix)
    else:
        dict_addonLang[addon].saytext2(filter, index, string, tokens, showPrefix)

def hudhint(addon, filter, string, tokens={}):
    dict_addonLang[addon].hudhint(filter, string, tokens)

def centermsg(addon, filter, string, tokens={}):
    dict_addonLang[addon].centermsg(filter, string, tokens)
    
# ==============================================================================
#   MISCELLANEOUS COMMANDS
# ==============================================================================
def respawn(userid):
    respawnCommand = getVariable('gg_respawn_cmd')
    if '#' not in str(respawnCommand):
        # Userids not requiring the "#" symbol
        es.server.queuecmd('%s %s' % (respawnCommand, userid))
    else:
        # SourceMod Workaround
        es.server.queuecmd('%s%s' % (respawnCommand, userid))

# ==============================================================================
#   RESET GUNGAME --- WARNING: POWERFUL COMMAND
# ==============================================================================
def resetGunGame():
    global leaders
    
    # Reset the leader information
    leaders = LeaderManager()
    leaders.getNewLeaders()
    
    # Game is no longer over
    setGlobal('gameOver', 0)
    
    # Reset the player information dictionary
    dict_players.clear()
    
    # Add all players to the players dictionary
    for userid in es.getUseridList():
        gungamePlayer = getPlayer(userid)

def clearGunGame():
    global leaders
    
    # Clear the dict_players
    dict_players.clear()
    
    # Clear the weapon order instances
    dict_weaponOrderInstances.clear()
    
    # Reset the leader information
    leaders = LeaderManager()
    leaders.getNewLeaders()
    
    # Reset the stored variables
    dict_variables.clear()
    
    # Clear the gungame globals
    dict_globals.clear()

def clearOldPlayers():
    # Loop through the players
    for userid in dict_players.copy():
        # Remove from dict_players if they aren't in the server
        if not clientInServer(userid):
            del dict_players[userid]

# ==============================================================================
#   WEAPON RELATED COMMANDS
# ==============================================================================
def getWeaponOrderList():
    '''Retrieves and returns the weapon order in order as a list.'''
    weaponOrder = getCurrentWeaponOrder()
    return [weaponOrder.order[level][0] for level in weaponOrder.order]

def getLevelWeapon(levelNumber):
    '''Retrieves and returns the weapon for the specified level.'''
    return getCurrentWeaponOrder().order[int(levelNumber)][0]
    
def getWeaponList(flag):
    '''Retrieves a list of weapons based on the following flags:
        * primary   (all primary weapons)
        * secondary (all secondary weapons)
        * all       (all weapons, minus knife)
        * valid     (all weapons, including knife)
    
    Note: weapon_c4 is not included in any of the above lists.'''
    # Is the flag valid?
    if flag not in dict_weaponLists:
        raise ArgumentError('Invalid flag (%s) for getWeaponList: \'primary\', \'secondary\', \'all\', \'valid\'' % flag)
    
    return dict_weaponLists[flag]

def sendWeaponOrderMenu(userid):
    level = getPlayer(userid).level
    page = (level - 1) / 10 + 1
    sendOrderedMenu('weapon_order', userid, page)

def prepWeaponOrderMenu(userid, popupid):
    level = getPlayer(userid).level
    page = int((level - 1) / 10) + 1
    
    if popupid != 'OrderedMenu_weapon_order:%s' % page:
        return
    
    lineNumber = level - (page * 10) + 12 if page > 1 else level + 2
    menu = popuplib.find(popupid)
    
    menu.modline(lineNumber, '->%i. [%i] %s' % (level, getLevelMultiKill(level), getLevelWeapon(level)))
    gamethread.delayed(0, menu.modline, (lineNumber, '%i. [%i] %s' % (level, getLevelMultiKill(level), getLevelWeapon(level))))
    
# ==============================================================================
#   LEVEL RELATED COMMANDS
# ==============================================================================
def getTotalLevels():
    '''Returns the total number of levels in the weapon order.'''
    return len(getCurrentWeaponOrder().order)

def setPreventLevelAll(state, addon):
    '''Sets the "preventlevel" attribute for all players to the specified value.'''
    state = clamp(state, 0, 1)
    
    for player in getPlayerList():
        player.setPreventLevel(state, addon)

def getAverageLevel(userid=0):
    '''Returns the average level of all of the players active on the server.
       
       Optional userid will be excluded from the average level.'''
    totalLevels = 0
    averageDivider = 0
    
    # Get levels of all players in server
    for player in getPlayerList():
        #if a userid has been passed exclude them from the averaging
        if player.userid == int(userid):
            continue
        
        averageDivider += 1
        totalLevels += player.level
    
    if averageDivider:
        return totalLevels / averageDivider
    
    return 0

def getLevelUseridList(levelNumber):
    '''Returns a list of userids that are on the specified level.'''
    levelNumber = int(levelNumber)
    levelUserids = []
    
    for player in getPlayerList():
        if player.level == levelNumber:
            levelUserids.append(int(player))
    
    return levelUserids

def levelExists(levelNumber):
    '''Returns True if the specified level exists, False if not.
    
    Note: Do we REALLY need this?'''
    return levelNumber in getCurrentWeaponOrder().order

def getLevelInfo(levelNumber):
    '''Returns the weapon and multikill value.
    
    Note: Do we REALLY need this?'''
    # Does the level exist?
    if not levelExists(levelNumber):
        raise ValueError('Cannot get level info (%s): level does not exist!' % levelNumber)
    
    return getCurrentWeaponOrder().order[levelNumber]

def getLevelMultiKill(levelNumber):
    '''Returns the multikill value for the specified level.'''
    return getCurrentWeaponOrder().order[levelNumber][1]

# ==============================================================================
#   CONFIG RELATED COMMANDS
# ==============================================================================
def variableExists(variableName):
    return variableName.lower() in dict_variables

def getVariable(variableName):
    variableName = variableName.lower()
    
    if variableName not in dict_variables:
        raise ValueError('Unable to get variable object (%s): not registered.' % variableName)
    
    return dict_variables[variableName]

def getVariableValue(variableName):
    '''Returns the specified variable's value:
        * Returns as an integer or string.
    '''
    variableName = variableName.lower()
    
    if variableName not in dict_variables:
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
    '''Sets the specified variable to the specified value.
        * Updates the value internally in GunGame, and on the console.
        * Fires the server_cvar event.
        * Automatically sets as an integer or string.'''
    variableName = variableName.lower()
    
    if variableName not in dict_variables:
        raise ValueError('Unable to set variable value (%s): not registered.' % variableName)
    
    # Set variable value
    dict_variables[variableName].set(value)
    
    # Fire server_cvar
    es.server.cmd('%s %s' % (variableName, value))

def getVariableList():
    '''Returns a list of variables that GunGame tracks.'''
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
        # Does the sound exist?
        if dict_sounds[soundName] == 0:
            continue
        
        # If the sound is random, add winner sound
        if dict_sounds[soundName] == '@random':
            addDownloadableWinnerSound()
            continue
        
        # Add to downloadables
        es.stringtable('downloadables', 'sound/%s' % dict_sounds[soundName])

def addDownloadableWinnerSound():
    global list_usedRandomSounds
    
    # Make sure we are in a map
    if not inMap():
        return

    # Open the file
    sounds = getFileLines('cfg/gungame5/random_winner_sounds.txt')
    
    # No random sounds, set default
    if not sounds:
        list_usedRandomSounds = ['music/HL2_song15.mp3']
        return
    
    # Remove all the used sounds
    for sound in list_usedRandomSounds:
        sounds.remove(sound)
    
    # No sounds left
    if not sounds:
        # Reset used random sounds
        list_usedRandomSounds = []
        
        # Re-call this function
        addDownloadableWinnerSound()
        return
    
    # Set random sound and make it downloadable
    list_usedRandomSounds.append(random.choice(sounds))
    es.stringtable('downloadables', 'sound/%s' % list_usedRandomSounds[-1])
    
    # Don't handle chattime
    if not getVariableValue('gg_dynamic_chattime'):
        return
    
    # Get path data
    realPath = getGameDir('sound/%s' % list_usedRandomSounds[-1])
    
    # If the file doesn't exist, just leave it
    if not os.path.isfile(realPath):
        return
    
    ext = os.path.splitext(realPath)[1][1:]
    duration = int(es.ServerVar('mp_chattime'))
    
    # Is an mp3 file, use mp3lib
    if ext == 'mp3':
        try:
            info = mp3lib.mp3info(realPath)
            duration = clamp(info['MM'] * 60 + info['SS'], 5, 30)
        except:
            echo('gungame', 0, 0, 'DynamicChattimeError', {'file': list_usedRandomSounds[-1]})
            logException()
    
    # Is a wav file, use the wave module
    elif ext == 'wav':
        try:
            w = wave.open(realPath, 'rb')
            duration = clamp(float(w.getnframes()) / w.getframerate(), 5, 30)
        except:
            echo('gungame', 0, 0, 'DynamicChattimeError', {'file': list_usedRandomSounds[-1]})
            logException()
        finally:
            w.close()
    
    # Set chattime
    es.delayed(5, 'mp_chattime %s' % duration)

def getSound(soundName):
    if soundName not in dict_sounds:
        raise SoundError('Cannot get sound (%s): sound file not found.' % soundName)
    
    # Is a random sound
    if dict_sounds[soundName] == '@random':
        return list_usedRandomSounds[-1]
    
    # Just return the normal
    else:
        return dict_sounds[soundName]

def getSoundSafe(soundName):
    # Does the sound exist?
    if soundName not in dict_sounds:
        return
    
    # Get sound object
    sound = getSound(soundName)
    
    # Is the sound empty or 0?
    if not sound:
        return
    
    # Get a random sound file from the list of sounds
    sound = sound.split(',')
    sound = random.choice(sound)
    
    # Return sound
    return sound

def playSound(filter, soundName, volume=1.0):
    # Get sound
    sound = getSoundSafe(soundName)
    
    if not sound:
        return
    
    # Play to 1 player
    if isNumeric(filter) or isinstance(filter, int):
        es.playsound(filter, sound, volume)
        return
    
    # Play to filter
    for userid in playerlib.getUseridList(filter):
        es.playsound(userid, sound, volume)

def emitSound(emitter, soundName, volume=1.0, attenuation=1.0):
    # Get sound
    sound = getSoundSafe(soundName)
    
    if not sound:
        return
    
    # Emit!
    es.emitsound('player', emitter, sound, volume, attenuation)

# ==============================================================================
#   MENU COMMANDS
# ==============================================================================
def getOrderedMenuName(name):
    return 'OrderedMenu_%s:1' % name

def sendOrderedMenu(name, users, page=1):
    popuplib.send('OrderedMenu_%s:%i' % (name, page), users)

# ==============================================================================
#   WINNER RELATED COMMANDS
# ==============================================================================
def getWinnerList():
    return dict_winners.keys()

def getTotalWinners():
    return len(getWinnerList())

def getWinnerRank(steamid):
    winners = getOrderedWinners()
    
    # Not a winner?
    if steamid not in winners:
        return -1
    
    return winners.index(steamid)+1

def getOrderedWinners():
    return sorted(dict_winners, key=lambda x: dict_winners[x]['wins'], reverse=True)

def getWinnerName(uniqueid):
    if uniqueid in dict_winners:
        return dict_winners[uniqueid]['name']
    else:
        return '<UNKNOWN>'

def getWins(uniqueid):
    uniqueid = str(uniqueid)
    
    if uniqueid in dict_winners:
        return dict_winners[uniqueid]['wins']
    else:
        return 0

def addWin(uniqueid):
    gungameWinner = getWinner(uniqueid)
    gungameWinner['wins'] += 1
    gungameWinner['name'] = es.getplayername(es.getuserid(uniqueid))

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

def loadWinnerDatabase():
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

def pruneWinnerDatabase(days):
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
    '''!Register an addon.
    
    @exception ValueError is raised if the addon is already registered.
    '''
    if addonName in dict_addons:
        raise ValueError('Cannot register addon (%s): already registered.' % addonName)
    
    # Register the addon and return the addon instance
    dict_addons[addonName] = Addon(addonName)
    return dict_addons[addonName]

def getAddon(addonName):
    '''!Get an addon instance.
    
    @exception ValueError is raised if the addon is not registered. See addonRegistered'''
    # Check the addon is registered
    if not addonRegistered(addonName):
        raise ValueError('Cannot get addon instance (%s): not already registered.' % addonName)
    
    return dict_addons[addonName]

def unregisterAddon(addonName):
    '''!Unregisters an addon.
    
    @param addonName Name of the addon to unregister.'''
    # Check if the addon is registered
    if not addonRegistered(addonName):
        return
    
    # Unregister addon
    dict_addons[addonName].unregisterCommands()
    del dict_addons[addonName]

def getAddonDisplayName(addonName):
    '''!Gets the display name of an addon.
    
    @exception ValueError is raised if \p addonName is not registered.
    
    @remarks Use addonRegistered before using this function to prevent raise errors.
    
    @return The display name of \p addonName.
    '''
    # Is GunGame?
    if addonName == 'gungame':
        return 'GunGame'
    
    # Check if the addon is registered
    if not addonRegistered(addonName):
        raise ValueError('Cannot get display name (%s): not registered.' % addonName)
    
    return dict_addons[addonName].getDisplayName()

def addonRegistered(addonName):
    '''!Checks to see if an addon is registered.
    
    @param addonName Name of the addon to check.
    
    @retval True The addon is registered.
    @retval False The addon is not registered.
    
    @remarks Use this before trying getAddon'''
    return addonName in dict_addons

def getRegisteredAddonList():
    '''!@return A list of registered addons.'''
    return dict_addons.keys()

def getDependencyList():
    '''!@return A list of current dependencies.'''
    return dict_dependencies.keys()

def dependencyExists(dependencyName):
    '''!Checks to see if a dependency exists.
    
    @param dependencyName The name of the dependency to check.
    
    @retval True The dependency exists.
    @retval False The dependency does not exist.'''
    return dependencyName in dict_dependencies

def getDependencyValue(dependencyName):
    '''!Gets the value of a dependency.
    
    @exception KeyError is raised if the dependency does not exist.
    
    @param dependencyName Name of the dependency to get the value of.
    
    @remarks Use dependencyExists before using this function to prevent raise errors.
    
    @return Value of the dependency.'''
    return dict_dependencies[dependencyName].dependencyValue

# ==============================================================================
#   GLOBALS RELATED COMMANDS
# ==============================================================================
def setGlobal(variableName, variableValue):
    '''!Sets the value of a global variable.
    
    @remark \p variableName is \b not case sensitive.'''
    variableName = variableName.lower()
    
    if isNumeric(variableValue):
        variableValue = int(variableValue)
    
    dict_globals[variableName] = variableValue

def getGlobal(variableName):
    '''!Returns the value of a global variable.
    
    @return The value of the variable
    @retval 0 The variable does not exist
    
    @remark \p variableName is \b not case sensitive.'''
    variableName = variableName.lower()
    
    if variableName in dict_globals:
        return dict_globals[variableName]
    else:
        return 0

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def isNumeric(value):
    '''!Checks to see if \p value can be converted to an integer.
    
    @param value Value to check
    
    @retval True \p value can be converted.
    @retval False \p value cannot be converted.'''
    try:
        int(value)
        return True
    except ValueError:
        return False

def getCfgDir(dir):
    '''!@return An absolute path to the gungame config directory plus \p dir.'''
    return getGameDir('cfg/gungame5/%s' % dir)

def getGameDir(dir):
    '''!Gets an absolute path to a game directory.
    
    @remark Implicitly replaces \\ with / (linux support)
    
    @param dir Directory to append to the game directory.
    
    @return An absolute path to the game directory plus \p dir.'''
    # Linux path seperators
    dir = dir.replace('\\', '/')
    
    # Return
    return '%s/%s' % (gamePath, dir)

def getAddonDir(addonName, dir):
    '''!Gets an absolute path to an addon directory.
    
    @exception ValueError is raised if \p addonName points to an invalid addon.
    
    @remark Implicitly replaces \\ with / (linux support)
    
    @param addonName Name of the addon to get the directory of
    @param dir Additional directory to append to the result
    
    @return addons/eventscripts/gungame/[included/custom]_addons/\p addonName/\p dir'''
    # Check addon exists
    if not addonExists(addonName):
        raise ValueError('Cannot get addon directory (%s): doesn\'t exist.' % addonName)
    
    # Get game dir
    addonPath = getGameDir('addons/eventscripts/gungame')
    
    # Linux path seperators
    dir = dir.replace('\\', '/')
    
    # Return
    return '%s/%s/%s' % (addonPath, 'custom_addons' if getAddonType(addonName) else 'included_addons', dir)

def clientInServer(userid):
    '''!Checks to see whether \p userid is in the server.
    
    @param userid Player to check.
    
    @retval True The client is on the server.
    @retval False The client is not on the server.'''
    return es.exists('userid', userid)

def inMap():
    '''!Checks to see if the server is currently in a map.
    
    @retval True The server is in a map.
    @retval False The server is not in a map.'''
    return (str(es.ServerVar('eventscripts_currentmap')) != '')

def isSpectator(userid):
    '''!Checks to see if \p userid is a spectator.
    
    @retval True The player is a spectator, currently connecting or not on the server.
    @retval False The player is on an active team.'''
    return getPlayer(userid).team <= 1

def hasEST():
    '''!Checks to see if ESTools is installed on the server.
    
    @retval True This server has EST installed.
    @retval False This server does not have EST installed.'''
    return str(es.ServerVar('est_version')) != '0'
    
def getESTVersion():
    '''!Gets the current version of ESTools.
    
    @return The value of \b est_version.
    
    @retval 0.0 If EST is not on the server. See hasEST().'''
    if hasEST():
        return float(es.ServerVar('est_version'))
    else:
        return 0.000

def isDead(userid):
    '''!Checks to see if \p userid is dead.
    
    @retval 1 The player is dead.
    @retval 0 The player is alive.'''
    return es.getplayerprop(userid, 'CBasePlayer.pl.deadflag')

def playerExists(userid):
    '''!Checks to see if \p userid is in \c dict_players.
    
    @retval True The player has a \c Player instance.
    @return False The player has no \c Player instance.'''
    userid = int(userid)
    return userid in dict_players

def getAddonType(addonName):
    '''!Gets the type of an addon.
    
    @param addonName The name of the addon to get the type of.
    
    @retval 0 /p addonName is an included addon.
    @retval 1 /p addonName is a custom addon.'''
    # Check addon exists
    if not addonExists(addonName):
        raise ValueError('Cannot get addon type (%s): doesn\'t exist.' % addonName)
    
    # Get addon type
    return int(os.path.isdir(getGameDir('addons/eventscripts/gungame/included_addons/%s' % addonName)))

def addonExists(addonName):
    '''!Checks to see if an addon exists.
    
    @param addonName The name of the addon to check exists.
    
    @return True or False depending on whether the addon exists.'''
    return os.path.isdir(getGameDir('addons/eventscripts/gungame/included_addons/%s' % addonName)) or os.path.isdir(getGameDir('addons/eventscripts/gungame/custom_addons/%s' % addonName))

def formatArgs():
    '''!@return A list of arguments that was supplied to the last console command.'''
    return map(es.getargv, xrange(1, es.getargc()))

def removeReturnChars(value):
    '''!Removes return characters (\\r and \\n) from \p value.
    
    @param value The string to clean.
    
    @return \p value with \\r and \\n removed from its contents.'''
    return str(value).strip('\r\n')

def clamp(val, lowVal=False, highVal=False):
    '''!Clamps a value between its low and high boundaries.
    
    If \p val is less than \p lowVal, \p lowVal will be returned.
    If \p val is greater than \p highVal, \p highVal will be returned.
    
    @param val The value to clamp between \p lowVal> and \p highVal
    @param lowVal The lowest value \p val may be. Set this to False to not have a lower boundary.
    @param highVal The highest value \p val may be. Set this to False to not have a lower boundary.
    
    @return A clamped value.'''
    if lowVal and highVal:
        return max(lowVal, min(val, highVal))
    elif lowVal is not False:
        return max(lowVal, val)
    elif highVal is not False:
        return min(highVal, val)
    
    return val

def canShowHints():
    '''!Checks to see if the HUDHint space is being used by a counter.
    
    @retval True If the HUDHint space is clear.
    @retval False If the HUDHint space is being used by a counter.'''
    return getGlobal('isWarmup') == 0 and getGlobal('voteActive') == 0

def getFileLines(location, removeBlankLines=True, comment='//', stripLines=True):
    '''!Processes a file, removing blank lines, commented lines and strips lines, too.
    
    @exception IOError will be raised if the file location is invalid.
    @exception OSError will be raised in certain invalid file location occasions.
    
    @see http://docs.python.org/lib/module-exceptions.html
    
    @param location The location of the file relative to the cstrike root directory.
    @param removeBlankLines [bool] Whether to remove blank lines or not.
    @param comment Lines starting with this string will be removed (making this value empty doesn't remove commented lines)
    @param stripLines [bool] Whether to strip lines or not.
    
    @return The processed lines.'''
    # Open file and get lines
    file = open(getGameDir(location), 'r')
    lines = file.readlines()
    file.close()
    
    # Strip lines
    if stripLines:
        lines = [x.strip() for x in lines]
    
    # Remove blank lines
    if removeBlankLines:
        lines = filter(bool, lines)
    
    # Remove commented lines
    if comment:
        lines = filter(lambda x: not x.startswith(comment), lines)
    
    return lines

def getSayCommandName(command):
    '''!Prefixes \p command with the say command prefix.
    
    @param command The name of the command to be prefixed
    
    @return \p command prefixed with the value of \b gg_say_prefix.'''
    return '%s%s' % (getVariableValue('gg_say_prefix'), command)

def removeCommandPrefix(command):
    '''!Removes the command prefixes (gg_ or the say command prefix) from \p command
    
    @param command The command to be cleaned
    
    @return The command name without prefixes.'''
    command = command.lower()
    
    # Get say prefix
    sayPrefix = getVariableValue('gg_say_prefix')
    
    # Starts with gg_ (console command)
    if command.startswith('gg_'):
        return command[3:]
    
    # Starts with the say prefix (say command)
    elif command.startswith(sayPrefix):
        return command[len(sayPrefix):]
    
    # Return the raw command
    return command

def getPlayerList(filter='#all'):
    '''!Returns a list of Player objects, filtered by the /p filter parameter.
    
    @return [list] Player instances.'''
    return map(getPlayer, playerlib.getUseridList(filter))

def getOS():
    '''!Returns the operating system type.
    
    @retval nt Windows NT
    @retval posix Unix & its variants.'''
    return osType

def getMinimumFuncArgs(function):
    '''!Gets the amount of required arguments for a function.
    
    @exception TypeError function must be a: static or class method, lambda or a normal function; builtins are not supported.
    
    @param function Function to get minimum arguments for.
    
    @return Minimum amount of arguments this function can be passed.'''
    if not hasattr(function, 'func_code'):
        raise TypeError('This function only supports: static methods, class methods and functions (NOT BUILTINS!). Ensure you have passed a function.')
    
    # Initialise variables
    modifier = 0
    names, _, __, defaults = inspect.getargspec(function)
    
    # Does this function have any defaults?
    if defaults:
        modifier -= len(defaults)
    
    # Is this a class method?
    if hasattr(function, 'im_func'):
       modifier -= 1
    
    return len(names) + modifier

def getMaximumFuncArgs(function):
    '''!Gets the maximum amount of arguments this function can be passed.
    
    @param function Function to get maximum arguments for.
    
    @retval -1 This function doesn't have limit on arguments.
    
    @return Maximum amount of arguments this function can be passed.'''
    if not hasattr(function, 'func_code'):
        raise TypeError('This function only supports: static methods, class methods and functions (NOT BUILTINS!). Ensure you have passed a function.')
    
    # Initialise variables
    modifier = 0
    names, varargs, _, defaults = inspect.getargspec(function)
    
    if varargs:
        return -1
    
    # Does this function have any defaults?
    if defaults:
        modifier += len(defaults)
    
    # Is this a class method?
    if hasattr(function, 'im_func'):
       modifier -= 1
    
    return len(names) + modifier

def inFunctionArgumentRange(function, arguments):
    '''!Checks to see whether \p arguments is within the allowed arguments of the function.

    @param function Function to check against.
    @param arguments Amount of arguments to check is in range.

    @return bool'''
    # Varargs (*args) support
    maxArgs = getMaximumFuncArgs(function)
    
    if maxArgs == -1:
        return True
    
    return getMinimumFuncArgs(function) <= arguments <= maxArgs

def logException(notes=None):
    '''!Shows the last error in the target's console and places it in the error log (if gg_error_logging is enabled).
    
    @note This will only log if gg_error_logging is enabled, otherwise it will just appear in the server console as normal.'''
    # Set parameters
    params = list(sys.exc_info())
    
    # Add notes if error logging is available
    if getVariableValue('gg_error_logging') == 1:
        params.append(notes)
    
    # Call the except hook
    sys.excepthook(*params)

def getVersion():
    '''!Gets the running GunGame version.
    
    @return tuple of integers: (major version, minor version, SVN revision)'''
    return tuple(map(int, str(es.ServerVar('eventscripts_gg')).split('.')))

def compareVersion(version):
    '''!Compares \p version with the current running GunGame version.
    
    @param version Version to compare. Must be an iterable object, 3 items, all integers.
    
    @retval -1 The supplied version is less than the one that is running.
    @retval 0 The supplied version is equal to the one that is running.
    @retval 1 The supplied version is greater than the one that is running.'''
    return cmp(version, getVersion())