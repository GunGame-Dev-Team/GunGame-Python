# Python imports
import os
import ConfigParser
import cPickle
import string

# EventScripts imports
import es
import gamethread
import playerlib
import langlib
import usermsg
import popuplib
import keyvalues

# GunGame imports
import gungamelib

# Create a public CVAR for GunGame seen as "eventscripts_ggp"
gungameVersion = "1.0.117"
es.set('eventscripts_ggp', gungameVersion)
es.makepublic('eventscripts_ggp')

# Register the addon with EventScripts
info = es.AddonInfo() 
info.name     = "GunGame: Python" 
info.version  = gungameVersion
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame" 
info.author   = "GunGame Development Team"

# TEMP CODE FOR PROFILER
import time
g_Prof = {}
def StartProfiling(storage):
    storage['start'] = time.clock()

def StopProfiling(storage):
    storage['stop'] = time.clock()

def GetProfilerTime(storage): 
    return storage['stop'] - storage['start']

# Global vars
dict_gungameVariables = {}
dict_cfgSettings = {}
dict_globals = {}
list_primaryWeapons = ['awp', 'scout', 'aug', 'mac10', 'tmp', 'mp5navy',
                       'ump45', 'p90', 'galil', 'famas', 'ak47', 'sg552',
                       'sg550', 'g3sg1', 'm249', 'm3', 'xm1014', 'm4a1']
list_secondaryWeapons = ['glock', 'usp', 'p228', 'deagle', 'elite', 'fiveseven']
list_allWeapons = ['glock', 'usp', 'p228', 'deagle', 'elite', 'fiveseven',
                   'awp', 'scout', 'aug', 'mac10', 'tmp', 'mp5navy', 'ump45',
                   'p90', 'galil', 'famas', 'ak47', 'sg552', 'sg550', 'g3sg1',
                   'm249', 'm3', 'xm1014', 'm4a1', 'hegrenade', 'flashbang',
                   'smokegrenade']
dict_gungameRegisteredAddons = {}
dict_reconnectingPlayers = {}
dict_gungameWinners = {}
dict_gungameRegisteredDependencies = {}
list_includedAddonsDir = []
list_customAddonsDir = []
list_leaderNames = []
list_stripExceptions = []

# Class used in dict_gungameWinners
class gungameWinners:
    "Class used to store GunGame winner information"
    int_wins = 1
    int_timestamp = es.gettime()

# Begin Multiple Error Classes
class _GunGameQueryError:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class UseridError(_GunGameQueryError):
    pass

class PlayerError(_GunGameQueryError):
    pass

class ArgumentError(_GunGameQueryError):
    pass
    
class LevelValueError(_GunGameQueryError):
    pass

class MultiKillValueError(_GunGameQueryError):
    pass
    
class AFKValueError(_GunGameQueryError):
    pass

class TripleValueError(_GunGameQueryError):
    pass

class VariableError(_GunGameQueryError):
    pass
# End Multiple Error Classes

# ==========================================================================================================================
# ==========================================================================================================================
#        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! BEGIN POPUPLIB COMMANDS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
# ==========================================================================================================================
# ==========================================================================================================================

# Display the GunGame Weapon Order Popup to the player that requested it
def displayWeaponOrderMenu():
    gungamelib.sendWeaponOrderMenu(es.getcmduserid())
    
# GUNGAME LEVEL POPUP
gungameLevelMenu = None

# Display the Level Popup to the player that requested it
def displayLevelMenu():
    popuplib.send('gungameLevelMenu', es.getcmduserid())

def buildLevelMenu():
    global dict_gungame_core
    # Check to see if the popup "gungameLevelMenu" exists
    if popuplib.exists('gungameLevelMenu'):
        # The popup exists...let's unsend it
        popuplib.unsendname('gungameLevelMenu', playerlib.getUseridList('#human'))
        # Now, we need to delete it
        popuplib.delete('gungameLevelMenu')
    # Let's create the "gungameLevelMenu" popup
    gungameLevelMenu = popuplib.create('gungameLevelMenu')
    if gungamelib.getVariableValue('gg_multikill') == 0:
        gungameLevelMenu.addline('->1. LEVEL') # Line #1
        gungameLevelMenu.addline('   * You are on level <level number>') # Line #2
        gungameLevelMenu.addline('   * You need a <weapon name> kill to advance') # Line #3
        gungameLevelMenu.addline('   * There currently is no leader') # Line #4
    else:
        gungameLevelMenu.addline('->1. LEVEL') # Line #1
        gungameLevelMenu.addline('   * You are on level <level number> (<weapon name>)') # Line #2
        gungameLevelMenu.addline('   * You have made #/# of your required kills') # Line #3
        gungameLevelMenu.addline('   * There currently is no leader') # Line #4
    if gungamelib.getVariableValue('gg_save_winners') > 0:
        gungameLevelMenu.addline('->2. WINS') # Line #5
        gungameLevelMenu.addline('   * You have won <player win count> time(s)') # Line #6
        gungameLevelMenu.addline('->3. LEADER(s)') # Line #7
        gungameLevelMenu.addline('   * Leader Level: There are no leaders') # Line #8
        gungameLevelMenu.addline('->   9. View Leaders Menu') # Line #9
    else:
        gungameLevelMenu.addline('->2. LEADER(s)') # Line #5
        gungameLevelMenu.addline('   * Leader Level: There are no leaders') # Line #6
        gungameLevelMenu.addline('->   9. View Leaders Menu') # Line #7
    gungameLevelMenu.submenu(9, 'gungameLeadersMenu')
    gungameLevelMenu.prepuser = prepGunGameLevelMenu
    gungameLevelMenu.timeout('send', 5)
    gungameLevelMenu.timeout('view', 5)

def prepGunGameLevelMenu(userid, popupid):
    gungameLevelMenu = popuplib.find('gungameLevelMenu')
    gungamePlayer = gungamelib.getPlayer(userid)
    if gungamelib.getVariableValue('gg_multikill') == 0:
        gungameLevelMenu.modline(2, '   * You are on level %d' %gungamePlayer['level']) # Line #2
        gungameLevelMenu.modline(3, '   * You need a %s kill to advance' %gungamePlayer.getWeapon()) # Line #3
    else:
        gungameLevelMenu.modline(2, '   * You are on level %d (%s)' %(gungamePlayer['level'], gungamePlayer.getWeapon())) # Line #2
        gungameLevelMenu.modline(3, '   * You have made %d/%d of your required kills' %(gungamePlayer.get('multikill'), gungamelib.getVariableValue('gg_multikill'))) # Line #3
    leaderLevel = gungamelib.getLeaderLevel()
    playerLevel = gungamePlayer['level']
    if leaderLevel > 1:
        # See if the player is a leader:
        if playerLevel == leaderLevel:
            # See if there is more than 1 leader
            if gungamelib.getCurrentLeaderCount() > 1:
                # This player is tied with other leaders
                gungameLevelMenu.modline(4, '   * You are currently tied for the leader position') # Line #4
            else:
                # This player is the only leader
                gungameLevelMenu.modline(4, '   * You are currently the leader') # Line #4
        # This player is not a leader
        else:
            levelsBehindLeader = leaderLevel - playerLevel
            if levelsBehindLeader == 1:
                gungameLevelMenu.modline(4, '   * You are 1 level behind the leader') # Line #4
            else:
                gungameLevelMenu.modline(4, '   * You are %d levels behind the leader' %levelsBehindLeader) # Line #4
    else:
        # There are no leaders
        gungameLevelMenu.modline(4, '   * There currently is no leader') # Line #4
    if gungamelib.getVariableValue('gg_save_winners') > 0:
        gungameLevelMenu.modline(6, '   * You have won %d time(s)' %12345) # Line #6
        if leaderLevel > 1:
            gungameLevelMenu.modline(8, '   * Leader Level: %d (%s)' %(leaderLevel, gungamelib.getLevelWeapon(leaderLevel))) # Line #8
        else:
            gungameLevelMenu.modline(8, '   * Leader Level: There are no leaders') # Line #8
    else:
        if leaderLevel > 1:
            gungameLevelMenu.modline(6, '   * Leader Level: %d (%s)' %(leaderLevel, gungamelib.getLevelWeapon(leaderLevel))) # Line #6
        else:
            gungameLevelMenu.modline(6, '   * Leader Level: There are no leaders') # Line #6

# GUNGAME LEADERS POPUP
gungameLeadersMenu = None

# Display the Level Popup to the player that requested it
def displayLeadersMenu():
    popuplib.send('gungameLeadersMenu', es.getcmduserid())

def buildLeaderMenu():
    # Check to see if the popup "gungameLevelMenu" exists
    if popuplib.exists('gungameLeadersMenu'):
        # The popup exists...let's unsend it
        popuplib.unsendname('gungameLeadersMenu', playerlib.getUseridList('#human'))
        # Now, we need to delete it
        popuplib.delete('gungameLeadersMenu')
    # Let's create the "gungameLeadersMenu" popup
    gungameLeadersMenu = popuplib.create('gungameLeadersMenu')
    gungameLeadersMenu.addline('->1. Current Leaders:')
    gungameLeadersMenu.addline('--------------------------')
    gungameLeadersMenu.addline('   * There currently is no leader')
    gungameLeadersMenu.addline('--------------------------')
    gungameLeadersMenu.addline('0. Exit')
    gungameLeadersMenu.timeout('send', 5)
    gungameLeadersMenu.timeout('view', 5)

