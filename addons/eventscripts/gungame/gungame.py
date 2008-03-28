''' (c) 2008 by the GunGame Coding Team

    Title: gungame
    Version: 1.0.198
    Description: The main addon, handles leaders and events.
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python Imports
import os
import cPickle
import ConfigParser

# EventScripts Imports
import es
import gamethread
import playerlib
import usermsg
import popuplib
import keyvalues

# GunGame Imports
import gungamelib
reload(gungamelib)

# ==============================================================================
#   EVENTSCRIPTS STUFF
# ==============================================================================
# Initialize some CVars
gungameVersion = "1.0.198"
es.ServerVar('eventscripts_ggp', gungameVersion).makepublic()

# Register with EventScripts
info = es.AddonInfo()
info.name     = "GunGame: Python"
info.version  = gungameVersion
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame"
info.author   = "XE_ManUp, RideGuy, Saul Rennison"

# ==============================================================================
#   GLOBALS
# ==============================================================================
dict_gungameVariables = {}
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

class gungameWinners:
    '''Class used to store GunGame winner information'''
    int_wins = 1
    int_timestamp = es.gettime()

# ==============================================================================
#   ERROR CLASSES
# ==============================================================================
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

# ==============================================================================
#   POPUP COMMANDS
# ==============================================================================
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
    if gungamelib.getVariableValue('gg_multikill_override') == 0:
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
    if gungamelib.getVariableValue('gg_multikill_override') == 0:
        gungameLevelMenu.modline(2, '   * You are on level %d' %gungamePlayer['level']) # Line #2
        gungameLevelMenu.modline(3, '   * You need a %s kill to advance' %gungamePlayer.getWeapon()) # Line #3
    else:
        gungameLevelMenu.modline(2, '   * You are on level %d (%s)' %(gungamePlayer['level'], gungamePlayer.getWeapon())) # Line #2
        gungameLevelMenu.modline(3, '   * You have made %d/%d of your required kills' %(gungamePlayer['multikill'], gungamelib.getVariableValue('gg_multikill_override'))) # Line #3
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
        # Get their name
        name = es.getplayername(userid)
        
        # Is their name 0?
        if isinstance(name, int) and name == 0:
            continue
        
        # Add their name to the leader names
        list_leaderNames.append(removeReturnChars(name))
    
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

# ==============================================================================
#   CONSOLE COMMANDS
# ==============================================================================
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

# ==============================================================================
#   HELPER FUNCTIONS
# ==============================================================================
def loadCustom(addonName):
    es.load('gungame/custom_addons/' + str(addonName))
    
def unloadCustom(addonName):
    es.unload('gungame/custom_addons/' + str(addonName))

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
    elif armorType == 1:
        # Give the player kevlar only
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
        list_leadersUserid = gungamelib.getCurrentLeaderList()
    
    # How many levels behind the leader?
    if levelsBehindLeader == 0:
        # Is there more than 1 leader?
        if gungamelib.getCurrentLeaderCount() == 1:    
            HudHintText = 'Current level: %d of %d\nCurrent weapon: %s%s\n\nYou are the leader.' % (gungamePlayer['level'], gungamelib.getTotalLevels(), gungamePlayer.getWeapon(), multiKillText)
        else:
            if leaderLevel == 1:
                HudHintText = 'Current level: %d of %d\nCurrent weapon: %s%s\n\nThere are no leaders.' % (gungamePlayer['level'], gungamelib.getTotalLevels(), gungamePlayer.getWeapon(), multiKillText)
            else:
                HudHintText = 'Current level: %d of %d\nCurrent weapon: %s%s\n\nYou are amongst the leaders (' % (gungamePlayer['level'], gungamelib.getTotalLevels(), gungamePlayer.getWeapon(), multiKillText)
                
                # Get the first 2 leaders
                leadersCount = 0
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
        HudHintText = 'Current level: %d of %d\nCurrent weapon: %s%s\n\nLeader (%s) level: %d of %d (%s)' \
                            %(gungamePlayer['level'], gungamelib.getTotalLevels(),gungamePlayer.getWeapon(),
                            multiKillText, es.getplayername(gungamelib.getCurrentLeaderList()[0]),
                            gungamelib.getLeaderLevel(), gungamelib.getTotalLevels(),
                            gungamelib.getLevelWeapon(gungamelib.getLeaderLevel()))
            
    if not int(gungamelib.getGlobal('voteActive')) and not int(gungamelib.getGlobal('isWarmup')):
        gamethread.delayed(0.5, usermsg.hudhint, (str(userid), HudHintText))

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    global dict_gungameWinners
    global countBombDeathAsSuicide
    
    # Load custom events
    es.loadevents('declare', 'addons/eventscripts/gungame/events/es_gungame_events.res')
    
    # Get the scripts in the "../cstrike/addons/eventscripts/gungame/included_addons" folder
    for includedAddon in os.listdir(gungamelib.getGameDir('/addons/eventscripts/gungame/included_addons/')):
        if includedAddon[0:3] == 'gg_':
            list_includedAddonsDir.append(includedAddon)
    
    # Get the scripts in the "../cstrike/addons/eventscripts/gungame/custom_addons" folder
    for customAddon in os.listdir(gungamelib.getGameDir('/addons/eventscripts/gungame/custom_addons/')):
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
    
    weaponOrderINI = ConfigParser.ConfigParser()
    gameDir = es.ServerVar('eventscripts_gamedir')
    
    # Loop through the Weapon Order INI and register their information with GunGame
    weaponOrderINI.read('%s/cfg/gungame/gg_weapon_orders.ini' % gameDir)
    for weaponOrderName in weaponOrderINI.sections():
        weaponOrderFile = weaponOrderINI.get(weaponOrderName, 'fileName')
        myWeaponOrder = gungamelib.getWeaponOrderFile(weaponOrderFile)
        if weaponOrderINI.get(weaponOrderName, 'fileName') == gungamelib.getVariableValue('gg_weapon_order_file'):
            myWeaponOrder.setWeaponOrderFile()
            
            if gungamelib.getVariableValue('gg_weapon_order') != '#default':
                myWeaponOrder.changeWeaponOrderType(gungamelib.getVariableValue('gg_weapon_order'))
            
            if gungamelib.getVariableValue('gg_multikill_override') > 1:
                myWeaponOrder.setMultiKillOverride(gungamelib.getVariableValue('gg_multikill_override'))
            
            myWeaponOrder.echo()
    
    '''
    #  ESS COMMAND REGISTRATION
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
    '''   
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

    if gungamelib.getVariableValue('gg_save_winners') > 0:
        # Set a variable for the path of the winner's database
        winnersDataBasePath = es.getAddonPath('gungame') + '/data/winnersdata.db'
        
        # See if the file exists
        if not os.path.isfile(winnersDataBasePath):
            # Open the file
            winnersDataBaseFile = open(winnersDataBasePath, 'w')
            
            # Place the contents of dict_gungameWinners in
            cPickle.dump(dict_gungameWinners, winnersDataBaseFile)
            
            # Save changes
            winnersDataBaseFile.close()
        # Open the "..cstrike/addons/eventscripts/gungame/data/winnerdata.db" file
        winnersDataBaseFile = open(winnersDataBasePath, 'r')
        
        # Load the winners database file into dict_gungameWinners via pickle
        dict_gungameWinners = cPickle.load(winnersDataBaseFile)
        
        # Close the winners database file
        winnersDataBaseFile.close()
    
    # Set Up Active Players
    gungamelib.resetGunGame()
    
    # Reset the leader names list
    list_leaderNames = []
    
    # Set Up a custom variable for voting in dict_gungameVariables
    dict_gungameVariables['gungame_voting_started'] = False

    # If there is a current map listed, then the admin has loaded GunGame mid-round/mid-map
    if gungamelib.inLevel():
        # Check to see if the warmup round needs to be activated
        if gungamelib.getVariableValue('gg_warmup_timer') > 0:
            es.load('gungame/included_addons/gg_warmup_round')
        else:
            # Fire gg_start event
            es.event('initialize','gg_start')
            es.event('fire','gg_start')
    
    # Restart map
    gungamelib.msg('gungame', '#all', 'Loaded')
    es.server.cmd('mp_restartgame 2')
    
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

def es_map_start(event_var):
    #Load custom GunGame events
    es.loadevents('declare', 'addons/eventscripts/gungame/events/es_gungame_events.res')
    
    # Execute GunGame's autoexec.cfg
    es.delayed('1', 'exec gungame/gg_server.cfg')
    
    # Split the map name into a list separated by "_"
    list_mapPrefix = event_var['mapname'].split('_')
    
    # Insert the new map prefix into the GunGame Variables
    gungamelib.setGlobal('gungame_currentmap_prefix', list_mapPrefix[0])
    
    # Reset the "gungame_voting_started" variable
    dict_gungameVariables['gungame_voting_started'] = False
    
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
    
    # Reset the leader names list
    list_leaderNames = []

def player_changename(event_var):
    # Change the player's name in the leaderlist
    if removeReturnChars(event_var['oldname']) in list_leaderNames:
        list_leaderNames[list_leaderNames.index(event_var['oldname'])] = removeReturnChars(event_var['newname'])

def round_start(event_var):
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

def round_freeze_end(event_var):
    global countBombDeathAsSuicide
    
    # Create a variable to prevent bomb explosion deaths from counting a suicides
    countBombDeathAsSuicide = True

def round_end(event_var):
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
                    
def player_activate(event_var):
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
    
def player_disconnect(event_var):
    global dict_reconnectingPlayers
    
    userid = int(event_var['userid'])
    
    if not gungamelib.playerExists(userid):
        return

    gungamePlayer = gungamelib.getPlayer(userid)
    steamid = gungamePlayer['steamid']

    # Make sure the player is not a bot
    if 'BOT' not in steamid:
        # See if this player is already in the Reconnecting Players Dictionary (shouldn't ever be, but we will check anyhow, just to be safe)
        if not dict_reconnectingPlayers.has_key(steamid):
            # Set this player up in the Reconnecting Players Dictionary
            reconnectLevel = gungamePlayer['level'] - gungamelib.getVariableValue('gg_retry_punish')
            if reconnectLevel > 0:
                dict_reconnectingPlayers[steamid] = reconnectLevel
            else:
                dict_reconnectingPlayers[steamid] = 1
    
    # Remove the player from the leader list
    # NOTE: Possibly decremented
    #if userid in gungamelib.getCurrentLeaderList():
    #    gungamelib.removeLeader(userid)
    
    # Var prep
    leaders = gungamelib.getCurrentLeaderList()
    oldLeaders = gungamelib.getOldLeaderList()
    
    # Has there been leader changes?
    if userid in oldLeaders:
        # Get first player stuff
        firstPlayer = int(leaders[0])
        player = gungamelib.getPlayer(firstPlayer)
        level = player['level']
        
        # Only 1 leader
        if len(leaders) == 1:
            # Get index
            index = player.attributes['index']
            name = es.getplayername(firstPlayer)
            
            # Announce to world
            gungamelib.saytext2('gungame', '#all', index, 'NewLeader', {'player': name, 'level': level}, False)
        else:
            # Happens if everyone is level 1, then a player disconnects.
            if leaders == es.getUseridList():
                return
            
            # Var prep
            leaderNames = []
            count = 0
            
            # Loop through leaders
            for userid in leaders:
                # Only have 3 leader names on there
                if count == 3:
                    leaderNames.append('...')
                    break
                
                # Add leader name
                leaderNames.append(es.getplayername(userid))
                
                # Increment count
                count += 1
            
            # Announce to world
            gungamelib.msg('gungame', '#all', 'NewLeaders', {'players': ', '.join(leaderNames), 'level': level}, False)

def player_spawn(event_var):
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    
    if not gungamelib.isSpectator(userid):
        if not es.isbot(userid):
            # Reset the player's location with GunGame's AFK Checker
            gamethread.delayed(0.6, gungamePlayer.resetPlayerLocation, ())

        # Check to see if the WarmUp Round is Active
        if not gungamelib.getGlobal('isWarmup'):
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

def player_jump(event_var):
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Is player human?
    if not es.isbot(userid):
        # Here, we will make sure that the player isn't counted as AFK
        gungamePlayer.playerNotAFK()

def player_death(event_var):
    global countBombDeathAsSuicide
    
    # Set vars
    userid = int(event_var['userid'])
    attacker = int(event_var['attacker'])
    gungameVictim = gungamelib.getPlayer(userid)
    
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
                                if gungamelib.getVariableValue('gg_multikill_override'):
                                    gungameAttacker['multikill'] = gungamelib.getVariableValue('gg_multikill_override')
                            else:
                                gungameAttacker['multikill'] += 1
                                
                            if gungameAttacker['multikill'] == multiKill:
                                levelUpOldLevel = gungameAttacker['level']
                                levelUpNewLevel = levelUpOldLevel + 1
                                
                                gungamelib.triggerLevelUpEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelUpOldLevel, levelUpNewLevel, userid, event_var['es_username'])
                                gungameAttacker['multikill'] = 0
                                
                                # Play the levelup sound
                                if gungamelib.getSound('levelup'):
                                    es.playsound(attacker, gungamelib.getSound('levelup'), 1.0)
                            else:
                                # Message the attacker
                                multiKill = gungamelib.getLevelMultiKill(gungameAttacker['level'])
                                gungamelib.hudhint('gungame', attacker, 'KillsThisLevel', {'kills': gungameAttacker['multikill'], 'togo': multiKill})
                                
                                # Message the victim
                                multiKill = gungamelib.getLevelMultiKill(gungameVictim['level'])
                                gungamelib.hudhint('gungame', userid, 'KillsThisLevel', {'kills': gungameVictim['multikill'], 'togo': multiKill})
                                
                        # Multikill was not active
                        else:
                            levelUpOldLevel = gungameAttacker['level']
                            levelUpNewLevel = levelUpOldLevel + 1
                            
                            gungamelib.triggerLevelUpEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelUpOldLevel, levelUpNewLevel, userid, event_var['es_username'])
                            
                            # Play the levelup sound
                            if gungamelib.getSound('levelup'):
                                es.playsound(attacker, gungamelib.getSound('levelup'), 1.0)
                            
                # The victim was AFK
                else:
                    gungamelib.hudhint('gungame', attacker, 'PlayerAFK', {'player': event_var['es_username']})
                    
                    # Check to see if AFK punishment is active
                    if gungamelib.getVariableValue('gg_afk_rounds') > 0:
                        # BOTs are never AFK
                        if not es.isbot(userid):
                            # Run the AFK punishment code
                            afkPunishCheck(userid)
        else:
            # Must be a team kill or a suicide
            if userid == attacker:
                # Yep! They killed themselves. Now let's see if we are going to punish the dead...
                if gungamelib.getVariableValue('gg_suicide_punish') > 0:
                    # Set vars
                    levelDownOldLevel = int(gungameAttacker['level'])
                    levelDownNewLevel = levelDownOldLevel - gungamelib.getVariableValue('gg_suicide_punish')
                    
                    # Let's not put them on a non-existant level 0...
                    if levelDownNewLevel > 0:
                        gungamelib.triggerLevelDownEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelDownOldLevel, levelDownNewLevel, userid, event_var['es_username'])
                    else:
                        gungamelib.triggerLevelDownEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelDownOldLevel, 1, userid, event_var['es_username'])
                        
                    # Play the leveldown sound
                    if gungamelib.getSound('leveldown'):
                        es.playsound(userid, gungamelib.getSound('leveldown'), 1.0)
            else:
                # Let's see if we get to punish the vile TK'er...
                if gungamelib.getVariableValue('gg_tk_punish') > 0:
                    # Set vars
                    levelDownOldLevel = gungameAttacker['level']
                    levelDownNewLevel = levelDownOldLevel - gungamelib.getVariableValue('gg_tk_punish')
                    
                    # Let's not put them on a non-existant level 0...
                    if levelDownNewLevel > 0:
                        gungamelib.triggerLevelDownEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelDownOldLevel, levelDownNewLevel, userid, event_var['es_username'])
                        
                    else:
                        gungamelib.triggerLevelDownEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelDownOldLevel, 1, userid, event_var['es_username'])
                        
                    # Play the leveldown sound
                    if gungamelib.getSound('leveldown'):
                        es.playsound(attacker, gungamelib.getSound('leveldown'), 1.0)
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
                    gungamelib.triggerLevelDownEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_attackername'], event_var['es_userteam'], levelDownOldLevel, levelDownNewLevel, userid, event_var['es_username'])
                    
                # Play the leveldown sound
                if gungamelib.getSound('leveldown'):
                    es.playsound(userid, gungamelib.getSound('leveldown'), 1.0)
    
def bomb_defused(event_var):
    # Set vars
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    playerWeapon = gungamePlayer.getWeapon()
    
    # Cant skip the last level
    if int(gungamePlayer['level']) == int(gungamelib.getTotalLevels()) or playerWeapon == 'knife' or playerWeapon == 'hegrenade':
        gungamelib.msg('gungame', userid, 'CannotSkipLevel_ByDefusing', {'level': playerWeapon})
        return
    
    # Level them up
    levelUpOldLevel = gungamePlayer['level']
    levelUpNewLevel = levelUpOldLevel + 1
    gungamelib.triggerLevelUpEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_username'], event_var['es_userteam'], levelUpOldLevel, levelUpNewLevel, '0', '0')

def bomb_exploded(event_var):
    # Set vars
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    playerWeapon = gungamePlayer.getWeapon()
    
    # Cant skip the last level
    if int(gungamePlayer['level']) == int(gungamelib.getTotalLevels()) or playerWeapon == 'knife' or playerWeapon == 'hegrenade':
        gungamelib.msg('gungame', userid, 'CannotSkipLevel_ByPlanting', {'level': playerWeapon})
        return
    
    # Level them up
    levelUpOldLevel = gungamePlayer['level']
    levelUpNewLevel = levelUpOldLevel + 1
    gungamelib.triggerLevelUpEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_username'], event_var['es_userteam'], levelUpOldLevel, levelUpNewLevel, '0', '0')
    
def player_team(event_var):
    if int(event_var['oldteam']) < 2 and int(event_var['team']) > 1:
        # Play the welcome sound
        if gungamelib.getSound('welcome'):
            es.playsound(userid, gungamelib.getSound('welcome'), 1.0)

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
    else:
        # Regular levelup code...
        userid = int(event_var['userid'])
        gungamePlayer = gungamelib.getPlayer(userid)
        
        if gungamelib.getLevelWeapon(event_var['new_level']) == 'knife':
            # Play sound
            if gungamelib.getSound('knifelevel'):
                for userid in es.getUseridList():
                    es.playsound(userid, gungamelib.getSound('knifelevel'), 1.0)
                
        if gungamelib.getLevelWeapon(event_var['new_level']) == 'hegrenade':
            # Play sound
            if gungamelib.getSound('nadelevel'):
                for userid in es.getUseridList():
                    es.playsound(userid, gungamelib.getSound('nadelevel'), 1.0)
        
        # Set the player's level in the GunGame Core Dictionary
        gungamePlayer['level'] = int(event_var['new_level'])
        
        # Reset the player's multikill in the GunGame Core Dictionary
        gungamePlayer['multikill'] = 0
        
        leaderLevel = gungamelib.getLeaderLevel()
        
        if leaderLevel == int(event_var['new_level']):
            rebuildLeaderMenu()

        if not dict_gungameRegisteredAddons.has_key('gg_warmup_round'):
            levelInfoHudHint(userid)

        if leaderLevel == gungamelib.getTotalLevels() - gungamelib.getVariableValue('gg_vote_trigger'):
            if es.ServerVar('eventscripts_nextmapoverride') == '':
                if not dict_gungameVariables['gungame_voting_started']:
                    es.event('initialize', 'gg_vote')
                    es.event('fire', 'gg_vote')
            else:
                gungamelib.echo('gungame', 0, 0, 'MapSetBefore')

def gg_leveldown(event_var):
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Set the player's level in the GunGame Core Dictionary
    gungamePlayer['level'] = int(event_var['new_level'])

def gg_new_leader(event_var):
    playerName = es.getplayername(event_var['userid'])
    leaderLevel = gungamelib.getLeaderLevel()
    
    gungamelib.saytext2('gungame', '#all', event_var['es_userindex'], 'NewLeader', {'player': playerName, 'level': leaderLevel}, False)
    rebuildLeaderMenu()

def gg_tied_leader(event_var):
    # Set variables
    leaderCount = gungamelib.getCurrentLeaderCount()
    index = playerlib.getPlayer(int(event_var['userid'])).get('index')
    playerName = es.getplayername(event_var['userid'])
    leaderLevel = gungamelib.getLeaderLevel()
    
    if leaderCount == 2:
        gungamelib.saytext2('gungame', '#all', index, 'TiedLeader_Singular', {'player': playerName, 'level': leaderLevel}, False)
    else:
        gungamelib.saytext2('gungame', '#all', index, 'TiedLeader_Plural', {'count': leaderCount, 'player': playerName, 'level': leaderLevel}, False)

    rebuildLeaderMenu()
    
def gg_leader_lostlevel(event_var):
    rebuildLeaderMenu()
    
def unload():
    global gungameWeaponOrderMenu
    global dict_gungameRegisteredAddons
    
    for addonName in gungamelib.getRegisteredAddonlist():
        if addonName in list_includedAddonsDir:
            es.unload('gungame/included_addons/%s' % addonName)
        elif addonName in list_customAddonsDir:
            es.unload('gungame/custom_addons/%s' % addonName)
        
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
    
    # Fire gg_unload event
    es.event('initialize','gg_unload')
    es.event('fire','gg_unload')
    
    # Remove the notify flag from all GunGame Console Variables
    list_gungameVariables = gungamelib.getVariableList()
    for variable in list_gungameVariables:
        es.ServerVar(variable).removeFlag('notify')
        es.server.cmd('%s 0' % variable)
    
    gungamelib.clearGunGame()

def gg_vote(event_var):
    dict_gungameVariables['gungame_voting_started'] = True
    if gungamelib.getVariableValue('gg_map_vote') == 2:
        es.server.cmd('ma_voterandom end %s' %gungamelib.getVariableValue('gg_map_vote_size'))

def gg_win(event_var):
    global dict_gungameWinners
    global countBombDeathAsSuicide
    
    userid = int(event_var['userid'])
    index = playerlib.getPlayer(userid).get('index')
    playerName = event_var['name']
    steamid = event_var['steamid']

    # Create a variable to prevent bomb explosion deaths from counting a suicides
    countBombDeathAsSuicide = False
    
    # End the GunGame Round
    es.server.cmd('es_xgive %d game_end' %userid)
    es.server.cmd('es_xfire %d game_end EndGame' %userid)
    
    # Enable alltalk
    es.server.cmd('sv_alltalk 1')
    
    # Reset all the players
    for userid in playerlib.getUseridList('#all'):
        gungamePlayer = gungamelib.getPlayer(userid)
        
        # Reset Players in the GunGame Core Database
        gungamePlayer.resetPlayer()
    
    # Tell the world
    gungamelib.saytext2('gungame', '#all', index, 'PlayerWon', {'player': playerName})
    gungamelib.centermsg('gungame', '#all', 'PlayerWon_Center', {'player': playerName})
    
    # Play the winner sound
    for userid in es.getUseridList():
        if gungamelib.getSound('winner'):
            es.playsound(userid, gungamelib.getSound('winner'), 1.0)
    
    if gungamelib.getVariableValue('gg_save_winners') > 0:
        # See if the player has won before
        if not dict_gungameWinners.has_key(steamid):
            # Ah, we have a new winner! Let's add them to the database
            dict_gungameWinners[steamid] = gungameWinners()
        else:
            # Increment the win count
            dict_gungameWinners[steamid].int_wins += 1
        
        # Open file
        winnersDataBasePath = es.getAddonPath('gungame') + '/data/winnersdata.db'
        winnersDataBaseFile = open(winnersDataBasePath, 'w')
        
        # Place the contents of dict_gungameWinners in it
        cPickle.dump(dict_gungameWinners, winnersDataBaseFile)
        
        # Close the file
        winnersDataBaseFile.close()

def server_cvar(event_var):
    cvarName = event_var['cvarname']
    newValue = event_var['cvarvalue']

    if gungamelib.isNumeric(newValue):
        newValue = int(newValue)
    
    if cvarName not in gungamelib.getVariableList():
        return
    
    if cvarName in gungamelib.getDependencyList():
        if newValue != gungamelib.getDependencyValue(cvarName):
            es.dbgmsg(0, '[GunGame] %s is a protected dependency' %cvarName)
            if str(gungamelib.getVariableValue(cvarName)) != newValue:
                gungamelib.setVariableValue(cvarName, gungamelib.getVariableValue(cvarName))
            return
            
    if gungamelib.getVariableValue(cvarName) != newValue:
        gungamelib.setVariableValue(cvarName, newValue)
    
    # GG_MAPVOTE
    if cvarName == 'gg_map_vote':
        if newValue == 1 and 'gg_map_vote' not in gungamelib.getRegisteredAddonlist():
            es.server.queuecmd('es_load gungame/included_addons/gg_map_vote')
        elif newValue != 1 and 'gg_map_vote' in gungamelib.getRegisteredAddonlist():
            es.unload('gungame/included_addons/gg_map_vote')
    # GG_NADE_BONUS
    elif cvarName == 'gg_nade_bonus':
        if newValue != 0 and newValue != 'knife' and newValue in list_allWeapons:
            es.server.queuecmd('es_load gungame/included_addons/gg_nade_bonus')
        elif newValue == 0 and 'gg_nade_bonus' in gungamelib.getRegisteredAddonlist():
            es.unload('gungame/included_addons/gg_nade_bonus')
    # GG_SPAWN_PROTECTION
    elif cvarName == 'gg_spawn_protect':
        if newValue > 0 and 'gg_spawn_protect' not in gungamelib.getRegisteredAddonlist():
            es.server.queuecmd('es_load gungame/included_addons/gg_spawn_protect')
        elif newValue == 0 and 'gg_spawn_protect' in gungamelib.getRegisteredAddonlist():
            es.unload('gungame/included_addons/gg_spawn_protect')
    # GG_FRIENDLYFIRE
    elif cvarName == 'gg_friendlyfire':
        if newValue > 0 and 'gg_friendlyfire' not in gungamelib.getRegisteredAddonlist():
            es.server.queuecmd('es_load gungame/included_addons/gg_friendlyfire')
        elif newValue == 0 and 'gg_friendlyfire' in gungamelib.getRegisteredAddonlist():
            es.unload('gungame/included_addons/gg_friendlyfire')
    # All other included addons
    elif cvarName in list_includedAddonsDir:
        if newValue == 1:
            es.server.queuecmd('es_load gungame/included_addons/%s' %cvarName)
        elif newValue == 0 and cvarName in gungamelib.getRegisteredAddonlist():
            es.unload('gungame/included_addons/%s' %cvarName)
    elif cvarName == 'gg_multikill_override':
        if newValue != gungamelib.getVariableValue('gg_multikill_override'):
            myWeaponOrder = gungamelib.getWeaponOrderFile(gungamelib.getVariableValue('gg_weapon_order_file'))
            if newValue == 0:
                myWeaponOrder.setMultiKillOverride(0)
            else:
                myWeaponOrder.setMultiKillOverride(newValue)
    elif cvarName == 'gg_weapon_order_file':
        if newValue != gungamelib.getVariableValue('gg_weapon_order_file'):
            myWeaponOrder = gungamelib.getWeaponOrderFile(gungamelib.getVariableValue('gg_weapon_order_file'))
            myWeaponOrder.setWeaponOrderFile()
            if gungamelib.getVariableValue('gg_multikill_override') > 1:
                myWeaponOrder.setMultiKillOverride(gungamelib.getVariableValue('gg_multikill_override'))