def rebuildLeaderMenu():
    list_leaderNames = []
    
    for userid in gungamelib.getCurrentLeaderList():
        list_leaderNames.append(removeReturnChars(es.getplayername(userid)))
    # Check to see if the popup "gungameLevelMenu" exists
    if popuplib.exists('gungameLeadersMenu'):
        # The popup exists...let's unsend it
        popuplib.unsendname('gungameLeadersMenu', playerlib.getUseridList('#human'))
        # Now, we need to delete it
        popuplib.delete('gungameLeadersMenu')
    # Get leader level
    leaderLevel = gungamelib.getLeaderLevel()
    # Let's create the "gungameLeadersMenu" popup
    gungameLeadersMenu = popuplib.create('gungameLeadersMenu')
    gungameLeadersMenu.addline('->1. Current Leaders:')
    gungameLeadersMenu.addline('    Level %d (%s)' %(leaderLevel, gungamelib.getLevelWeapon(leaderLevel)))
    gungameLeadersMenu.addline('--------------------------')
    for leaderName in list_leaderNames:
        gungameLeadersMenu.addline('   * %s' %leaderName)
    gungameLeadersMenu.addline('--------------------------')
    gungameLeadersMenu.addline('0. Exit')
    gungameLeadersMenu.timeout('send', 5)
    gungameLeadersMenu.timeout('view', 5)
    
# ==========================================================================================================================
# ==========================================================================================================================
#          !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! END POPUPLIB COMMANDS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
# ==========================================================================================================================
# ==========================================================================================================================


# ==========================================================================================================================
# ==========================================================================================================================
#        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! BEGIN GUNGAME COMMANDS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
# ==========================================================================================================================
# ==========================================================================================================================

'''
# BEGIN ESS (OLDSCHOOL) COMMANDS
# ------------------------------------------------------
def ess_isafk():
    # gg_isafk <variable> <userid>
    if int(es.getargc()) == 3:
        userid = es.getargv(2)
        if es.exists('userid', userid):
            varName = es.getargv(1)
            gungamePlayer = gungamelib.getPlayer(userid)
            if gungamePlayer.get('isPlayerAfk'):
                es.set(varName,'1')
            else:
                es.set(varName,'0')
        else:
            raise UseridError, str(userid) + ' is an invalid userid'
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def ess_seteyeangle():
    # gg_seteyeangle <userid> <pitch> <yaw>
    if int(es.getargc()) == 4:
        userid = es.getargv(1)
        if es.exists('userid', userid):
            gungamePlayer = gungamelib.getPlayer(userid)
            gungamePlayer.set('eyeangle', es.getargv(2), es.getargv(3))
        else:
            raise UseridError, str(userid) + ' is an invalid userid'
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 3'

def ess_teleport():
    # gg_teleport <userid> <x> <y> <z> [pitch] [yaw]
    if int(es.getargc()) >= 5:
        userid = es.getargv(1)
        if es.exists('userid', userid):
            if int(es.getargc()) != 6:
                if int(es.getargc()) == 5:
                    gungame.teleportPlayer(userid, es.getargv(2), es.getargv(3), es.getargv(4))
                else:
                    gungame.teleportPlayer(userid, es.getargv(2), es.getargv(3), es.getargv(4), es.getargv(5), es.getargv(6))
            else:
                raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 4 or 6'
        else:
            raise UseridError, str(userid) + ' is an invalid userid'
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 4 or 6'

def ess_resetafk():
    # gg_resetafk <userid>
    if int(es.getargc()) == 2:
        userid = es.getargv(1)
        if es.exists('userid', userid):
            gungame.resetPlayerAfk(userid)
        else:
            raise UseridError, str(userid) + ' is an invalid userid'
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def ess_getlevel():
    # gg_getlevel <variable> <userid>
    if int(es.getargc()) == 3:
        userid = es.getargv(2)
        if es.exists('userid', userid):
            varName = es.getargv(1)
            gungamePlayer = gungamelib.getPlayer(userid)
            playerLevel = gungamePlayer['level']
            es.set(varName, playerLevel)
        else:
            raise UseridError, str(userid) + ' is an invalid userid'
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def ess_setlevel():
    # gg_setlevel <userid> <level>
    if int(es.getargc()) == 3:
        userid = es.getargv(1)
        if es.exists('userid', userid):
            varName = es.getargv(2)
            gungamePlayer = gungamelib.getPlayer(userid)
            gungamePlayer.set('level', es.getargv(2))
        else:
            raise UseridError, str(userid) + ' is an invalid userid'
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def ess_gungamelib.getLeaderLevel():
    # gg_gungamelib.getLeaderLevel <variable>
    if int(es.getargc()) == 2:
        varName = es.getargv(1)
        leaderLevel = gungame.gungamelib.getLeaderLevel()
        es.set(varName, leaderLevel)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def ess_getgungamevar():
    # gg_getgungamevar <variable> <variable name>
    if int(es.getargc()) == 3:
        varName = es.getargv(1)
        queriedVar = es.getargv(2)
        gungamelib.getVariableValue(varName)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'
        
def ess_setgungamevar():
    # gg_setgungamevar <variable name> <value>
    if int(es.getargc()) == 3:
        varName = es.getargv(1)
        varValue = es.getargv(2)
        gungamelib.setVariableValue(varName, varValue)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def ess_getpreventlevel():
    # gg_getpreventlevel <variable> <userid>
    if int(es.getargc()) == 3:
        varName = es.getargv(1)
        userid = es.getargv(2)
        gungamePlayer = gungamelib.getPlayer(userid)
        es.set(varName, gungamePlayer.get('preventlevel'))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'
        
def ess_setpreventlevel():
    # gg_setgungamevar <userid> <0 | 1>
    if int(es.getargc()) == 3:
        userid = es.getargv(1)
        preventValue = int(es.getargv(2))
        gungamePlayer = gungamelib.getPlayer(userid)
        gungamePlayer.set('preventlevel', preventValue)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def ess_stripplayer():
    # gg_stripplayer <userid>
    if int(es.getargc()) == 2:
        userid = es.getargv(1)
        if es.exists('userid', userid):
            stripPlayer(userid)
        else:
            raise UseridError, str(userid) + ' is an invalid userid'
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def ess_getweapon():
    # gg_getweapon <variable> <userid>
    if int(es.getargc()) == 3:
        userid = es.getargv(2)
        varName = es.getargv(1)
        gungamePlayer = gungamelib.getPlayer(userid)
        es.set(varName, dict_gungameWeaponOrder[gungamePlayer['level']])
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'
    
def ess_giveweapon():
    # gg_giveweapon <userid>
    if int(es.getargc()) == 2:
        userid = es.getargv(1)
        giveWeapon(userid)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def ess_gungamelib.getTotalLevels():
    if int(es.getargc()) == 2:
        varName = es.getargv(1)
        es.set(varName, gungamelib.getTotalLevels())
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def ess_setweapons():
    # gg_setweapons < #default | #random | #reversed >
    if int(es.getargc()) == 2:
        weaponOrder = es.getargv(1).lower()
        gungamelib.setVariableValue('gg_weapon_order', weaponOrder)
        setWeapons(weaponOrder)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def ess_setweaponorderfile():
    # gg_setweaponorderfile <Path to File>
    if int(es.getargc()) == 2:
        weaponOrderFile = es.getargv(1)
        gungamelib.setVariableValue('gg_weapon_order_file', weaponOrderFile)
        setWeaponOrderFile(gungamelib.getVariableValue('gg_weapon_order_file'))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'
        
def ess_registeraddon():
    #gg_registeraddon <Path to Script> <Script Name>
    if int(es.getargc()) == 3:
        registerAddon(str(es.getargv(1)), es.getargv(2))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def ess_unregisteraddon():
    #gg_unregisteraddon <Path to Script>
    global dict_gungameRegisteredAddons
    if int(es.getargc()) == 2:
        # addonName = es.getargv(1)
        unregisterAddon(str(es.getargv(1)))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def ess_getregisteredaddons():
    #gg_getregisteredaddons <variable>
    global dict_gungameRegisteredAddons
    if int(es.getargc()) == 2:
        keygroupName = es.getargv(1)
        if es.exists('keygroup', keygroupName):
            es.keygroupdelete(keygroupName)
        es.keygroupcreate(keygroupName)
        keygroup_registeredAddons = keyvalues.getKeyGroup(keygroupName)
        keygroup_registeredAddons['addons'] = keyvalues.KeyValues(name='addons')
        for addonName in dict_gungameRegisteredAddons:
            keygroup_registeredAddons['addons'][addonName] = dict_gungameRegisteredAddons[addonName]
            
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def ess_registerdependency():
    #gg_registerdependency <Path to Script> <Script Name>
    if int(es.getargc()) == 3:
        registerAddon(str(es.getargv(1)), es.getargv(2))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def ess_loadcustom():
    #gg_loadcustom <addonName>
    global dict_gungameRegisteredAddons
    if int(es.getargc()) == 2:
        # addonName = es.getargv(1)
        loadCustom(es.getargv(1))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def ess_unloadcustom():
    #gg_unloadcustom <addonName>
    global dict_gungameRegisteredAddons
    if int(es.getargc()) == 2:
        # addonName = es.getargv(1)
        unloadCustom(es.getargv(1))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'
# ---------------------------------------------------
# END ESS (OLDSCHOOL) COMMANDS
'''

# ===================================================================================================
# LOADING SHORTCUTS
# ===================================================================================================
def loadCustom(addonName):
    es.load('gungame/custom_addons/' + str(addonName))
    
def unloadCustom(addonName):
    es.unload('gungame/custom_addons/' + str(addonName))

# ===================================================================================================
# LEVEL UP AND DOWN TRIGGERING
# ===================================================================================================
def triggerLevelUpEvent(levelUpUserid, levelUpSteamid, levelUpName, levelUpTeam, levelUpOldLevel, levelUpNewLevel, victimUserid=0, victimName=None, weapon=None):
    # BEGIN THE EVENT CODE FOR INITIALIZING & FIRING EVENT "GG_LEVELUP"
    # -----------------------------------------------------------------------------------------------------------
    es.event('initialize', 'gg_levelup')
    # The userid of the player that levelled up
    es.event('setint', 'gg_levelup', 'userid', levelUpUserid)
    # The steamid of player that levelled up (provided by uniqueid)
    es.event('setstring', 'gg_levelup', 'steamid', levelUpSteamid)
    # The name of the player that levelled up
    es.event('setstring', 'gg_levelup', 'name', levelUpName)
    # The team # of the player that levelled up: team 2= Terrorists, 3= CT
    es.event('setstring', 'gg_levelup', 'team', levelUpTeam)                                
    # The old level of the player that levelled up
    es.event('setint', 'gg_levelup', 'old_level', levelUpOldLevel)
    # The new level of the player that levelled up
    es.event('setint', 'gg_levelup', 'new_level', levelUpNewLevel)
    # The userid of victim
    es.event('setint', 'gg_levelup', 'victim', victimUserid)
    # The victim's name
    es.event('setstring', 'gg_levelup', 'victimname', victimName)
    # The attackers weapon
    es.event('setstring', 'gg_levelup', 'weapon', weapon)
    # Fire the "GG_LEVELUP" event
    es.event('fire', 'gg_levelup')
    # --------------------------------------------------------------------------------------------------------
    # END THE EVENT CODE FOR INITIALIZING & FIRING EVENT "GG_LEVELUP"
    
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

def removeReturnChars(playerName):
    playerName = playerName.strip('\n')
    playerName = playerName.strip('\r')
    return playerName

def afkPunishCheck(userid):
    gungamePlayer = gungamelib.getPlayer(userid)
    afkMaxAllowed = gungamelib.getVariableValue('gg_afk_rounds')
    if afkMaxAllowed > 0:
        # Increment the "int_afk_rounds" for this player in the GunGame Core Dictionary
        gungamePlayer['afkrounds'] += 1
        # If they have been AFK for too many rounds, we proceed beyond the below check
        if gungamePlayer['afkrounds'] >= afkMaxAllowed:
            if gungamelib.getVariableValue('gg_afk_action') == 1:
                # Kick the player from the server for being AFK for the maximum number of rounds
                es.server.cmd('kickid %d \"AFK too long.\"' %userid)
            elif gungamelib.getVariableValue('gg_afk_action') == 2:
                # Set the player's team to spectator for being AFK for the maximum number of rounds
                es.server.cmd('es_xfire %d !self setteam 1' %userid)
                # POPUP!!! "You were switched to Spectator\n for being AFK!\n \n----------\n->0. Exit" 

def equipPlayer():
    userid = es.getuserid()
    es.server.cmd('es_xremove game_player_equip')
    es.server.cmd('es_xgive %s game_player_equip' %userid)
    es.server.cmd('es_xfire %s game_player_equip addoutput \"weapon_knife 1\"' %userid)
    
    # Retrieve the armor type
    armorType = gungamelib.getVariableValue('gg_player_armor')
    
    if armorType == 2:
    # Give the player full armor
        es.server.cmd('es_xfire %s game_player_equip addoutput \"item_assaultsuit 1\"' %userid)
    # Give the player kevlar only
    elif armorType == 1:
        es.server.cmd('es_xfire %s game_player_equip addoutput \"item_kevlar 1\"' %userid)

def levelInfoHudHint(userid):
    gungamePlayer = gungamelib.getPlayer(userid)

    leaderLevel = gungamelib.getLeaderLevel()
    # Get levels behind leader
    levelsBehindLeader = leaderLevel - gungamePlayer['level']
            
    # Get list of leaders userids
    list_leadersUserid = gungamelib.getCurrentLeaderList()
            
    multiKill = gungamelib.getLevelMultiKill(gungamePlayer['level'])
    
    if multiKill > 1:
        multiKillText = '\nRequired Kills: %d/%d' %(gungamePlayer['multikill'], multiKill)
    else:
        multiKillText = '\n'
            
    if leaderLevel < 2:
        HudHintText = 'Current level: %d of %d\nCurrent weapon: %s%s' %(gungamePlayer['level'], gungamelib.getTotalLevels(), gungamePlayer.getWeapon(), multiKillText)
    else:
        # Get levels behind leader
        levelsBehindLeader = leaderLevel - gungamePlayer['level']
        # Get list of leaders userids
        list_leadersUserid = gungamelib.getLevelUseridList(leaderLevel)
        
    # How many levels behind the leader?
    if levelsBehindLeader == 0:
        # Is there more than 1 leader?
        if gungamelib.getCurrentLeaderCount() == 1:    
            HudHintText = 'Current level: %d of %d\nCurrent weapon: %s%s\nYou are the leader.' % (gungamePlayer['level'], gungamelib.getTotalLevels(), gungamePlayer.getWeapon(), multiKillText)
        else:
            if leaderLevel != 1:
                HudHintText = 'Current level: %d of %d\nCurrent weapon: %s%s\nYou are amongst the leaders (' % (gungamePlayer['level'], gungamelib.getTotalLevels(), gungamePlayer.getWeapon(), multiKillText)
            else:
                HudHintText = 'Current level: %d of %d\nCurrent weapon: %s%s\nThere are no leaders' % (gungamePlayer['level'], gungamelib.getTotalLevels(), gungamePlayer.getWeapon(), multiKillText)
            leadersCount = 0
                    
            # Get the first 2 leaders
            for leader in list_leadersUserid:
                # Increment leader count
                leadersCount += 1
                        
                # More than 2 leaders added?
                if leadersCount == 3:
                    HudHintText += '...'
                    break
                        
                # Don't add the comma if there is 2 or less leaders
                if (len(list_leadersUserid) == 2 and leadersCount == 1) or (len(list_leadersUserid) == 1 and leadersCount == 0):
                    HudHintText += es.getplayername(leader)
                    break
                        
                # Don't add our userid
                if leader == userid:
                    continue
                        
                # Add the name to the hudhint and increment the leaders count
                HudHintText += es.getplayername(leader) + ', '
                    
                # Finish off the HudHint
                HudHintText += ')'
    else:
        HudHintText = 'Current level: %d of %d\nCurrent weapon: %s%s\nLeader (%s) level: %d of %d (%s)' %(gungamePlayer['level'], gungamelib.getTotalLevels(), gungamePlayer.getWeapon(), multiKillText, es.getplayername(list_leadersUserid[0]), gungamelib.getLeaderLevel(), gungamelib.getTotalLevels(), gungamelib.getLevelWeapon(gungamelib.getLeaderLevel()))
            
    if not int(gungamelib.getGlobal('voteActive')) and not int(gungamelib.getGlobal('isWarmup')):
        gamethread.delayed(0.5, usermsg.hudhint, (userid, HudHintText))

# ==========================================================================================================================
# ==========================================================================================================================
#          !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! END GUNGAME COMMANDS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
# ==========================================================================================================================
# ==========================================================================================================================


# ==========================================================================================================================
# ==========================================================================================================================
#             !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! BEGIN GAME EVENTS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
# ==========================================================================================================================
# ==========================================================================================================================
def load():
    StartProfiling(g_Prof)
    
    global dict_gungameWinners
    global countBombDeathAsSuicide
    
    # LOAD CUSTOM GUNGAME EVENTS
    es.loadevents('declare', 'addons/eventscripts/gungame/events/es_gungame_events.res')
    
    # Get the scripts in the "../cstrike/addons/eventscripts/gungame/included_addons" folder
    for includedAddon in os.listdir(os.getcwd() + '/cstrike/addons/eventscripts/gungame/included_addons/'):
        if includedAddon[0:3] == 'gg_':
            list_includedAddonsDir.append(includedAddon)
    
    # Get the scripts in the "../cstrike/addons/eventscripts/gungame/custom_addons" folder
    for customAddon in os.listdir(os.getcwd() + '/cstrike/addons/eventscripts/gungame/custom_addons/'):
        if customAddon[0:3] == 'gg_':
            list_customAddonsDir.append(customAddon)
    
    # Load the "../cstrike/cfg/gungame/gg_en_config.cfg"
    gungamelib.getConfig('gg_en_config.cfg')
    
    # Load the "../cstrike/cfg/gungame/gg_default_addons.cfg"
    gungamelib.getConfig('gg_default_addons.cfg')
    
    # Load the "../cstrike/cfg/gungame/gg_map_vote.cfg"
    gungamelib.getConfig('gg_map_vote.cfg')
        
    # See if we need to create a list of strip exceptions
    global list_stripExceptions
    if gungamelib.getVariableValue('gg_map_strip_exceptions') != 0:
        # Create a list of stripping exceptions using the 'gg_map_strip_exceptions' variable
        list_stripExceptions = gungamelib.getVariableValue('gg_map_strip_exceptions').split(',')
    
    # NEW NEW NEW
    weaponOrderINI  = ConfigParser.ConfigParser()
    gameDir         = es.ServerVar('eventscripts_gamedir')
    # Loop through the Weapon Order INI and register their information with GunGame
    weaponOrderINI.read('%s/cfg/gungame/gg_weapon_orders.ini' %gameDir)
    for weaponOrderName in weaponOrderINI.sections():
        weaponOrderFile = weaponOrderINI.get(weaponOrderName, 'fileName')
        myWeaponOrder = gungamelib.getWeaponOrderFile(weaponOrderFile)
        if weaponOrderINI.get(weaponOrderName, 'fileName') == gungamelib.getVariableValue('gg_weapon_order_file'):
            myWeaponOrder.setWeaponOrderFile()
            if gungamelib.getVariableValue('gg_weapon_order') != '#default':
                myWeaponOrder.changeWeaponOrderType(gungamelib.getVariableValue('gg_weapon_order'))
            if gungamelib.getVariableValue('gg_multikill') > 1:
                gungamelib.setMultiKillOverride(gungamelib.getVariableValue('gg_multikill'))
            myWeaponOrder.echo()
    
    
    '''
    # BEGIN ESS COMMAND REGISTRATION
    # -------------------------------------------------------
    
    # GG_ISAFK
    if not es.exists('command', 'gg_isafk'):
        es.regcmd('gg_isafk', 'gungame/ess_isafk', 'Queries to see if the player is AFK')
    # GG_SETEYEANGLE
    if not es.exists('command', 'gg_seteyeangle'):
        es.regcmd('gg_seteyeangle', 'gungame/ess_seteyeangle', 'Sets the specified userid angle of vision to pitch and yaw')
    # GG_TELEPORT
    if not es.exists('command', 'gg_teleport'):
        es.regcmd('gg_teleport', 'gungame/ess_teleport', 'Teleports the specified userid to x, y, z location')
    # GG_RESETAFK
    if not es.exists('command', 'gg_resetafk'):
        es.regcmd('gg_resetafk', 'gungame/ess_resetafk', 'Resets the afk location to the current position & eye angles')
    # GG_GETLEVEL
    if not es.exists('command', 'gg_getlevel'):
        es.regcmd('gg_getlevel', 'gungame/ess_getlevel', 'Retrieves the level of the selected player')
    # GG_SETLEVEL
    if not es.exists('command', 'gg_setlevel'):
        es.regcmd('gg_setlevel', 'gungame/ess_setlevel', 'Sets the level of the selected player')
    # GG_SETWEAPONS
    if not es.exists('command', 'gg_setweapons'):
        es.regcmd('gg_setweapons', 'gungame/ess_setweapons', 'Sets the weapon order for GunGame: #default, #reverse, #random')
    # GG_GETGUNGAMEVAR
    if not es.exists('command', 'gg_getgungamevar'):
        es.regcmd('gg_getgungamevar', 'gungame/ess_getgungamevar', 'Retrieves the value of the selected gungame variable')
    # GG_SETGUNGAMEVAR
    if not es.exists('command', 'gg_setgungamevar'):
        es.regcmd('gg_setgungamevar', 'gungame/ess_setgungamevar', 'Sets the value of the selected gungame variable')
    # GG_GETPREVENTLEVEL
    if not es.exists('command', 'gg_getpreventlevel'):
        es.regcmd('gg_getpreventlevel', 'gungame/ess_getpreventlevel', 'Retrieves the value of prevent level')
    # GG_SETPREVENTLEVEL
    if not es.exists('command', 'gg_setpreventlevel'):
        es.regcmd('gg_setpreventlevel', 'gungame/ess_setpreventlevel', 'Sets the value of prevent level')
    # GG_STRIPPLAYER
    if not es.exists('command', 'gg_stripplayer'):
        es.regcmd('gg_stripplayer', 'gungame/ess_stripplayer', 'Strips the player using Gungame\'s strip method')
    # GG_GETWEAPON
    if not es.exists('command', 'gg_getweapon'):
        es.regcmd('gg_getweapon', 'gungame/ess_getweapon', 'Retrieves the player\'s current level\'s weapon name')
    # GG_GIVEWEAPON
    if not es.exists('command', 'gg_giveweapon'):
        es.regcmd('gg_giveweapon', 'gungame/ess_giveweapon', 'Gives the player the weapon for their corresponding level')
    # GG_GETTOTALLEVELS
    if not es.exists('command', 'gg_gettotallevels'):
        es.regcmd('gg_gettotallevels', 'gungame/ess_gettotallevels', 'Returns the total number of levels in the GunGame database')
    # GG_gungamelib.getLeaderLevel
    if not es.exists('command', 'gg_gungamelib.getLeaderLevel'):
        es.regcmd('gg_gungamelib.getLeaderLevel', 'gungame/ess_gungamelib.getLeaderLevel', 'Returns the leader level')
    # GG_SETWEAPONORDERFILE
    if not es.exists('command', 'gg_setweaponorderfile'):
        es.regcmd('gg_setweaponorderfile', 'gungame/ess_setweaponorderfile', 'Sets the weapon order file that is used by GunGame')
    # GG_REGISTERADDON
    if not es.exists('command', 'gg_registeraddon'):
        es.regcmd('gg_registeraddon', 'gungame/ess_registeraddon', 'Registers addon with GunGame')
    # GG_UNREGISTERADDON
    if not es.exists('command', 'gg_unregisteraddon'):
        es.regcmd('gg_unregisteraddon', 'gungame/ess_unregisteraddon', 'Unregisters addon with GunGame')
    # GG_GETREGISTEREDADDONS
    if not es.exists('command', 'gg_getregisteredaddons'):
        es.regcmd('gg_getregisteredaddons', 'gungame/ess_getregisteredaddons', 'Retrieves a list of addons in a keygroup')
    #gg_LOADCUSTOM
    if not es.exists('command', 'gg_loadcustom'):
        es.regcmd('gg_loadcustom', 'gungame/ess_loadcustom', 'Loads an addon \'from gungame/custom_addons\'')
    #gg_UNLOADCUSTOM
    if not es.exists('command', 'gg_unloadcustom'):
        es.regcmd('gg_unloadcustom', 'gungame/ess_unloadcustom', 'Unloads an addon \'from gungame/custom_addons\'')

    # ---------------------------------------------------
    # END ESS COMMAND REGISTRATION
    '''
    # BEGIN POPUP COMMAND REGISTRATION
    # ----------------------------------------------------------
    
    # !WEAPONS
    if not es.exists('saycommand', '!weapons'):
        es.regsaycmd('!weapons', 'gungame/displayWeaponOrderMenu')
    if not es.exists('clientcommand', '!weapons'):
        es.regclientcmd('!weapons', 'gungame/displayWeaponOrderMenu')
    
    # !LEVEL
    buildLevelMenu()
    if not es.exists('saycommand', '!level'):
        es.regsaycmd('!level', 'gungame/displayLevelMenu')
    if not es.exists('clientcommand', '!level'):
        es.regclientcmd('!level', 'gungame/displayLevelMenu')
    
    # !LEADER / !LEADERS
    buildLeaderMenu()
    if not es.exists('saycommand', '!leader'):
        es.regsaycmd('!leader', 'gungame/displayLeadersMenu')
    if not es.exists('clientcommand', '!leader'):
        es.regclientcmd('!leader', 'gungame/displayLeadersMenu')
    
    if not es.exists('saycommand', '!leaders'):
        es.regsaycmd('!leaders', 'gungame/displayLeadersMenu')
    if not es.exists('clientcommand', '!leaders'):
        es.regclientcmd('!leaders', 'gungame/displayLeadersMenu')
    # -------------------------------------------------------
    # END POPUP COMMAND REGISTRATION
    if gungamelib.getVariableValue('gg_save_winners') > 0:
        # BEGIN CREATE WINNERSDATA.DB and LOAD INTO DICT_GUNGAMEWINNERS
        # -------------------------------------------------------------------------------------------------------------
        # Set a variable for the path of the winner's database
        winnersDataBasePath = es.getAddonPath('gungame') + '/data/winnersdata.db'
        # See if the "..cstrike/addons/eventscripts/gungame/data/winnerdata.db" exists...
        if not os.path.isfile(winnersDataBasePath):
            # Open the "../cstrike/addons/eventscripts/gungame/data/winnersdata.db"
            winnersDataBaseFile = open(winnersDataBasePath, 'w')
            # Place the contents of dict_gungameWinners in the "../cstrike/addons/eventscripts/gungame/data/winnersdata.db"
            cPickle.dump(dict_gungameWinners, winnersDataBaseFile)
            # Close the "../cstrike/addons/eventscripts/gungame/data/winnersdata.db", saving the changes
            winnersDataBaseFile.close()
        # Open the "..cstrike/addons/eventscripts/gungame/data/winnerdata.db" file
        winnersDataBaseFile = open(winnersDataBasePath, 'r')
        # Load the winners database file into dict_gungameWinners via pickle
        dict_gungameWinners = cPickle.load(winnersDataBaseFile)
        # Close the winners database file
        winnersDataBaseFile.close()
        # ----------------------------------------------------------------------------------------------------------
        # END CREATE WINNERSDATA.DB and LOAD INTO DICT_GUNGAMEWINNERS
    
    # Set Up Active Players
    gungamelib.resetGunGame()
    
    # Reset the leader names list
    list_leaderNames = []
    
    # Set Up a custom variable for voting in dict_gungameVariables
    dict_gungameVariables['gungame_voting_started'] = False

    # If there is a current map listed, then the admin has loaded GunGame mid-round/mid-map
    if str(es.ServerVar('eventscripts_currentmap')) != '':
        # Check to see if the warmup round needs to be activated
        if gungamelib.getVariableValue('gg_warmup_timer') > 0:
            es.load('gungame/included_addons/gg_warmup_round')
        else:
            # Fire gg_start event
            es.event('initialize','gg_start')
            es.event('fire','gg_start')
    
    # RESTART CURRENT MAP
    es.server.cmd('mp_restartgame 2')
    es.msg('#multi', '\x04[\x03GunGame\x04]\x01 Loaded')
    
    # Split the map name into a list separated by "_"
    list_mapPrefix = str(es.ServerVar('eventscripts_currentmap')).split('_')
    
    # Insert the new map prefix into the GunGame Variables
    gungamelib.setGlobal('gungame_currentmap_prefix', list_mapPrefix[0])

    # Create a variable to prevent bomb explosion deaths from counting a suicides
    countBombDeathAsSuicide = False
    
    # Load gg_sounds
    gungamelib.getSoundPack(gungamelib.getVariableValue('gg_soundpack'))
    
    # Fire gg_load event
    es.event('initialize','gg_load')
    es.event('fire','gg_load')
    StopProfiling(g_Prof)
    #es.msg("Load benchmark: %f seconds" % GetProfilerTime(g_Prof))

def es_map_start(event_var):
    #Load custom GunGame events
    es.loadevents('declare', 'addons/eventscripts/gungame/events/es_gungame_events.res')
    
    # Execute GunGame's autoexec.cfg
    es.server.cmd('es_xdelayed 1 exec gungame/autoexec.cfg')
    
    # Split the map name into a list separated by "_"
    list_mapPrefix = event_var['mapname'].split('_')
    
    # Insert the new map prefix into the GunGame Variables
    gungamelib.setGlobal('gungame_currentmap_prefix', list_mapPrefix[0])
    
    # Reset the "gungame_voting_started" variable
    gungamelib.setVariableValue('gungame_voting_started', False)
    
    
    # See if the option to randomize weapons is turned on
    if gungamelib.getVariableValue('gg_weapon_order') == '#random':
        # Randomize the weapon order
        myWeaponOrder = gungamelib.getWeaponOrderFile(gungamelib.getCurrentWeaponOrderFile())
        myWeaponOrder.changeWeaponOrderType('#random')
    
    # Check to see if the warmup round needs to be activated
    if gungamelib.getVariableValue('gg_warmup_timer') > 0:
        es.load('gungame/included_addons/gg_warmup_round')
    else:
        # Fire gg_start event
        es.event('initialize','gg_start')
        es.event('fire','gg_start')
    
    # Reset the GunGame Round
    gungamelib.resetGunGame()
    es.msg('Leader Level = %d' %gungamelib.getLeaderLevel())
    es.msg(gungamelib.getCurrentLeaderList())
    
    # Reset the leader names list
    list_leaderNames = []

def player_changename(event_var):
    # Change the player's name in the leaderlist
    if removeReturnChars(event_var['oldname']) in list_leaderNames:
        list_leaderNames[list_leaderNames.index(event_var['oldname'])] = removeReturnChars(event_var['newname'])

def round_start(event_var):
    StartProfiling(g_Prof)
    global list_stripExceptions
    global list_allWeapons
    global countBombDeathAsSuicide
    
    # Create a variable to prevent bomb explosion deaths from counting a suicides
    countBombDeathAsSuicide = False
    
    # Disable Buyzones
    userid = es.getuserid()
    es.server.cmd('es_xfire %d func_buyzone disable' %userid)
    
    # REMOVE WEAPONS BUILT INTO THE MAP
    # Loop through all weapons
    for weapon in list_allWeapons:
        # Make sure that the admin doesn't want the weapon left on the map
        if weapon not in list_stripExceptions:
            # Remove the weapon from the map
            es.server.cmd('es_xfire %d weapon_%s kill' %(userid, weapon))
    
    # Set up the "game_player_equip" entity to auto-strip the players for us
    equipPlayer()

    # Check to see if objectives need to be enabled/disabled
    mapObjectives = gungamelib.getVariableValue('gg_map_obj')
    
    # Get the map prefix for the following checks
    mapPrefix = gungamelib.getGlobal('gungame_currentmap_prefix')
    
    # If both the BOMB and HOSTAGE objectives are enabled, we don't do anything else
    if mapObjectives < 3:
        # If ALL Objectives are DISABLED
        if mapObjectives == 0:
            # Since objectives are disabled, if this is a "de_" map, we disable only BOMB Objectives
            if mapPrefix == 'de':
                # Disable the bomb zones
                es.server.cmd('es_xfire %d func_bomb_target Disable' %userid)
                # Kill/remove the C4
                es.server.cmd('es_xfire %d weapon_c4 Kill' %userid)
            # Since objectives are disabled, if this is a "cs_" map, we disable only HOSTAGE Objectives
            elif mapPrefix == 'cs':
                # Disable the ability to rescue hostages
                es.server.cmd('es_xfire %d func_hostage_rescue Disable' %userid)
                # Remove the hostages from the map
                es.server.cmd('es_xfire %d hostage_entity Kill' %userid)
        # If only the HOSTAGE Objective is enabled
        elif mapObjectives == 1:
            # Since the BOMB objective is disabled, if this is a "de_" map, we disable only BOMB Objectives
            if mapPrefix == 'de':
                # Disable the bomb zones
                es.server.cmd('es_xfire %d func_bomb_target Disable' %userid)
                # Kill/remove the C4
                es.server.cmd('es_xfire %d weapon_c4 Kill' %userid)
        # If only the BOMB Objective is enabled
        elif mapObjectives == 2:
            # Since the HOSTAGE objective is disabled, if this is a "cs_" map, we disable only HOSTAGE Objectives
            if mapPrefix == 'cs':
                # Disable the ability to rescue hostages
                es.server.cmd('es_xfire %d func_hostage_rescue Disable' %userid)
                # Remove the hostages from the map
                es.server.cmd('es_xfire %d hostage_entity Kill' %userid)
    StopProfiling(g_Prof)
    #es.msg("Event round_start benchmark: %f seconds" % GetProfilerTime(g_Prof))

def round_freeze_end(event_var):
    global countBombDeathAsSuicide
    
    # Create a variable to prevent bomb explosion deaths from counting a suicides
    countBombDeathAsSuicide = True

def round_end(event_var):
    StartProfiling(g_Prof)
    global countBombDeathAsSuicide
    
    # Create a variable to prevent bomb explosion deaths from counting a suicides
    countBombDeathAsSuicide = False
    
    # Set up the "game_player_equip" entity to auto-strip the players for us
    equipPlayer()
    
    # Make sure we don't count them as AFK if there was a ROUND_DRAW or GAME_COMMENCING reason code
    if int(event_var['reason']) != 10 and int(event_var['reason']) != 16:
        # Let's be proactive and see if any of the alive players were AFK if "gg_afk_rounds" is enabled
        if gungamelib.getVariableValue('gg_afk_rounds') > 0:
            # Create a list of userids of human players that were alive at the end of the round
            list_playerlist = playerlib.getUseridList('#alive,#human')
            # Now, we will loop through the userid list and run the AFK Punishment Checks on them
            for userid in list_playerlist:
                gungamePlayer = gungamelib.getPlayer(userid)
                # Check to see if the player was AFK
                if gungamePlayer.isPlayerAFK():
                    # See if the player needs to be punished for being AFK
                    afkPunishCheck(int(userid))
    StopProfiling(g_Prof)
    #es.msg("Event round_end benchmark: %f seconds" % GetProfilerTime(g_Prof))

def player_activate(event_var):
    StartProfiling(g_Prof)
    global dict_gungameWinners
    userid = int(event_var['userid'])
    
    gungamePlayer = gungamelib.getPlayer(userid)
    steamid = gungamePlayer['steamid']
    
    # See if the player has won before
    if gungamelib.getVariableValue('gg_save_winners') > 0:
        if dict_gungameWinners.has_key(steamid):
            # Yes, they have won before...let's be nice and update their timestamp
            dict_gungameWinners[steamid].int_timestamp = es.gettime()
    
    
    # See if this player was set up in the Reconnecting Players Dictionary
    if dict_reconnectingPlayers.has_key(steamid):
        # Yes, they were. Therefore, we set their level to be whatever it needs to be
        gungamePlayer['level'] = dict_reconnectingPlayers[steamid]
        # Delete the player from the Reconnecting Players Dictionary
        del dict_reconnectingPlayers[steamid]
    
    StopProfiling(g_Prof)
    #es.msg("Event player_activate benchmark: %f seconds" % GetProfilerTime(g_Prof))
    
def player_disconnect(event_var):
    StartProfiling(g_Prof)
    global dict_reconnectingPlayers
    userid = int(event_var['userid'])
    
    gungamePlayer = gungamelib.getPlayer(userid)
    steamid = gungamePlayer['steamid']
    
    # Make sure the player is not a BOT
    if 'BOT' not in steamid:
        # See if this player is already in the Reconnecting Players Dictionary (shouldn't ever be, but we will check anyhow, just to be safe)
        if not dict_reconnectingPlayers.has_key(steamid):
            # Set this player up in the Reconnecting Players Dictionary
            reconnectLevel = gungamePlayer['level'] - gungamelib.getVariableValue('gg_retry_punish')
            if reconnectLevel > 0:
                dict_reconnectingPlayers[steamid] = reconnectLevel
            else:
                dict_reconnectingPlayers[steamid] = 1
    gungamePlayer.removePlayer()
    
    StopProfiling(g_Prof)
    #es.msg("Event player_disconnect benchmark: %f seconds" % GetProfilerTime(g_Prof))

def player_spawn(event_var):
    StartProfiling(g_Prof)
    userid = int(event_var['userid'])
    
    gungamePlayer = gungamelib.getPlayer(userid)
        
    if int(event_var['es_userteam']) > 1:
        # Reset the player's location with GunGame's AFK Checker
        gamethread.delayed(0.6, gungamePlayer.resetPlayerLocation, ())
        
        # Strip the player
        '''
        if gungamelib.getVariableValue('gg_deathmatch'):
            gungamePlayer.stripPlayer()
        '''
        
        # Check to see if the WarmUp Round is Active
        if not dict_gungameRegisteredAddons.has_key('gg_warmup_round'):
            # Since the WarmUp Round is not Active, give the player the weapon relevant to their level
            gungamePlayer.giveWeapon()
            
            levelInfoHudHint(userid)
            
        if gungamelib.getVariableValue('gg_map_obj') > 1:
            # Check to see if this player is a CT
            if int(event_var['es_userteam']) == 3:
                # Check to see if the map is a "de_*" map
                if gungamelib.getGlobal('gungame_currentmap_prefix') == 'de':
                    # See if the admin wants us to give them a defuser
                    if gungamelib.getVariableValue('gg_player_defuser') > 0:
                        playerlibPlayer = playerlib.getPlayer(userid)
                            
                        # Make sure the player doesn't already have a defuser
                        if not playerlibPlayer.get('defuser'):
                            es.server.cmd('es_xgive %d item_defuser' %userid)

    StopProfiling(g_Prof)
    #es.msg("Event player_spawn benchmark: %f seconds" % GetProfilerTime(g_Prof))

def player_jump(event_var):
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Is player human?
    if not es.isbot(userid):
        # Here, we will make sure that the player isn't counted as AFK
        gungamePlayer.playerNotAFK()

def player_death(event_var):
    StartProfiling(g_Prof)
    global countBombDeathAsSuicide
    
    # Set vars
    userid = int(event_var['userid'])
    gungameVictim = gungamelib.getPlayer(userid)
    attacker = int(event_var['attacker'])
    
    # If the attacker is not "world"
    if attacker != 0:
        gungameAttacker = gungamelib.getPlayer(attacker)
        # If the attacker is not on the same team
        if int(event_var['es_userteam']) != int(event_var['es_attackerteam']):
            # If the weapon is the correct weapon
            weapon = event_var['weapon']
            if weapon == gungameAttacker.getWeapon():
                # If the victim was not AFK
                if not gungameVictim.isPlayerAFK():
                    # Make sure that PreventLevel is not set to "1"
                    if int(gungameAttacker['preventlevel']) == 0:
                        # If multikill is active we need to set up for it
                        multiKill = gungamelib.getLevelMultiKill(gungameAttacker['level'])
                        if multiKill > 1:
                        
                            if weapon == 'knife' or weapon == 'hegrenade':
                                if gungamelib.getVariableValue('gg_multikill'):
                                    gungameAttacker['multikill'] = gungamelib.getVariableValue('gg_multikill')
                                
                            else:
                                gungameAttacker['multikill'] += 1
                                
                            if gungameAttacker['multikill'] == multiKill:
                                levelUpOldLevel = gungameAttacker['level']
                                levelUpNewLevel = levelUpOldLevel + 1
                                
                                # triggerLevelUpEvent(levelUpUserid, levelUpSteamid, levelUpName, levelUpTeam, levelUpOldLevel, levelUpNewLevel, victimUserid, victimName)
                                triggerLevelUpEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelUpOldLevel, levelUpNewLevel, userid, event_var['es_username'])
                                gungameAttacker['multikill'] = 0
                            else:
                                # Message the Attacker
                                usermsg.hudhint(attacker, 'Kills this level: %d of %d' %(gungameAttacker['multikill'], multiKill))
                                # Message the victim:
                                multiKill = gungamelib.getLevelMultiKill(gungameVictim['level'])
                                usermsg.hudhint(userid, 'Kills this level: %d of %d' %(gungameVictim['multikill'], multiKill))
                                
                        # Multikill was not active
                        else:
                            levelUpOldLevel = gungameAttacker['level']
                            levelUpNewLevel = levelUpOldLevel + 1
                            
                            # triggerLevelUpEvent(levelUpUserid, levelUpSteamid, levelUpName, levelUpTeam, levelUpOldLevel, levelUpNewLevel, victimUserid, victimName)
                            triggerLevelUpEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelUpOldLevel, levelUpNewLevel, userid, event_var['es_username'])
                            
                # The victim was AFK
                else:
                    usermsg.hudhint(attacker, '%s was AFK\nYour kill did not count!!!' %event_var['es_username'])
                    
                    # Check to see if AFK punishment is active
                    if gungamelib.getVariableValue('gg_afk_rounds') > 0:
                        # BOTs are never AFK
                        if not es.isbot(userid):
                            # Run the AFK punishment code
                            afkPunishCheck(userid)            
        # Must be a team kill or a suicide...let's see, shall we?
        else:
            # Check to see if the player was suicidal
            if userid == attacker:
                # Yep! They killed themselves. Now let's see if we are going to punish the dead...
                if gungamelib.getVariableValue('gg_suicide_punish') > 0:
                    # Set vars
                    levelDownOldLevel = int(gungameAttacker['level'])
                    levelDownNewLevel = levelDownOldLevel - gungamelib.getVariableValue('gg_suicide_punish')
                    
                    # Let's not put them on a non-existant level 0...
                    if levelDownNewLevel > 0:
                        # LEVEL DOWN CODE
                        triggerLevelDownEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelDownOldLevel, levelDownNewLevel, userid, event_var['es_username'])
                        
                    else:
                        triggerLevelDownEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelDownOldLevel, 1, userid, event_var['es_username'])
            # Team Killer!!!
            else:
                # Let's see if we get to punish the vile TK'er...
                if gungamelib.getVariableValue('gg_tk_punish') > 0:
                    # Set vars
                    levelDownOldLevel = gungameAttacker['level']
                    levelDownNewLevel = levelDownOldLevel - gungamelib.getVariableValue('gg_tk_punish')
                    
                    # Let's not put them on a non-existant level 0...
                    if levelDownNewLevel > 0:
                        triggerLevelDownEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelDownOldLevel, levelDownNewLevel, userid, event_var['es_username'])
                        
                    else:
                        triggerLevelDownEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelDownOldLevel, 1, userid, event_var['es_username'])
    else:
        # Killed by "world"
        gungameAttacker = gungamelib.getPlayer(userid)
        
        if gungamelib.getVariableValue('gg_suicide_punish') > 0:
            # Make sure that the explosion of the bomb doesn't count as a suicide to punish
            if countBombDeathAsSuicide:
                # Set vars
                levelDownOldLevel = gungameAttacker['level']
                levelDownNewLevel = levelDownOldLevel - gungamelib.getVariableValue('gg_suicide_punish')
                
                # Let's not put them on a non-existant level 0...
                if levelDownNewLevel > 0:
                    # LEVEL DOWN CODE
                    triggerLevelDownEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_attackername'], event_var['es_userteam'], levelDownOldLevel, levelDownNewLevel, userid, event_var['es_username'])
    StopProfiling(g_Prof)
    #es.msg("Event player_death benchmark: %f seconds" % GetProfilerTime(g_Prof))
    
def bomb_defused(event_var):
    ## TODO: Should we put in an option to allow them to skip these levels by defusing?
    
    # Set vars
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    playerWeapon = gungamePlayer.getWeapon()
    
    # Cant skip the last level
    if int(gungamePlayer['level']) == int(gungamelib.getTotalLevels()) or playerWeapon == 'knife' or playerWeapon == 'hegrenade':
        es.tell(userid, '#multi', 'You can not skip the \4%s\1 level by defusing the bomb!' % playerWeapon)
    
    # Level them up
    levelUpOldLevel = gungamePlayer['level']
    levelUpNewLevel = levelUpOldLevel + 1
    triggerLevelUpEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_username'], event_var['es_userteam'], levelUpOldLevel, levelUpNewLevel, '0', '0')

def bomb_exploded(event_var):
    # Set vars
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    playerWeapon = gungamePlayer.getWeapon()
    
    # Cant skip the last level
    if int(gungamePlayer['level']) == int(gungamelib.getTotalLevels()) or playerWeapon == 'knife' or playerWeapon == 'hegrenade':
        es.tell(userid, '#multi', 'You can not skip the \4%s\1 level by planting the bomb!' % playerWeapon)
    
    # Level them up
    levelUpOldLevel = gungamePlayer['level']
    levelUpNewLevel = levelUpOldLevel + 1
    triggerLevelUpEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_username'], event_var['es_userteam'], levelUpOldLevel, levelUpNewLevel, '0', '0')

def gg_levelup(event_var):
    # Check for a winner first
    if int(event_var['old_level']) == gungamelib.getTotalLevels():
        es.event('initialize', 'gg_win')
        es.event('setint', 'gg_win', 'userid', event_var['userid'])
        es.event('setint', 'gg_win', 'loser', event_var['victim'])
        es.event('setstring', 'gg_win', 'steamid', event_var['steamid'])
        es.event('setint', 'gg_win', 'team', event_var['team'])
        es.event('setstring', 'gg_win', 'name', event_var['name'])
        es.event('fire', 'gg_win')
    # No winner...so sad. Let's continue with the regular levelup code.
    else:
        # BEGIN REGULAR LEVELUP CODE
        # --------------------------------------------
        userid = int(event_var['userid'])
        gungamePlayer = gungamelib.getPlayer(userid)
        # Set the player's level in the GunGame Core Dictionary
        gungamePlayer['level'] = int(event_var['new_level'])
        # Reset the player's multikill in the GunGame Core Dictionary
        gungamePlayer['multikill'] = 0
        # -----------------------------------------
        # END REGULAR LEVELUP CODE
        
        leaderLevel = gungamelib.getLeaderLevel()
        if leaderLevel == int(event_var['new_level']):
            rebuildLeaderMenu()

        if not dict_gungameRegisteredAddons.has_key('gg_warmup_round'):
            levelInfoHudHint(userid)
        
        # BEGIN CODE FOR TRIGGERING CUSTOM EVENT "GG_VOTE"
        # ----------------------------------------------------------------------------------
        if leaderLevel == gungamelib.getTotalLevels() - gungamelib.getVariableValue('gg_vote_trigger'):
            # Only continue if no other script has set the next map
            if es.ServerVar('eventscripts_nextmapoverride') == '':
                if not gungamelib.getVariableValue('gungame_voting_started'):
                    es.event('initialize', 'gg_vote')
                    es.event('fire', 'gg_vote')
            else:
                es.dbgmsg(0, '[GunGame] - Map vote failed because eventscripts_nextmapoverride was previously set by another script.')
        # ----------------------------------------------------------------------------------
        # END CODE FOR TRIGGERING CUSTOM EVENT "GG_VOTE"

def gg_leveldown(event_var):
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Set the player's level in the GunGame Core Dictionary
    gungamePlayer['level'] = int(event_var['new_level'])
            
def gg_new_leader(event_var):
    for playerID in es.getUseridList():
        usermsg.saytext2(playerID, event_var['es_userindex'], '\3%s\1 is now leading on level \4%d' %(es.getplayername(event_var['userid']), gungamelib.getLeaderLevel()))
    rebuildLeaderMenu()
    
def gg_tied_leader(event_var):
    leaderCount = gungamelib.getCurrentLeaderCount()
    if leaderCount == 2:
        # Loop through the players and send a saytext2 message
        for playerID in es.getUseridList():
            usermsg.saytext2(playerID, event_var['es_userindex'], '\4[2-way tie]\3 %s\1 has tied the other leader on level \4%d' % (es.getplayername(event_var['userid']), gungamelib.getLeaderLevel()))
    # There are more than 2 leaders
    elif leaderCount > 2:
        # Loop through the players and send a saytext2 message
        for playerID in es.getUseridList():
            usermsg.saytext2(playerID, event_var['es_userindex'], '\4[%d-way tie]\3 %s\1 has tied the other leaders on level \4%d' % (leaderCount, es.getplayername(event_var['userid']), gungamelib.getLeaderLevel()))

    rebuildLeaderMenu()
    
def gg_leader_lostlevel(event_var):
    rebuildLeaderMenu()
    
def unload():
    global gungameWeaponOrderMenu
    #popuplib.delete('gungameWeaponOrderMenu.delete()
    global dict_gungameRegisteredAddons
    for addonName in gungamelib.getRegisteredAddonlist():
        if addonName in list_includedAddonsDir:
            es.unload('gungame/included_addons/%s' %addonName)
        elif addonName in list_customAddonsDir:
            es.unload('gungame/custom_addons/%s' %addonName)
        
    # Enable Buyzones
    userid = es.getuserid()
    es.server.cmd('es_xfire %d func_buyzone Enable' %userid)
    
    # Check to see if objectives need to be enabled/disabled
    mapObjectives = gungamelib.getVariableValue('gg_map_obj')
    
    # Get the map prefix for the following checks
    mapPrefix = gungamelib.getGlobal('gungame_currentmap_prefix')
    
    # If both the BOMB and HOSTAGE objectives were enabled, we don't do anything else
    if mapObjectives < 3:
        # If ALL Objectives were DISABLED
        if mapObjectives == 0:
            # Since objectives were disabled, if this is a "de_" map, we enable only BOMB Objectives
            if mapPrefix == 'de':
                # Enable the bomb zones
                es.server.cmd('es_xfire %d func_bomb_target Enable' %userid)
            # Since objectives were disabled, if this is a "cs_" map, we enable only HOSTAGE Objectives
            elif mapPrefix == 'cs':
                # Enable the ability to rescue hostages
                es.server.cmd('es_xfire %d func_hostage_rescue Enable' %userid)
        # If only the HOSTAGE Objective was enabled
        elif mapObjectives == 1:
            # Since the BOMB objective was disabled, if this is a "de_" map, we enable only BOMB Objectives
            if mapPrefix == 'de':
                # Disable the bomb zones
                es.server.cmd('es_xfire %d func_bomb_target Enable' %userid)
        # If only the BOMB Objective was enabled
        elif mapObjectives == 2:
            # Since the HOSTAGE objective was disabled, if this is a "cs_" map, we enable only HOSTAGE Objectives
            if mapPrefix == 'cs':
                # Enable the ability to rescue hostages
                es.server.cmd('es_xfire %d func_hostage_rescue Enable' %userid)
    
    # Unregister all GunGame Say and Client Commands
    if es.exists('saycommand', '!weapons'):
        es.unregsaycmd('!weapons')
        
    if es.exists('clientcommand', '!weapons'):
        es.unregclientcmd('!weapons')
        
    if es.exists('saycommand', '!leader'):
        es.unregsaycmd('!leader')
        
    if es.exists('clientcommand', '!leader'):
        es.unregclientcmd('!leader')
        
    if es.exists('saycommand', '!leaders'):
        es.unregsaycmd('!leaders')
        
    if es.exists('clientcommand', '!leaders'):
        es.unregclientcmd('!leaders')
        
    # Unload gg_sounds
    # es.unload('gungame/included_addons/gg_sounds')
    
    # Fire gg_unload event
    es.event('initialize','gg_unload')
    es.event('fire','gg_unload')
    
    # Remove the notify flag from all GunGame Console Variables
    list_gungameVariables = gungamelib.getVariableList()
    for variable in list_gungameVariables:
        es.ServerVar(variable).removeFlag('notify')
        
    gungamelib.clearGunGame()

def gg_vote(event_var):
    gungamelib.setVariableValue('gungame_voting_started', True)
    if gungamelib.getVariableValue('gg_map_vote') == 2:
        es.server.cmd('ma_voterandom end %s' %gungamelib.getVariableValue('gg_map_vote_size'))

def gg_win(event_var):
    global dict_gungameWinners
    global countBombDeathAsSuicide
    
    userid = int(event_var['userid'])
    playerName = event_var['name']
    steamid = event_var['steamid']

    # Create a variable to prevent bomb explosion deaths from counting a suicides
    countBombDeathAsSuicide = False
    
    # End the GunGame Round
    es.server.cmd('es_xgive %d game_end' %userid)
    es.server.cmd('es_xfire %d game_end EndGame' %userid)
    
    # Enable alltalk
    es.server.cmd('sv_alltalk 1')
    
    # SayText2 the message to the world
    for pUserid in playerlib.getUseridList('#all'):
        gungamePlayer = gungamelib.getPlayer(pUserid)
        # Reset Players in the GunGame Core Database
        gungamePlayer.resetPlayer()
        usermsg.saytext2(pUserid, event_var['es_userindex'], '\3%s\1 won the game!' % playerName)
    
    # Now centermessage it
    es.centermsg('%s won!' %playerName)
    gamethread.delayed(2, es.centermsg, ('%s won!' %playerName))
    gamethread.delayed(4, es.centermsg, ('%s won!' %playerName))
    
    if gungamelib.getVariableValue('gg_save_winners') > 0:
        # See if the player has won before
        if not dict_gungameWinners.has_key(steamid):
            # Ah, we have a new winner! Let's add them to the database
            dict_gungameWinners[steamid] = gungameWinners()
        else:
            # Increment the win count
            dict_gungameWinners[steamid].int_wins += 1
        winnersDataBasePath = es.getAddonPath('gungame') + '/data/winnersdata.db'
        # Place the contents of dict_gungameWinners in the "../cstrike/addons/eventscripts/gungame/data/winnersdata.db"
        winnersDataBaseFile = open(winnersDataBasePath, 'w')
        # Place the contents of dict_gungameWinners in the "../cstrike/addons/eventscripts/gungame/data/winnersdata.db"
        cPickle.dump(dict_gungameWinners, winnersDataBaseFile)
        # Close the "../cstrike/addons/eventscripts/gungame/data/winnersdata.db", saving the changes
        winnersDataBaseFile.close()


def server_cvar(event_var):
    cvarName = event_var['cvarname']
    newValue = event_var['cvarvalue']
    
    if cvarName not in gungamelib.getVariableList():
        return
    
    # I had to remove this because server_cvar was not triggering.
    # However, the line below: if str(gungamelib.getVariableValue(cvarName)) != newValue: ... should take care of it
    '''
    if newValue == str(gungamelib.getVariableValue(cvarName)):
        return
    '''
    
    if cvarName in gungamelib.getDependencyList():
        if newValue != gungamelib.getDependencyValue(cvarName):
            es.dbgmsg(0, '[GunGame] %s is a protected dependency' %cvarName)
            if str(gungamelib.getVariableValue(cvarName)) != newValue:
                gungamelib.setVariableValue(cvarName, gungamelib.getVariableValue(cvarName))
            return
            
    if str(gungamelib.getVariableValue(cvarName)) != newValue:
        gungamelib.setVariableValue(cvarName, newValue)
    
    # GG_MAPVOTE
    if cvarName == 'gg_map_vote':
        if newValue == '1' and not dict_gungameRegisteredAddons.has_key('gg_map_vote'):
            es.server.queuecmd('es_load gungame/included_addons/gg_map_vote')
        elif newValue != '1' and dict_gungameRegisteredAddons.has_key('gg_map_vote'):
            es.unload('gungame/included_addons/gg_map_vote')
    # GG_NADE_BONUS
    elif cvarName == 'gg_nade_bonus':
        if newValue != '0' and newValue != 'knife' and newValue in list_allWeapons:
            es.server.queuecmd('es_load gungame/included_addons/gg_nade_bonus')
        elif newValue == '0' and dict_gungameRegisteredAddons.has_key('gg_nade_bonus'):
            es.unload('gungame/included_addons/gg_nade_bonus')
    # GG_SPAWN_PROTECTION
    elif cvarName == 'gg_spawn_protect':
        if int(newValue) > 0 and not dict_gungameRegisteredAddons.has_key('gg_spawn_protect'):
            es.server.queuecmd('es_load gungame/included_addons/gg_spawn_protect')
        elif newValue == '0' and dict_gungameRegisteredAddons.has_key('gg_spawn_protect'):
            es.unload('gungame/included_addons/gg_spawn_protect')
    # GG_FRIENDLYFIRE
    elif cvarName == 'gg_friendlyfire':
        if int(newValue) > 0 and not dict_gungameRegisteredAddons.has_key('gg_friendlyfire'):
            es.server.queuecmd('es_load gungame/included_addons/gg_friendlyfire')
        elif newValue == '0' and dict_gungameRegisteredAddons.has_key('gg_friendlyfire'):
            es.unload('gungame/included_addons/gg_friendlyfire')
    # All other included addons
    elif cvarName in list_includedAddonsDir:
        if newValue == '1':
            es.server.queuecmd('es_load gungame/included_addons/%s' %cvarName)
        elif newValue == '0' and cvarName in gungamelib.getRegisteredAddonlist():
            es.unload('gungame/included_addons/%s' %cvarName)

# ==========================================================================================================================
# ==========================================================================================================================
#                !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! END GAME EVENTS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
# ==========================================================================================================================
# ==========================================================================================================================


# ==========================================================================================================================
#   HELPER FUNCTIONS
# ==========================================================================================================================
def getPlayer(userid):
    try:
        # Why not just use the Player constructor?
        return Player(userid)
    except (UseridError, TypeError), e:
        raise e

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

# ==========================================================================================================================
#   MESSAGE WRAPPERS
# ==========================================================================================================================
def msg(userid, addon, msg, opts={}, usePrefix=True):
    # Create message
    if userid == '#all':
        Message().msg('%s:%s' % (addon, msg), opts, usePrefix)
    else:
        Message(userid).msg('%s:%s' % (addon, msg), opts, usePrefix)

def saytext2(userid, addon, index, msg, opts={}, usePrefix=True):
    # Create message
    if userid == '#all':
        Message().saytext2(index, '%s:%s' % (addon, msg), opts, usePrefix)
    else:
        Message(userid).saytext2(index, '%s:%s' % (addon, msg), opts, usePrefix)

def echo(userid, addon, msg, opts={}, usePrefix=True):
    # Create message
    if userid == '#all':
        Message().echo('%s:%s' % (addon, msg), opts, usePrefix)
    else:
        Message(userid).echo('%s:%s' % (addon, msg), opts, usePrefix)

def hudhint(userid, addon, msg, opts={}):
    # Create message
    if userid == '#all':
        Message().hudhint('%s:%s' % (addon, msg), opts)
    else:
        Message(userid).hudhint('%s:%s' % (addon, msg), opts)

def centermsg(userid, addon, msg, opts={}):
    # Create message
    if userid == '#all':
        Message().centermsg('%s:%s' % (addon, msg), opts)
    else:
        Message(userid).centermsg('%s:%s' % (addon, msg), opts)

# ==========================================================================================================================
#   MESSAGE CLASS
# ==========================================================================================================================
class Message:
    def __init__(self, userid = None):
        # Set vars
        self.userid = 0
        self.object = None
        
        # Is userid console?
        if userid == 0:
            # Set userid and object
            self.userid = 0
            self.object = None
            
            # Ignore the rest of init
            return
        
        # Set the player object
        if userid:
            self.object = playerlib.getPlayer(userid)
            self.userid = userid
    
    def getLangStrings(self, message):
        # Set some vars
        file = message.split(':')[0]
        string = message.split(':')[1]
        
        # Set lang strings
        if file == 'core':
            self.langStrings = langlib.Strings('%s/cstrike/addons/eventscripts/gungame/strings.ini' % os.getcwd())
        else:
            # Does the folder exist in included_addons?
            if os.path.isfile(getGameDir('addons\\eventscripts\\gungame\\included_addons\\%s\\strings.ini' % file)):
                # Load file from included_addons
                self.langStrings = langlib.Strings('%s/cstrike/addons/eventscripts/gungame/included_addons/%s/strings.ini' % (os.getcwd(), file))
            elif os.path.isfile(getGameDir('addons\\eventscripts\\gungame\\custom_addons\\%s\\strings.ini' % file)):
                # Load file from custom_addons
                self.langStrings = langlib.Strings('%s/cstrike/addons/eventscripts/gungame/custom_addons/%s/strings.ini' % (os.getcwd(), file))
            else:
                # Raise error
                raise NameError, 'Could not find %s/strings.ini in either the included_addons or custom_addons folder.' % file
        
        # Format the string then return it
        return string
    
    def getString(self, message, tokens = None, object = None):
        # If no object set, use the class default
        if not object and self.userid != 0 and self.object != None:
            object = self.object
        
        # Return the string
        try:
            # Get the string
            rtnStr = self.langStrings(message, tokens, object.get('lang'))
            rtnStr = rtnStr.replace('#lightgreen', '\3').replace('#green', '\4').replace('#default', '\1')
            rtnStr = rtnStr.replace('\\3', '\3').replace('\\4', '\4').replace('\\1', '\1')
            rtnStr = rtnStr.replace('\\x03', '\3').replace('\\x04', '\4').replace('\\x01', '\1')
            
            # Return the string
            return rtnStr
        except:
            return self.langStrings(message, tokens)
        
    def msg(self, message, tokens = {}, usePrefix=True):
        # Get string
        string = self.getLangStrings(message)
        
        # Set prefix
        if usePrefix:
            prefix = '\4[%s]\1 ' % (self.langStrings('Prefix', {}, 'en'))
        else:
            prefix = ''
        
        if self.userid:
            es.tell(self.userid, '#multi', '%s%s' % (prefix, self.getString(string, tokens)))
        else:
            # Loop through the players
            for userid in es.getUseridList():
                # Get some vars
                userid = int(userid)
                object = playerlib.getPlayer(userid)
                
                # Send it
                es.tell(userid, '#multi', '%s%s' % (prefix, self.getString(string, tokens)))
                
    def hudhint(self, message, tokens = {}):
        # Get lang strings
        string = self.getLangStrings(message)
        
        # Is a userid set?
        if self.userid:
            # Send HudHint
            usermsg.hudhint(self.userid, self.getString(string, tokens))
        else:
            # Loop through the players
            for userid in es.getUseridList():
                # Get some vars
                userid = int(userid)
                object = playerlib.getPlayer(userid)
                
                # Send it
                usermsg.hudhint(userid, self.getString(string, tokens, object))
                
    def saytext2(self, index, message, tokens = {}, usePrefix=True):
        # Get lang strings
        string = self.getLangStrings(message)
        
        # Set prefix
        if usePrefix:
            prefix = '\4[%s]\1 ' % (self.langStrings('Prefix', {}, 'en'))
        else:
            prefix = ''
        
        # Is a userid set?
        if self.userid:
            # Send SayText2 message
            usermsg.saytext2(self.userid, index, '%s%s' % (prefix, self.getString(string, tokens)))
        else:
            # Loop through the players
            for userid in es.getUseridList():
                # Get some vars
                userid = int(userid)
                object = playerlib.getPlayer(userid)
                
                # Send it
                usermsg.saytext2(userid, index, '%s%s' % (prefix, self.getString(string, tokens, object)))
                
    def centermsg(self, message, tokens={}):
        # Get lang strings
        string = self.getLangStrings(message)
        
        # Is a userid set?
        if self.userid:
            # Send CenterMsg
            es.centermsg(self.userid, self.getString(string, tokens))
        else:
            # Loop through the players
            for userid in es.getUseridList():
                # Get some vars
                userid = int(userid)
                object = playerlib.getPlayer(userid)
                
                # Send it
                es.centermsg(userid, self.getString(string, tokens, object))
            
    def echo(self, message, tokens={}, usePrefix=True):
        # Get string
        string = self.getLangStrings(message)
        
        # Set prefix
        if usePrefix:
            prefix = '%s: ' % (self.langStrings('Prefix', {}, 'en'))
        else:
            prefix = ''
        
        if self.userid == 0:
            # Print to console
            es.dbgmsg(0, '%s%s' % (prefix, self.getString(string, tokens)))
        elif self.userid:
            # Send echo message
            usermsg.echo(self.userid, '%s%s' % (prefix, self.getString(string, tokens)))
        else:
            # Loop through the players
            for userid in es.getUseridList():
                # Get some vars
                userid = int(userid)
                object = playerlib.getPlayer(userid)
                
                # Send it
                usermsg.echo(userid, '%s%s' % (prefix, self.getString(string, tokens)))