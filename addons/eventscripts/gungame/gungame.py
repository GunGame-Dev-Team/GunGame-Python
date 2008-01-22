import es
import os
import random
import gamethread
import gungame
import playerlib
import langlib
import usermsg
import popuplib
import cPickle
import string
import keyvalues

# Create a public CVAR for GunGame seen as "eventscripts_ggp"
gungameVersion = "1.0.77"
es.set('eventscripts_ggp', gungameVersion)
es.makepublic('eventscripts_ggp')

# Register the addon with EventScripts
info = es.AddonInfo() 
info.name     = "GunGame: Python" 
info.version  = gungameVersion
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007"

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
dict_afk = {}
dict_gungame_core = {}
dict_gungameVariables = {}
dict_globals = {}
list_primaryWeapons = ['awp', 'scout', 'aug', 'mac10', 'tmp', 'mp5navy', 'ump45', 'p90', 'galil', 'famas', 'ak47', 'sg552', 'sg550', 'g3sg1', 'm249', 'm3', 'xm1014', 'm4a1']
list_secondaryWeapons = ['glock', 'usp', 'p228', 'deagle', 'elite', 'fiveseven']
list_allWeapons = ['glock', 'usp', 'p228', 'deagle', 'elite', 'fiveseven', 'awp', 'scout', 'aug', 'mac10', 'tmp', 'mp5navy', 'ump45', 'p90', 'galil', 'famas', 'ak47', 'sg552', 'sg550', 'g3sg1', 'm249', 'm3', 'xm1014', 'm4a1', 'hegrenade', 'flashbang', 'smokegrenade']
dict_gungameRegisteredAddons = {}
dict_reconnectingPlayers = {}
dict_gungameWinners = {}
dict_gungameRegisteredDependencies = {}
list_includedAddonsDir = []
list_customAddonsDir = []

# Class used in the dict_gungame_core
class gungamePlayers:
    "Class used to store core GunGame information"
    int_level = 1
    int_afk_rounds = 0
    int_multikill = 0
    int_triple_level = 0
    int_prevent_level = 0

# Class used in dict_gungameWinners
class gungameWinners:
    "Class used to store GunGame winner information"
    int_wins = 1
    int_timestamp = es.gettime()

# Class used in dict_afk
class afkPlayers:
    "Class used in dictionary for AFK Players"
    int_afk_math_total = 0

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

# ===================================================================================================
# ===================================================================================================
#        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! BEGIN POPUPLIB COMMANDS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
# ===================================================================================================
# ===================================================================================================

# GUNGAME WEAPON ORDER POPUP
gungameWeaponOrderMenu = None

# Handle the GunGame Weapon Order Popup
def weaponOrderMenuHandler(userid, choice, popupname):
    pass

# Display the GunGame Weapon Order Popup to the player that requested it
def displayWeaponOrderMenu():
    popuplib.send('gungameWeaponOrderMenu_page1', es.getcmduserid())

def buildWeaponOrderMenu():
    global dict_gungameWeaponOrder
    global gungameWeaponOrderMenu
    # Create a list of level numbers to use for creating the popup
    list_gungameLevels = dict_gungameWeaponOrder.keys()
    # Create a list of weapon names to use for creating the popup
    list_gungameWeapons = dict_gungameWeaponOrder.values()
    # Find out how many menu pages there are going to be
    totalMenuPages = int(round((int(getTotalLevels()) * 0.1) + 0.4))
    # Create a variable to store the current page count
    buildPageCount = 1
    # Create a variable to keep track of the index number for pulling the level/weapon information from the list_gungameLevels and list_gungameWeapons
    levelCountIndex = 0
    # Create a variable to track the "max" or the "cap" of indexes to retrieve from the lists
    levelCountMaxIndex = 0
    # Do he following loop until we have reached the total number of pages that we have to create
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
                gungameWeaponOrderMenu.addline('->%d.   %s' %(list_gungameLevels[levelCountIndex], list_gungameWeapons[levelCountIndex]))
            else:
                # Now, we add the weapons to the popup, as well as number them by level (without the extra "space")
                gungameWeaponOrderMenu.addline('->%d. %s' %(list_gungameLevels[levelCountIndex], list_gungameWeapons[levelCountIndex]))
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
    if int(getGunGameVar('gg_multikill')) == 0:
        gungameLevelMenu.addline('->1. LEVEL') # Line #1
        gungameLevelMenu.addline('   * You are on level <level number>') # Line #2
        gungameLevelMenu.addline('   * You need a <weapon name> kill to advance') # Line #3
        gungameLevelMenu.addline('   * There currently is no leader') # Line #4
    else:
        gungameLevelMenu.addline('->1. LEVEL') # Line #1
        gungameLevelMenu.addline('   * You are on level <level number> (<weapon name>)') # Line #2
        gungameLevelMenu.addline('   * You have made #/# of your required kills') # Line #3
        gungameLevelMenu.addline('   * There currently is no leader') # Line #4
    if int(getGunGameVar('gg_save_winners')) > 0:
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
    global list_leaderNames
    gungameLevelMenu = popuplib.find('gungameLevelMenu')
    gungamePlayer = gungame.getPlayer(userid)
    if int(getGunGameVar('gg_multikill')) == 0:
        gungameLevelMenu.modline(2, '   * You are on level %d' %int(gungamePlayer.get('level'))) # Line #2
        gungameLevelMenu.modline(3, '   * You need a %s kill to advance' %gungamePlayer.get('weapon')) # Line #3
    else:
        gungameLevelMenu.modline(2, '   * You are on level %d (%s)' %(int(gungamePlayer.get('level')), gungamePlayer.get('weapon'))) # Line #2
        gungameLevelMenu.modline(3, '   * You have made %d/%d of your required kills' %(int(gungamePlayer.get('multikill')), int(getGunGameVar('gg_multikill')))) # Line #3
    leaderLevel = int(getLeaderLevel())
    playerLevel = int(gungamePlayer.get('level'))
    if leaderLevel > 1:
        # See if the player is a leader:
        if playerLevel == leaderLevel:
            # See if there is more than 1 leader
            if int(len(list_leaderNames)) > 1:
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
    if int(getGunGameVar('gg_save_winners')) > 0:
        gungameLevelMenu.modline(6, '   * You have won %d time(s)' %gungamePlayer.get('Wins')) # Line #6
        if leaderLevel > 1:
            gungameLevelMenu.modline(8, '   * Leader Level: %d (%s)' %(leaderLevel, getLevelWeapon(leaderLevel))) # Line #8
        else:
            gungameLevelMenu.modline(8, '   * Leader Level: There are no leaders') # Line #8
    else:
        if leaderLevel > 1:
            gungameLevelMenu.modline(6, '   * Leader Level: %d (%s)' %(leaderLevel, getLevelWeapon(leaderLevel))) # Line #6
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
    global list_leaderNames
    # Check to see if the popup "gungameLevelMenu" exists
    if popuplib.exists('gungameLeadersMenu'):
        # The popup exists...let's unsend it
        popuplib.unsendname('gungameLeadersMenu', playerlib.getUseridList('#human'))
        # Now, we need to delete it
        popuplib.delete('gungameLeadersMenu')
    # Get leader level
    leaderLevel = int(getLeaderLevel())
    # Let's create the "gungameLeadersMenu" popup
    gungameLeadersMenu = popuplib.create('gungameLeadersMenu')
    gungameLeadersMenu.addline('->1. Current Leaders:')
    gungameLeadersMenu.addline('    Level %d (%s)' %(leaderLevel, getLevelWeapon(leaderLevel)))
    gungameLeadersMenu.addline('--------------------------')
    for leaderName in list_leaderNames:
        gungameLeadersMenu.addline('   * %s' %leaderName)
    gungameLeadersMenu.addline('--------------------------')
    gungameLeadersMenu.addline('0. Exit')
    gungameLeadersMenu.timeout('send', 5)
    gungameLeadersMenu.timeout('view', 5)
    
# ===================================================================================================
# ===================================================================================================
#          !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! END POPUPLIB COMMANDS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
# ===================================================================================================
# ===================================================================================================


# ===================================================================================================
# ===================================================================================================
#        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! BEGIN GUNGAME COMMANDS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
# ===================================================================================================
# ===================================================================================================

class Player:
    "Class used for the get/set commands in GunGame"
    userid = 0

    global dict_gungameWeaponOrder
    
    # default initialization routine. Give us a userid.
    def __init__(self, playerid):
        try:
            # We'll be nice and convert the playerid to an int in case they gave
            # us a string userid.
            self.userid = int(playerid)
            # Check if it's a valid userid. Otherwise we throw.
            if not es.exists('userid', self.userid):
                raise UseridError, str(self.userid) + ' is an invalid userid'
            # Maybe use es.createplayerlist(userid) to get initial values?
            self.refreshAttributes()
            # TODO: What else do we need to initialize?
        except TypeError, e:
            raise TypeError, 'Player argument expected a userid'

    def refreshAttributes(self):
        """
        Refresh the attributes for this player from ES. These are cached in
        the player object for performance.
        """
        # If this fails maybe they gave us the wrong userid, so maybe it should
        # except all the way up? Probably need a cleaner exception, though.
        try:
            self.attributes = es.createplayerlist(self.userid)[self.userid]
        except KeyError:
            raise PlayerError, 'player has left the server'
            
            
    # BEGIN "SET" COMMANDS:
    # -------------------------------------
    # myPlayer = gungame.setPlayer(event_var['userid'])
    def set(self, param, value1, value2=None):
        #global dict_gungame_core
        param = str(param).lower()
        
        # SET LEVEL
        # myPlayer.set('level', 6)
        if param == 'level':
            value1 = int(value1)
            if value1 > 0:
                if dict_gungame_core.has_key(self.userid):
                    dict_gungame_core[self.userid].int_level = value1
            else:
                raise LevelValueError, 'Level value must be greater than 0'
        
        # SET AFK ROUNDS
        # myPlayer.set('afkrounds', 2)
        if param == 'afkrounds':
            value1 = int(value1)
            if value1 > 0:
                if dict_gungame_core.has_key(self.userid):
                    dict_gungame_core[self.userid].int_afk_rounds = value1
            else:
                raise AFKValueError, 'AFK Rounds value must be greater than 0'
        
        # SET TRIPLE LEVEL
        # myPlayer.set('afkrounds', 2)
        if param == 'triple':
            value1 = int(value1)
            if value1 >= 0:
                if dict_gungame_core.has_key(self.userid):
                    dict_gungame_core[self.userid].int_triple_level = value1
            else:
                raise TripleValueError, 'Triple Level value must be equal to or greater than 0'
        
        # SET MULTIKILL
        # myPlayer.set('multikill', 3)
        if param == 'multikill':
            value1 = int(value1)
            if value1 > -1:
                if dict_gungame_core.has_key(self.userid):
                    dict_gungame_core[self.userid].int_multikill = value1
            else:
                raise MultiKillValueError, 'MultiKill value must be greater than -1'
        
        # SET EYEANGLE
        # myPlayer.set('eyeangle', #, #)
        if param == 'eyeangle':
            if value1 or value2:
                #es.setang(self.userid, value1, value2) ?
                es.server.cmd('es_setang %d %s %s' %(self.userid, eyeangle0, eyeangle1))
            gamethread.delayed(0.6,update_afk_dict,str(self.userid))
        
        # SET PREVENT LEVEL
        # myPlayer.set('PreventLevel', 1)
        if param == 'preventlevel':
            value1 = int(value1)
            if value1 == 0 or value1 == 1:
                if dict_gungame_core.has_key(self.userid):
                    dict_gungame_core[self.userid].int_prevent_level = value1
            else:
                raise ArgumentError, self.value1 + ' must be either 0 or 1'
    # ---------------------------------
    # END "SET" COMMANDS

    # BEGIN "GET" COMMANDS:
    # -------------------------------------
    # myPlayer = gungame.getPlayer(event_var['userid'])
    def get(self, param):
        #global dict_gungame_core
        param = str(param).lower()
        # GET ISPLAYERAFK
        # myPlayer.get('isplayerafk')
        if param == 'isplayerafk':
            if not es.isbot(self.userid):
                list_playerlocation = es.getplayerlocation(self.userid)
                afk_math_total = int(sum(list_playerlocation)) - list_playerlocation[2] + int(es.getplayerprop(self.userid,'CCSPlayer.m_angEyeAngles[0]')) + int(es.getplayerprop(self.userid,'CCSPlayer.m_angEyeAngles[1]'))
                if int(afk_math_total) == int(dict_afk[self.userid].int_afk_math_total):
                    return True
                else:
                    return False
            else:
                return False
        
        # GET AFK ROUNDS
        # myPlayer.get('afkrounds')
        if param == 'afkrounds':
            if dict_gungame_core.has_key(self.userid):
                return dict_gungame_core[self.userid].int_afk_rounds
        
        # GET TRIPLE LEVEL
        # myPlayer.get('triple')
        if param == 'triple':
            if dict_gungame_core.has_key(self.userid):
                return dict_gungame_core[self.userid].int_triple_level
        
        # GET LEVEL
        # myPlayer.get('level')
        if param == 'level':
            if dict_gungame_core.has_key(self.userid):
                return dict_gungame_core[self.userid].int_level
        
        # GET MULTIKILL
        # myPlayer.get('multikill')
        if param == 'multikill':
            if dict_gungame_core.has_key(self.userid):
                return dict_gungame_core[self.userid].int_multikill
        
# GET WEAPON
        # myPlayer.get('weapon')
        if param == 'weapon':
            if dict_gungame_core.has_key(self.userid):
                return dict_gungameWeaponOrder[self.get('level')]
            
        # GET PREVENT LEVEL
        # myPlayer.get('PreventLevel')
        if param == 'preventlevel':
            if dict_gungame_core.has_key(self.userid):
                return dict_gungame_core[self.userid].int_prevent_level
        
        # GET WINS
        # myPlayer.get('Wins')
        if param == 'wins':
            steamid = playerlib.uniqueid(self.userid, 1)
            if dict_gungameWinners.has_key(steamid):
                return dict_gungameWinners[steamid].int_wins
            else:
                return 0
    # ---------------------------------
    # END "GET" COMMANDS

# BEGIN ESS (OLDSCHOOL) COMMANDS
# ------------------------------------------------------
def ess_isafk():
    # gg_isafk <variable> <userid>
    if int(es.getargc()) == 3:
        userid = es.getargv(2)
        if es.exists('userid', userid):
            varName = es.getargv(1)
            gungamePlayer = gungame.getPlayer(userid)
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
            gungamePlayer = gungame.getPlayer(userid)
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
            gungamePlayer = gungame.getPlayer(userid)
            playerLevel = gungamePlayer.get('level')
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
            gungamePlayer = gungame.getPlayer(userid)
            gungamePlayer.set('level', es.getargv(2))
        else:
            raise UseridError, str(userid) + ' is an invalid userid'
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def ess_getleaderlevel():
    # gg_getleaderlevel <variable>
    if int(es.getargc()) == 2:
        varName = es.getargv(1)
        leaderLevel = gungame.getLeaderLevel()
        es.set(varName, leaderLevel)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def ess_getgungamevar():
    # gg_getgungamevar <variable> <variable name>
    if int(es.getargc()) == 3:
        varName = es.getargv(1)
        queriedVar = es.getargv(2)
        getGunGameVar(varName)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'
        
def ess_setgungamevar():
    # gg_setgungamevar <variable name> <value>
    if int(es.getargc()) == 3:
        varName = es.getargv(1)
        varValue = es.getargv(2)
        setGunGameVar(varName, varValue)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def ess_getpreventlevel():
    # gg_getpreventlevel <variable> <userid>
    if int(es.getargc()) == 3:
        varName = es.getargv(1)
        userid = es.getargv(2)
        gungamePlayer = gungame.getPlayer(userid)
        es.set(varName, gungamePlayer.get('preventlevel'))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'
        
def ess_setpreventlevel():
    # gg_setgungamevar <userid> <0 | 1>
    if int(es.getargc()) == 3:
        userid = es.getargv(1)
        preventValue = int(es.getargv(2))
        gungamePlayer = gungame.getPlayer(userid)
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
        gungamePlayer = gungame.getPlayer(userid)
        es.set(varName, gungamePlayer.get('weapon'))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'
    
def ess_giveweapon():
    # gg_giveweapon <userid>
    if int(es.getargc()) == 2:
        userid = es.getargv(1)
        giveWeapon(userid)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def ess_gettotallevels():
    if int(es.getargc()) == 2:
        varName = es.getargv(1)
        es.set(varName, getTotalLevels())
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def ess_setweapons():
    # gg_setweapons < #default | #random | #reversed >
    if int(es.getargc()) == 2:
        weaponOrder = es.getargv(1).lower()
        setGunGameVar('gg_weapon_order', weaponOrder)
        setWeapons(weaponOrder)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def ess_setweaponorderfile():
    # gg_setweaponorderfile <Path to File>
    if int(es.getargc()) == 2:
        weaponOrderFile = es.getargv(1)
        setGunGameVar('gg_weapon_order_file', weaponOrderFile)
        setWeaponOrderFile(getGunGameVar('gg_weapon_order_file'))
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
# ---------------------------------------------------
# END ESS (OLDSCHOOL) COMMANDS

# BEGIN Generic Gungame COMMANDS
# ---------------------------------------------------
def teleportPlayer(userid, x, y, z, eyeangle0=None, eyeangle1=None):
    userid = int(userid)
    # gungame.teleportPlayer(2, 1, 1, 1, 90, 180)
    es.server.cmd('es_setpos %d %s %s %s' %(userid, x, y, z))
    if eyeangle0 or eyeangle1:
        es.server.cmd('es_setang %d %s %s' %(userid, eyeangle0, eyeangle1))
    gamethread.delayed(0.6,update_afk_dict,userid)

def resetPlayerAfk(userid):
    # gungame.resetPlayerAfk(2)
    update_afk_dict(userid)

def getLeaderLevel():
    global dict_gungame_core
    leaderLevel = 0
    for userid in dict_gungame_core:
        if int(dict_gungame_core[userid].int_level) > leaderLevel:
            leaderLevel = int(dict_gungame_core[userid].int_level)
    return leaderLevel

def getAverageLevel():
    global dict_gungame_core
    averageLevel = 0
    averageDivider = 0
    for userid in dict_gungame_core:
        averageDivider += 1
        averageLevel += int(dict_gungame_core[userid].int_level)
    if averageDivider:
        return int(round(averageLevel / averageDivider))
    else:
        return 0

def getGunGameVar(variableName):
    # gungame.getGunGameVar('gg_afk_punish')
    global dict_gungameVariables
    variableName = str(variableName.lower())
    if dict_gungameVariables.has_key(variableName):
        return dict_gungameVariables[variableName]

def setGunGameVar(variableName, variableValue):
    # gungame.setGunGameVar('gg_afk_punish', 2)
    global dict_gungameVariables
    # Change the variable name to lower case
    variableName = str(variableName.lower())
    # Make sure the GunGame Variables Dictionary contains this variable name
    if dict_gungameVariables.has_key(variableName):
        # See if whoever issue the command is actually changing the value of the variable in the dictionary
        if str(getGunGameVar(variableName)) != str(variableValue):
            # Initialize the event "gg_variable_changed"
            es.event('initialize', 'gg_variable_changed')
            # Set the cvar name that is being changed
            es.event('setstring', 'gg_variable_changed', 'cvarname', variableName)
            # Set the old value of the variable that is being changed
            es.event('setstring', 'gg_variable_changed', 'oldvalue', getGunGameVar(variableName))
            # Set the new value of the variable being changed
            es.event('setstring', 'gg_variable_changed', 'newvalue', variableValue)
            # Fire the event "gg_variable_changed"
            es.event('fire', 'gg_variable_changed')
            # Change the value in the GunGame Variables Dictionary
            dict_gungameVariables[variableName] = variableValue
            # Set the variable's value in the Valve Console
            es.set(variableName, variableValue)
    else:
        # Oops, this variable doesn't exist in the GunGame Variables Dictionary
        raise VariableError, str(variableName) + ' is not a valid GunGame variable'

def setGlobal(variableName, variableValue):
    global dict_globals
    dict_globals[variableName] = str(variableValue)

def getGlobal(variableName):
    global dict_globals
    # Does the variable exist?
    if dict_globals.has_key(variableName):
        return dict_globals[variableName]
    else:
        return '0'

def giveWeapon(userid):
    if es.exists('userid', userid):
        gungamePlayer = gungame.getPlayer(userid)
        if int(es.getplayerteam(userid)) > 1 and not gungamePlayer.attributes['isdead']:
            playerWeapon = gungamePlayer.get('weapon')
            if playerWeapon != 'knife':
                es.server.cmd('es_xdelayed 0.001 es_xgive %s weapon_%s' %(userid, playerWeapon))
    else:
        raise UseridError, str(userid) + ' is an invalid userid'

def setWeapons(weaponOrder):
    #gungame.setWeapons(string)
    global dict_gungameWeapons
    global dict_gungameWeaponOrder
    global gungameWeaponOrderMenu
    weaponOrderPath = os.getcwd() + '/cstrike/cfg/gungame/weapon_order/' + getGunGameVar('gg_weapon_order_file')
    weaponOrder = str(weaponOrder.lower())
    if weaponOrder == '#default':
        dict_gungameWeaponOrder = {}
        dict_gungameWeaponOrder = dict_gungameWeapons
        logWeaponOrder('Loading', weaponOrderPath)
        restartGunGame('Weapon Order Changed to \'\x03#default\x01\'...Restarting.')
        buildWeaponOrderMenu()
    elif weaponOrder == '#reversed':
        dict_gungameWeaponOrder = {}
        list_gungameLevels = dict_gungameWeapons.keys()
        list_gungameWeapons = dict_gungameWeapons.values()
        list_gungameWeapons.reverse()
        weaponArrayNumber = 0
        for level in list_gungameLevels:
            dict_gungameWeaponOrder[level] = list_gungameWeapons[weaponArrayNumber]
            weaponArrayNumber += 1
        logWeaponOrder('Reversing', weaponOrderPath)
        restartGunGame('Weapon Order Changed to \'\x03#reversed\x01\'...Restarting.')
        buildWeaponOrderMenu()
    elif weaponOrder == '#random':
        dict_gungameWeaponOrder = {}
        list_gungameLevels = dict_gungameWeapons.keys()
        random.shuffle(list_gungameLevels)
        list_gungameWeapons = dict_gungameWeapons.values()
        random.shuffle(list_gungameWeapons)
        weaponArrayNumber = 0
        for level in list_gungameLevels:
            dict_gungameWeaponOrder[level] = list_gungameWeapons[weaponArrayNumber]
            weaponArrayNumber += 1
        logWeaponOrder('Randomizing', weaponOrderPath)
        restartGunGame('Weapon Order Changed to \'\x03#random\x01\'...Restarting.')
        buildWeaponOrderMenu()
    else:
        es.dbgmsg(0, '[GunGame] \'%s\' is an invalid choice for the weapon order. Choices are: #default #reversed #random' %weaponOrder)

def getLevelWeapon(levelNumber):
    levelNumber = int(levelNumber)
    if dict_gungameWeaponOrder.has_key(levelNumber):
        return str(dict_gungameWeaponOrder[levelNumber])
        
def getLevelUseridList(levelNumber):
    global dict_gungame_core
    levelNumber = int(levelNumber)
    list_levelUserids = []
    for userid in dict_gungame_core:
        if dict_gungame_core[int(userid)].int_level == levelNumber:
            list_levelUserids.append(userid)
    return list_levelUserids

def getTotalLevels():
    global dict_gungameWeaponOrder
    list_weaponOrderKeys = dict_gungameWeaponOrder.keys()
    return int(len(list_weaponOrderKeys))

def stripPlayer(userid):
    playerlibPlayer = playerlib.getPlayer(userid)
    playerlibPrimary = playerlibPlayer.get('primary')
    playerlibSecondary = playerlibPlayer.get('secondary')
    if playerlibPrimary:
        es.server.cmd('es_xremove %d' %int(playerlibPlayer.get('weaponindex', playerlibPrimary)))
    if playerlibSecondary:
        es.server.cmd('es_xremove %d' %int(playerlibPlayer.get('weaponindex', playerlibSecondary)))

def registerAddon(addonName, menuText):
    global dict_gungameRegisteredAddons
    addonName = addonName.replace('/', '\\')
    menuText = str(menuText)
    # Make sure that this addon has not already been registered as a GunGame Addon
    if not dict_gungameRegisteredAddons.has_key(addonName):
        if menuText != '':
            # Add the addon to the GunGame Registered Addons List
            dict_gungameRegisteredAddons[addonName] = menuText
            # Send a message to console stating that the addon has been successfully registered with GunGame
            es.dbgmsg(0, '[GunGame] Addon Registered Successfully: \'%s\'' %addonName)
    else:
        # Send an error message to console stating that the addon has been previously registered with GunGame
        es.dbgmsg(0, '[GunGame] Addon Registration Failed. \'%s\' has already been registered.' %addonName)

def unregisterAddon(addonName):
    global dict_gungameRegisteredAddons
    addonName = addonName.replace('/', '\\')
    # Make sure that this addon has been registered as a GunGame Addon
    if dict_gungameRegisteredAddons.has_key(addonName):
        # Remove the addon to the GunGame Registered Addons List
        del dict_gungameRegisteredAddons[addonName]
        # Send a message to console stating that the addon has been successfully unregistered with GunGame
        es.dbgmsg(0, '[GunGame] Addon Unregistered Successfully: \'%s\'' %addonName)
    else:
        # Send an error message to console stating that the addon has not been previously registered with GunGame
        es.dbgmsg(0, '[GunGame] Addon Unregistration Failed. \'%s\' has not been previously registered.' %addonName)

def checkRegisteredAddon(addonName):
    global dict_gungameRegisteredAddons
    addonName = addonName.replace('/', '\\')
    # Check if this addon is registered as a GunGame Addon
    if dict_gungameRegisteredAddons.has_key(addonName):
        return 1
    return 0

def getRegisteredAddons():
    global dict_gungameRegisteredAddons
    return dict_gungameRegisteredAddons
    
def registerDependency(dependencyName, addonName):
    global dict_gungameRegisteredAddons
    global dict_gungameRegisteredDependencies
    dependencyName = dependencyName.replace('/','\\')
    addonName = addonName.replace('/', '\\')
    # Make sure that this addon is registered as a GunGame Addon
    if dict_gungameRegisteredAddons.has_key(addonName):
        # Check if addon is already a registered as a GunGame Dependency
        if dict_gungameRegisteredDependencies.has_key(dependencyName):
            # Check if this addon already registered this dependency
            if addonName not in dict_gungameRegisteredDependencies[dependencyName]:
                dict_gungameRegisteredDependencies[dependencyName].append(addonName)
                # Send a message to console stating that the depenency has been successfully unregistered with GunGame
                es.dbgmsg(0, '[GunGame] Dependency Registered Successfully: \'%s\'' %dependencyName)
            else:
                # Send an error message to console stating that the addon has been previously registered to this depependency
                es.dbgmsg(0, '[GunGame] Dependency Registered Failed. \'%s\' has already been registered to \'%s\'' %(addonName,dependencyName))
        else:
            dict_gungameRegisteredDependencies[dependencyName] = [addonName]
            # Send a message to console stating that the depenency has been successfully unregistered with GunGame
            es.dbgmsg(0, '[GunGame] Dependency Registered Successfully: \'%s\'' %dependencyName)
    else:
        # Send an error message to console stating that the addon is not a registered addon
        es.dbgmsg(0, '[GunGame] Dependency Registration Failed. \'%s\' is not a registered addon.' %addonName)

def unregisterDependency(dependencyName, addonName):
    global dict_gungameRegisteredDependencies
    dependencyName = dependencyName.replace('/','\\')
    addonName = addonName.replace('/', '\\')
    # Check if addon is already a registered as a GunGame Dependency
    if dict_gungameRegisteredDependencies.has_key(dependencyName):
        # Check if this addon already registered this dependency
        if addonName in dict_gungameRegisteredDependencies[dependencyName]:
            dict_gungameRegisteredDependencies[dependencyName].remove(addonName)
            # Send a message to console stating that the depenency has been successfully unregistered with GunGame
            es.dbgmsg(0, '[GunGame] Dependency Unregistered Successfully: \'%s\'' %dependencyName)
            # Remove dependency from dict if it has no more addons
            if not len(dict_gungameRegisteredDependencies[dependencyName]):
                del dict_gungameRegisteredDependencies[dependencyName]
        else:
            # Send an error message to console stating that the addon has been previously registered to this depependency
            es.dbgmsg(0, '[GunGame] Dependency Unregistered Failed. \'%s\' is not registered to \'%s\'' %(addonName,dependencyName))
    else:
        # Send an error message to console stating that the addon is not a registered addon
        es.dbgmsg(0, '[GunGame] Dependency Unregistration Failed. \'%s\' is not a registered dependency.' %addonName)

def checkDependency(dependencyName):
    global dict_gungameRegisteredDependencies
    dependencyName = dependencyName.replace('/','\\')
    # Check to see if addon is a registered dependency
    if dict_gungameRegisteredDependencies.has_key(dependencyName):
        return 1
    else:
        return 0

def getAddonDependencyList(dependencyName):
    global dict_gungameRegisteredDependencies
    dependencyName = dependencyName.replace('/','\\')
    dependencyList = []
    if dict_gungameRegisteredDependencies.has_key(dependencyName):
        for addon in dict_gungameRegisteredDependencies[dependencyName]:
            dependencyList.append(addon)
    return dependencyList

def getRegisteredDependencies():
    global dict_gungameRegisteredDependencies
    return dict_gungameRegisteredDependencies

def getIncludedAddonsDirList():
    global list_includedAddonsDir
    return list_includedAddonsDir
    
def getCustomAddonsDirList():
    global list_customAddonsDir
    return list_customAddonsDir
# -----------------------------------------------
# END Generic Gungame COMMANDS

def logWeaponOrder(text, weaponOrderPath):
    # The entire function of this module is to simply echo the weapon order to the log file
    global dict_gungameWeaponOrder
    es.dbgmsg(0, '')
    es.dbgmsg(0, '[GunGame] %s Weapons from \'%s\':' %(text, weaponOrderPath))
    for level in dict_gungameWeaponOrder:
        if level < 10:
            # Echo the GunGame Weapon Order text to the console
            es.dbgmsg(0, '    0%d. %s' %(level, dict_gungameWeaponOrder[level]))
        else:
            # Echo the GunGame Weapon Order text to the console
            es.dbgmsg(0, '    %d. %s' %(level, dict_gungameWeaponOrder[level]))
    es.dbgmsg(0, '')
    global list_weaponOrderErrors
    # If there are any errors in the weapon order, we will echo them here
    if len(list_weaponOrderErrors):
        for errorText in list_weaponOrderErrors:
            es.dbgmsg(0, list_weaponOrderErrors.pop())
        es.dbgmsg(0, '')

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
    gungamePlayer = gungame.getPlayer(userid)
    afkMaxAllowed = int(getGunGameVar('gg_afk_rounds'))
    if afkMaxAllowed > 0:
        # Increment the "int_afk_rounds" for this player in the GunGame Core Dictionary
        gungamePlayer.set('afkrounds', (int(gungamePlayer.get('afkrounds')) + 1))
        # If they have been AFK for too many rounds, we proceed beyond the below check
        if int(gungamePlayer.get('afkrounds')) >= afkMaxAllowed:
            if int(getGunGameVar('gg_afk_action')) == 1:
                # Kick the player from the server for being AFK for the maximum number of rounds
                es.server.cmd('kickid %d \"AFK too long.\"' %userid)
            elif int(getGunGameVar('gg_afk_action')) == 2:
                # Set the player's team to spectator for being AFK for the maximum number of rounds
                es.server.cmd('es_xfire %d !self setteam 1' %userid)
                # POPUP!!! "You were switched to Spectator\n for being AFK!\n \n----------\n->0. Exit" 

def equipPlayer():
    userid = es.getuserid()
    es.server.cmd('es_xremove game_player_equip')
    es.server.cmd('es_xgive %s game_player_equip' %userid)
    es.server.cmd('es_xfire %s game_player_equip addoutput \"weapon_knife 1\"' %userid)
    
    # Retrieve the armor type
    armorType = int(getGunGameVar('gg_player_armor'))
    
    if armorType == 2:
    # Give the player full armor
        es.server.cmd('es_xfire %s game_player_equip addoutput \"item_assaultsuit 1\"' %userid)
    # Give the player kevlar only
    elif armorType == 1:
        es.server.cmd('es_xfire %s game_player_equip addoutput \"item_kevlar 1\"' %userid)

def registerPlayers():
    global dict_afk
    global dict_gungame_core
    global dict_reconnectingPlayers
    global list_leaderNames
    global dict_gungameWinners
    
    # Set Up/Clear the AFK Dictionary
    dict_afk = {}
    
    # Set Up/Clear the GunGame Core Dictionary
    dict_gungame_core = {}
    
    # Set Up/Clear the Reconnecting Players Dictionary
    dict_reconnectingPlayers = {}
    
    # Reset the leader names list
    list_leaderNames = []
    
    # Set up a custom variable for tracking the leader level in dict_gungameVariables
    dict_gungameVariables['oldleaderlevel'] = 1

    # BEGIN PLAYER SETUP CODE
    # ---------------------------------------
    for userid in es.getUseridList():
        userid = int(userid)
        steamid = playerlib.uniqueid(userid, 1)
        # BEGIN AFK CODE
        # ------------------------
        if not dict_afk.has_key(userid) and not es.isbot(userid):
            dict_afk[userid] = afkPlayers()
            gamethread.delayed(1, update_afk_dict, userid)
        # ---------------------
        # END AFK CODE
        
        # BEGIN GUNGAME CORE DATABASE CODE
        # ---------------------------------------------------------
        if not dict_gungame_core.has_key(userid):
            dict_gungame_core[userid] = gungamePlayers()
            dict_gungame_core[userid].str_steamid = steamid
        # ------------------------------------------------------
        # END GUNGAME CORE DATABASE CODE
        
        # See if the player has won before
        if int(getGunGameVar('gg_save_winners')) > 0:
            if dict_gungameWinners.has_key(steamid):
                # Yes, they have won before...let's be nice and update their timestamp
                dict_gungameWinners[steamid].int_timestamp = es.gettime()

    # -----------------------------------
    # END PLAYER SETUP CODE
    
    
    
    # Reset the leader names
    buildLeaderMenu()

def rebuildLeaderNameList():
    global dict_gungame_core
    global list_leaderNames
    leaderLevel = int(getLeaderLevel())
    list_leaderNames = []
    for userid in dict_gungame_core:
        if int(dict_gungame_core[userid].int_level) == leaderLevel:
            list_leaderNames.append(es.getplayername(userid))

def restartGunGame(reasonText=None):
    if reasonText:
        reasonText = '\x04[\x03GunGame\x04]\x01 ' + reasonText
    registerPlayers()
    setPreventLevelAll(1)
    gamethread.delayedname(4.5, 'setPreventAll0', setPreventLevelAll, (0))
    es.server.cmd('mp_restartgame 5')
    # Check to see if the warmup round needs to be activated
    if int(getGunGameVar('gg_warmup_timer')) > 0:
        gamethread.delayed(5, es.load, ('gungame/included_addons/gg_warmup_round'))
    else:
        # Fire gg_start event
        gamethread.delayed(5, es.event, ('initialize','gg_start'))
        gamethread.delayed(5, es.event, ('fire','gg_start'))
    es.msg(reasonText)
    gamethread.delayed(2, es.centermsg, ('GunGame Restarting!!!'))

def setPreventLevelAll(value):
    for userid in es.getUseridList():
        gungamePlayer = gungame.getPlayer(userid)
        gungamePlayer.set('preventlevel', int(value))

def setWeaponOrderFile(fileName):
    # BEGIN READING THE "../cstrike/cfg/gungame/weapon_order/%FILENAME%" FOR THE WEAPON ORDER
    # ----------------------------------------------------------------------------------------------------------------------------

    # All globals go at the top. Initialize them outside of functions, if possible
    global dict_gungameWeapons
    global dict_gungameWeaponOrder
    global list_weaponOrderErrors

    # Generic Dictionary that holds the information from the '/cstrike/cfg/gungame/weapon_order.txt', level information and weapons
    dict_gungameWeapons = {}
    # Actual dictionary that holds the level information and weapons used in-game
    dict_gungameWeaponOrder = {}
    
    weaponOrderPath = os.getcwd() + '/cstrike/cfg/gungame/weapon_order/' + fileName
    
    # Create a list of "valid weapons" to keep the admins from accidental typos, although this will never possibly happen. :p
    list_validWeapons = ['glock','usp','p228','deagle','fiveseven','elite','m3','xm1014','tmp','mac10','mp5navy','ump45','p90','galil','famas','ak47','scout','m4a1','sg550','g3sg1','awp','sg552','aug','m249','hegrenade','knife']
    if os.path.isfile(weaponOrderPath):
        list_weaponOrderErrors = []
        # Open the 'cstrike/cfg/gungame/weapon_order.txt'
        weaponOrderFile = open(weaponOrderPath, 'r')
        # Echo the GunGame Weapon Order text to the console
        levelCount = 0
        # Loop through each line in the 'cstrike/cfg/gungame/weapon_order.txt'
        for line in weaponOrderFile.readlines():
            # Strip the spaces from the beginning/end of each line and convert to lower case
            line = line.strip().lower()
            # Make sure that the line doesn't being with '//'
            if not line.startswith('//'):
                # Make sure that the admin didn't typo the weapons by checking against the list_validWeapons
                if line in list_validWeapons:
                    # Now that we have verified it is a valid weapon, increment the level counter
                    levelCount += 1
                    # Add the valid weapon to the GunGame Weapons Dictionary
                    dict_gungameWeapons[levelCount] = line
                else:
                    # Let's not echo blank lines to the console as an "invalid weapon." That might confuse someone. ;)
                    if line:
                        # Uh-oh! The admin typoed a weapon name. Let's warn them by echoing this to the console.
                        list_weaponOrderErrors.append('[GunGame] \'%s\' is not a valid weapon: skipping.' %line)
        if not dict_gungameWeapons:
            # Heh...the admin has deleted all valid weapons or typoed every last one of them. Let's echo this to the console and unload GunGame.
            es.dbgmsg(0, '[GunGame] There are no valid weapons listed in \'%s\': Unloading GunGame.' %weaponOrderPath)
            es.server.queuecmd('es_xunload gungame')
        else:
            setWeapons(getGunGameVar('gg_weapon_order'))
            #dict_gungameWeaponOrder = dict_gungameWeapons
            #logWeaponOrder('Loading', weaponOrderPath)
        # Close the file and remove it from memory
        weaponOrderFile.close()

    else:
        # Oh boy...the admin of this server must have typoed or deleted the file. Let's echo that to console and unload GunGame.
        if fileName != 'default_weapon_order.txt':
            es.dbgmsg(0, 'Unable to open \'%s\' ::: File does not exist. ::: Attempting to load default weapon order file...' %weaponOrderPath)
            setWeaponOrderFile('default_weapon_order.txt')
        else:
            es.dbgmsg(0, 'Unable to open \'%s\' ::: File does not exist. ::: Unloading GunGame.' %weaponOrderPath)
            es.server.queuecmd('es_xunload gungame')
    # ------------------------------------------------------------------------------------------------------------------------
    # END READING THE "../cstrike/cfg/gungame/weapon_order/%FILENAME%" FOR THE WEAPON ORDER

def loadConfig(configPath):
    global dict_gungameVariables
    # BEGIN READING THE  CONFIG OPTIONS
    # ---------------------------------------------------------
    if os.path.isfile(configPath):
        # Open the Config
        gungameConfig = open(configPath, 'r')
        # Loop through each line in the Config
        for line in gungameConfig.readlines():
            # Strip the spaces from the begninning and end of each line
            line = line.strip().lower()
            # Make sure that the line doesn't begin with '//'
            if not line.startswith('//'):
                # Change the text to lowercase and convert to a string
                if line:
                    # Add the variables and values to dict_gungameVariables
                    list_variables = line.split()
                    # If the variable has not been added to the GunGame Variables Database
                    if not dict_gungameVariables.has_key(list_variables[0]):
                        # Add the variable and value to the GunGame Variables Database
                        dict_gungameVariables[list_variables[0]] = list_variables[1]
                        # Create console variables
                        es.ServerVar(list_variables[0]).set(list_variables[1])
                        # See if this is our "gg_default_addons.cfg" and trigger the event "gg_variable_changed"
                        if configPath == os.getcwd() + '/cstrike/cfg/gungame/gg_default_addons.cfg' or configPath == os.getcwd() + '/cstrike/cfg/gungame/gg_en_config.cfg':
                            # Initialize the event "gg_variable_changed"
                            es.event('initialize', 'gg_variable_changed')
                            # Set the cvar name that is being changed
                            es.event('setstring', 'gg_variable_changed', 'cvarname', list_variables[0])
                            # Set the old value of the variable that is being changed
                            es.event('setstring', 'gg_variable_changed', 'oldvalue', list_variables[1])
                            # Set the new value of the variable being changed
                            es.event('setstring', 'gg_variable_changed', 'newvalue', list_variables[1])
                            # Fire the event "gg_variable_changed"
                            es.event('fire', 'gg_variable_changed')
                    else:
                        es.dbgmsg(0, '[GunGame] \'%s\' has already been added to the GunGame Variables Database...skipping.' %list_variables[0])
        es.dbgmsg(0, '')
        es.dbgmsg(0, '[GunGame] \'%s\' has been successfully loaded.' %configPath)
        es.dbgmsg(0, '')
    else:
        if configPath != os.getcwd() + '/cstrike/cfg/gungame/gg_en_config.cfg' or configPath != os.getcwd() + '/cstrike/cfg/gungame/gg_default_addons.cfg':
            # We can't load it if it doesn't exist, silly rabbit!
            es.dbgmsg(0, '[GunGame] Unable to load the Config: \'%s\' ::: File does not exist. :::' %configPath)
        else:
            # Strange. I know that I provided them with these files...yet, they seem to have disappeared!
            es.dbgmsg(0, '[GunGame] Unable to load the Config: \'%s\' ::: File does not exist. ::: Unloading GunGame.' %configPath)
            es.server.queuecmd('es_xunload gungame')
    # -----------------------------------------------------
    # END READING THE CONFIG OPTIONS

def unloadConfig(configPath):
    # BEGIN READING THE  CONFIG OPTIONS
    # ---------------------------------------------------------
    try:
        if configPath != os.getcwd() + '/cstrike/cfg/gungame/gg_en_config.cfg' or configPath != os.getcwd() + '/cstrike/cfg/gungame/gg_default_addons.cfg':
            # Open the Config
            gungameConfig = open(configPath, 'r')
            # Loop through each line in the Config
            for line in gungameConfig:
                # Strip the spaces from the begninning and end of each line
                line = line.strip().lower()
                # Make sure that the line doesn't begin with '//'
                if not line.startswith('//'):
                    if line != '':
                        # Add the variables and values to dict_gungameVariables
                        list_variables = line.split()
                        # If the variable exists in the GunGame Variables Database
                        if dict_gungameVariables.has_key(str(list_variables[0])):
                            # Add the variable and value to the GunGame Variables Database
                            del dict_gungameVariables[str(list_variables[0])]
                            # Set Console Variable to "unloaded"
                            es.set(str(list_variables[0]), 'unloaded')
            es.dbgmsg(0, '')
            es.dbgmsg(0, '[GunGame] \'%s\' has been successfully unloaded.' %configPath)
            es.dbgmsg(0, '')
    except IOError:
        # We can't unload the config from GunGame if it doesn't exist, now can we?
        es.dbgmsg(0, '[GunGame] Unable to unload Config: \'%s\' ::: File does not exist. :::' %configPath)
# ===================================================================================================
# ===================================================================================================
#          !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! END GUNGAME COMMANDS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
# ===================================================================================================
# ===================================================================================================


# ===================================================================================================
# ===================================================================================================
#             !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! BEGIN GAME EVENTS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
# ===================================================================================================
# ===================================================================================================
def load():
    StartProfiling(g_Prof)
    
    global list_includedAddonsDir
    global list_customAddonsDir
    global dict_gungameVariables
    global dict_gungameWinners
    global countBombDeathAsSuicide
    
    # LOAD CUSTOM GUNGAME EVENTS
    es.loadevents('declare', 'addons/eventscripts/gungame/events/es_gungame_events.res')
    
    # Load the "../cstrike/cfg/gungame/gg_en_config.cfg"
    loadConfig(os.getcwd() + '/cstrike/cfg/gungame/gg_en_config.cfg')
    StopProfiling(g_Prof)
    
    # Load the "../cstrike/cfg/gungame/gg_default_addons.cfg"
    loadConfig(os.getcwd() + '/cstrike/cfg/gungame/gg_default_addons.cfg')
    
    # Load the "../cstrike/cfg/gungame/gg_map_vote.cfg"
    gungame.loadConfig(os.getcwd() + '/cstrike/cfg/gungame/gg_map_vote.cfg')
    
    # Get the scripts in the "../cstrike/addons/eventscripts/gungame/included_addons" folder
    list_includedAddonsDir = []
    for includedAddon in os.listdir(os.getcwd() + '/cstrike/addons/eventscripts/gungame/included_addons/'):
        if includedAddon[0:3] == 'gg_':
            list_includedAddonsDir.append(includedAddon)
    
    # Get the scripts in the "../cstrike/addons/eventscripts/gungame/custom_addons" folder
    list_customAddonsDir = []
    for customAddon in os.listdir(os.getcwd() + '/cstrike/addons/eventscripts/gungame/custom_addons/'):
        if customAddon[0:3] == 'gg_':
            list_customAddonsDir.append(customAddon)
    
    # See if we need to create a list of strip exceptions
    global list_stripExceptions
    if getGunGameVar('gg_map_strip_exceptions') != '0':
        # Create a list of stripping exceptions using the 'gg_map_strip_exceptions' variable
        list_stripExceptions = dict_gungameVariables['gg_map_strip_exceptions'].split(',')
    
    # Open the weapon order file
    setWeaponOrderFile(getGunGameVar('gg_weapon_order_file'))
    
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
    # GG_GETLEADERLEVEL
    if not es.exists('command', 'gg_getleaderlevel'):
        es.regcmd('gg_getleaderlevel', 'gungame/ess_getleaderlevel', 'Returns the leader level')
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
    # ---------------------------------------------------
    # END ESS COMMAND REGISTRATION
    
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
    if int(getGunGameVar('gg_save_winners')) > 0:
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
    registerPlayers()
    
    # Set Up a custom variable for voting in dict_gungameVariables
    dict_gungameVariables['gungame_voting_started'] = False
    
    # Set up a custom variable for tracking the leader level in dict_gungameVariables
    dict_gungameVariables['oldleaderlevel'] = 1

    # If there is a current map listed, then the admin has loaded GunGame mid-round/mid-map
    if str(es.ServerVar('eventscripts_currentmap')) != '':
        # Check to see if the warmup round needs to be activated
        if int(getGunGameVar('gg_warmup_timer')) > 0:
            es.load('gungame/included_addons/gg_warmup_round')
        else:
            # Fire gg_start event
            es.event('initialize','gg_start')
            es.event('fire','gg_start')
    
    # RESTART CURRENT MAP
    es.server.cmd('mp_restartgame 2')
    es.msg('#multi', '\x04[\x03GunGame\x04]\x01 Loaded')
    
    # GET MAP PREFIX
    list_mapPrefix = str(es.ServerVar('eventscripts_currentmap')).split('_')
    mapPrefix = list_mapPrefix[0]
    dict_gungameVariables['gungame_currentmap_prefix'] = list_mapPrefix[0]

    # Create a variable to prevent bomb explosion deaths from counting a suicides
    countBombDeathAsSuicide = False

    StopProfiling(g_Prof)
    #es.msg("Load benchmark: %f seconds" % GetProfilerTime(g_Prof))
    
    # Load gg_sounds
    es.load('gungame/included_addons/gg_sounds')
    
    # Fire gg_load event
    es.event('initialize','gg_load')
    es.event('fire','gg_load')

def es_map_start(event_var):
    #Load custom GunGame events
    es.loadevents('declare', 'addons/eventscripts/gungame/events/es_gungame_events.res')
    
    # Execute GunGame's autoexec.cfg
    es.server.cmd('es_xdelayed 1 exec gungame/autoexec.cfg')
    
    # Split the map name into a list separated by "_"
    list_mapPrefix = event_var['mapname'].split('_')
    
    # Insert the new map prefix into the GunGame Variables
    setGunGameVar('gungame_currentmap_prefix', list_mapPrefix[0])
    
    # Reset the "gungame_voting_started" variable
    setGunGameVar('gungame_voting_started', False)
    
    # See if the option to randomize weapons is turned on
    if getGunGameVar('gg_weapon_order') == '#random':
        # Randomize the weapon order
        setWeapons('#random')
    
    # Check to see if the warmup round needs to be activated
    if int(getGunGameVar('gg_warmup_timer')) > 0:
        es.load('gungame/included_addons/gg_warmup_round')
    else:
        # Fire gg_start event
        es.event('initialize','gg_start')
        es.event('fire','gg_start')
    
    # Reset the GunGame Round
    registerPlayers()

def player_changename(event_var):
    global list_leaderNames
    # Change the player's name in the leaderlist
    if event_var['oldname'] in list_leaderNames:
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
    mapObjectives = int(getGunGameVar('gg_map_obj'))
    
    # Get the map prefix for the following checks
    mapPrefix = getGunGameVar('gungame_currentmap_prefix')
    
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
        if int(getGunGameVar('gg_afk_rounds')) > 0:
            # Create a list of userids of human players that were alive at the end of the round
            list_playerlist = playerlib.getUseridList('#alive,#human')
            # Now, we will loop through the userid list and run the AFK Punishment Checks on them
            for userid in list_playerlist:
                gungamePlayer = gungame.getPlayer(userid)
                # Check to see if the player was AFK
                if gungamePlayer.get('isplayerafk'):
                    # See if the player needs to be punished for being AFK
                    afkPunishCheck(int(userid))
    StopProfiling(g_Prof)
    #es.msg("Event round_end benchmark: %f seconds" % GetProfilerTime(g_Prof))

def player_activate(event_var):
    StartProfiling(g_Prof)
    global dict_gungameWinners
    userid = int(event_var['userid'])
    steamid = playerlib.uniqueid(userid, 1)
    # BEGIN AFK CODE
    # ------------------------
    if not dict_afk.has_key(userid) and not es.isbot(userid):
        dict_afk[userid] = afkPlayers()
    # ---------------------
    # END AFK CODE
    
    # BEGIN GUNGAME CORE DATABASE CODE
    # ---------------------------------------------------------
    if not dict_gungame_core.has_key(userid):
        dict_gungame_core[userid] = gungamePlayers()
        dict_gungame_core[userid].str_steamid = steamid
    # ------------------------------------------------------
    # END GUNGAME CORE DATABASE CODE
    
    # See if the player has won before
    if int(getGunGameVar('gg_save_winners')) > 0:
        if dict_gungameWinners.has_key(steamid):
            # Yes, they have won before...let's be nice and update their timestamp
            dict_gungameWinners[steamid].int_timestamp = es.gettime()
    
    # See if this player was set up in the Reconnecting Players Dictionary
    if dict_reconnectingPlayers.has_key(steamid):
        # Yes, they were. Therefore, we set their level to be whatever it needs to be
        dict_gungame_core[userid].int_level = dict_reconnectingPlayers[steamid]
        # Delete the player from the Reconnecting Players Dictionary
        del dict_reconnectingPlayers[steamid]
    
    if int(getGunGameVar('gg_save_winners')) > 0:
        # See if the player has won before
        if dict_gungameWinners.has_key(steamid):
            # Update the player's timestamp since they have won before
            dict_gungameWinners[steamid].int_timestamp = es.gettime()
    StopProfiling(g_Prof)
    #es.msg("Event player_activate benchmark: %f seconds" % GetProfilerTime(g_Prof))
    
def player_disconnect(event_var):
    StartProfiling(g_Prof)
    global dict_reconnectingPlayers
    userid = int(event_var['userid'])
    
    # Make sure the player is not a BOT
    if not es.isbot(userid):
        # See if this player is already in the Reconnecting Players Dictionary (shouldn't ever be, but we will check anyhow, just to be safe)
        if not dict_reconnectingPlayers.has_key(dict_gungame_core[userid].str_steamid):
            # Set this player up in the Reconnecting Players Dictionary
            dict_reconnectingPlayers[dict_gungame_core[userid].str_steamid] = int(dict_gungame_core[userid].int_level) - int(getGunGameVar('gg_retry_punish'))
    
    # BEGIN AFK CODE
    # ------------------------
    if dict_afk.has_key(userid) and not es.isbot(userid):
        del dict_afk[userid]
    # ---------------------
    # END AFK CODE
    
    # BEGIN GUNGAME CORE DATABASE CODE
    # ----------------------------------------------------------
    if dict_gungame_core.has_key(userid):
        del dict_gungame_core[userid]
    # ------------------------------------------------------
    # END GUNGAME CORE DATABASE CODE
    StopProfiling(g_Prof)
    #es.msg("Event player_disconnect benchmark: %f seconds" % GetProfilerTime(g_Prof))

def player_spawn(event_var):
    StartProfiling(g_Prof)
    userid = int(event_var['userid'])
    
    # Make sure the player exists in the GunGame Core Database
    if dict_gungame_core.has_key(userid):
        gungamePlayer = gungame.getPlayer(userid)
        if int(event_var['es_userteam']) > 1:
            # BEGIN AFK CODE
            # ------------------------
            gamethread.delayed(0.6, update_afk_dict, userid)
            # ---------------------
            # END AFK CODE
            
            # Strip the player
            stripPlayer(userid)
            
            # Check to see if the WarmUp Round is Active
            if not dict_gungameRegisteredAddons.has_key('gungame\\included_addons\\gg_warmup_round'):
                # Since the WarmUp Round is not Active, give the player the weapon relevant to their level
                giveWeapon(userid)
                
                # Get leader level
                leaderLevel = int(getLeaderLevel())
                
                if leaderLevel < 2:
                    HudHintText = 'Current level: %d of %d\nCurrent weapon: %s' %(gungamePlayer.get('level'), getTotalLevels(), gungamePlayer.get('weapon'))
                else:
                    # Get levels behind leader
                    levelsBehindLeader = leaderLevel - gungamePlayer.get('level')
                    # Get list of leaders userids
                    list_leadersUserid = getLevelUseridList(leaderLevel)
                    # How many levels behind the leader?
                    if levelsBehindLeader == 0:
                        # Is there more than 1 leader?
                        if len(list_leadersUserid) == 1:    
                            HudHintText = 'Current level: %d of %d\nCurrent weapon: %s\n\nYou are the leader.' % (gungamePlayer.get('level'), getTotalLevels(), gungamePlayer.get('weapon'))
                        else:
                            HudHintText = 'Current level: %d of %d\nCurrent weapon: %s\n\nYou are amongst the leaders (' % (gungamePlayer.get('level'), getTotalLevels(), gungamePlayer.get('weapon'))
                            leadersCount = 0
                            
                            # Get the first 2 leaders
                            for leader in list_leadersUserid:
                                # Increment leader count
                                leadersCount += 1
                                
                                # Already 2 leaders added?
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
                        HudHintText = 'Current level: %d of %d\nCurrent weapon: %s\n\nLeader (%s) level: %d of %d (%s)' %(gungamePlayer.get('level'), getTotalLevels(), gungamePlayer.get('weapon'), es.getplayername(list_leadersUserid[0]), leaderLevel, getTotalLevels(), getLevelWeapon(leaderLevel))
                        
                gamethread.delayed(0.5, usermsg.hudhint, (userid, HudHintText))
                
            if int(getGunGameVar('gg_map_obj')) > 1:
                # Check to see if this player is a CT
                if int(event_var['es_userteam']) == 3:
                    # Check to see if the map is a "de_*" map
                    if getGunGameVar('gungame_currentmap_prefix') == 'de':
                        # See if the admin wants us to give them a defuser
                        if int(getGunGameVar('gg_player_defuser')) > 0:
                            playerlibPlayer = playerlib.getPlayer(userid)
                            
                            # Make sure the player doesn't already have a defuser
                            if not playerlibPlayer.get('defuser'):
                                es.server.cmd('es_xgive %d item_defuser' %userid)
    StopProfiling(g_Prof)
    #es.msg("Event player_spawn benchmark: %f seconds" % GetProfilerTime(g_Prof))

def player_jump(event_var):
    global dict_afk
    userid = int(event_var['userid'])
    
    # Is player human?
    if not es.isbot(userid):
        # Here, we will make sure that the player isn't counted as AFK
        dict_afk[userid].int_afk_math_total = 1

def player_death(event_var):
    global countBombDeathAsSuicide
    
    # Set vars
    userid = int(event_var['userid'])
    gungameVictim = gungame.getPlayer(userid)
    attacker = int(event_var['attacker'])
    
    # If the attacker is not "world"
    if attacker != 0:
        gungameAttacker = gungame.getPlayer(attacker)
        # If the attacker is not on the same team
        if int(event_var['es_userteam']) != int(event_var['es_attackerteam']):
            # If the weapon is the correct weapon
            if event_var['weapon'] == gungameAttacker.get('weapon'):
                # If the victim was not AFK
                if not gungameVictim.get('isplayerafk'):
                    # Make sure that PreventLevel is not set to "1"
                    if int(gungameAttacker.get('preventlevel')) == 0:
                        # If multikill is active we need to set up for it
                        if int(getGunGameVar('gg_multikill')) > 1:
                            if int(getGunGameVar('gg_multikill')) < 2:
                                setGunGameVar('gg_multikill', 0)
                                levelUpOldLevel = gungameAttacker.get('level')
                                levelUpNewLevel = attackerOldLevel + 1
                                gungameAttacker.set('level', levelUpNewLevel)
                                # triggerLevelUpEvent(levelUpUserid, levelUpSteamid, levelUpName, levelUpTeam, levelUpOldLevel, levelUpNewLevel, victimUserid, victimName)
                                triggerLevelUpEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelUpOldLevel, levelUpNewLevel, userid, event_var['es_username'])
                            else:
                                attackerMultiKillCount = gungameAttacker.get('multikill') + 1
                                if attackerMultiKillCount == int(getGunGameVar('gg_multikill')):
                                    levelUpOldLevel = gungameAttacker.get('level')
                                    levelUpNewLevel = levelUpOldLevel + 1
                                    # triggerLevelUpEvent(levelUpUserid, levelUpSteamid, levelUpName, levelUpTeam, levelUpOldLevel, levelUpNewLevel, victimUserid, victimName)
                                    triggerLevelUpEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelUpOldLevel, levelUpNewLevel, userid, event_var['es_username'])
                                else:
                                    usermsg.hudhint(userid, 'Kills this level: %d of %d' %(attackerMultiKillCount, int(getGunGameVar('gg_multikill'))))
                                    gungameAttacker.set('multikill', attackerMultiKillCount)
                        # Multikill was not active
                        else:
                            levelUpOldLevel = gungameAttacker.get('level')
                            levelUpNewLevel = levelUpOldLevel + 1
                            # triggerLevelUpEvent(levelUpUserid, levelUpSteamid, levelUpName, levelUpTeam, levelUpOldLevel, levelUpNewLevel, victimUserid, victimName)
                            triggerLevelUpEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelUpOldLevel, levelUpNewLevel, userid, event_var['es_username'])
                # The victim was AFK
                else:
                    usermsg.hudhint(attacker, '%s was AFK\nYour kill did not count!!!' %event_var['es_username'])
                    
                    # Check to see if AFK punishment is active
                    if int(getGunGameVar('gg_afk_rounds')) > 0:
                        # BOTs are never AFK
                        if not es.isbot(userid):
                            # Run the AFK punishment code
                            afkPunishCheck(userid)            
        # Must be a team kill or a suicide...let's see, shall we?
        else:
            # Check to see if the player was suicidal
            if userid == attacker:
                # Yep! They killed themselves. Now let's see if we are going to punish the dead...
                if int(getGunGameVar('gg_suicide_punish')) > 0:
                    # Set vars
                    levelDownOldLevel = int(gungameAttacker.get('level'))
                    levelDownNewLevel = levelDownOldLevel - int(getGunGameVar('gg_suicide_punish'))
                    
                    # Let's not put them on a non-existant level 0...
                    if levelDownNewLevel > 0:
                        # LEVEL DOWN CODE
                        triggerLevelDownEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelDownOldLevel, levelDownNewLevel, userid, event_var['es_username'])
                    else:
                        triggerLevelDownEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelDownOldLevel, 1, userid, event_var['es_username'])
            # Team Killer!!!
            else:
                # Let's see if we get to punish the vile TK'er...
                if int(getGunGameVar('gg_tk_punish')) > 0:
                    # Set vars
                    levelDownOldLevel = gungameAttacker.get('level')
                    levelDownNewLevel = levelDownOldLevel - int(getGunGameVar('gg_tk_punish'))
                    
                    # Let's not put them on a non-existant level 0...
                    if levelDownNewLevel > 0:
                        triggerLevelDownEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelDownOldLevel, levelDownNewLevel, userid, event_var['es_username'])
                    else:
                        triggerLevelDownEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], levelDownOldLevel, 1, userid, event_var['es_username'])
    else:
        # Killed by "world"
        gungameAttacker = gungame.getPlayer(userid)
        
        if int(getGunGameVar('gg_suicide_punish')) > 0:
            # Make sure that the explosion of the bomb doesn't count as a suicide to punish
            if countBombDeathAsSuicide:
                # Set vars
                levelDownOldLevel = gungameAttacker.get('level')
                levelDownNewLevel = levelDownOldLevel - int(getGunGameVar('gg_suicide_punish'))
                
                # Let's not put them on a non-existant level 0...
                if levelDownNewLevel > 0:
                    # LEVEL DOWN CODE
                    triggerLevelDownEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_attackername'], event_var['es_userteam'], levelDownOldLevel, levelDownNewLevel, userid, event_var['es_username'])

def bomb_defused(event_var):
    ## TODO: Should we put in an option to allow them to skip these levels by defusing?
    
    # Set vars
    userid = int(event_var['userid'])
    gungamePlayer = gungame.getPlayer(userid)
    playerWeapon = gungamePlayer.get('weapon')
    
    # Cant skip the last level
    if int(gungamePlayer.get('level')) == int(getTotalLevels()) or playerWeapon == 'knife' or playerWeapon == 'hegrenade':
        es.tell(userid, '#multi', 'You can not skip the \4%s\1 level by defusing the bomb!' % playerWeapon)
    
    # Level them up
    levelUpOldLevel = gungamePlayer.get('level')
    levelUpNewLevel = levelUpOldLevel + 1
    triggerLevelUpEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_username'], event_var['es_userteam'], levelUpOldLevel, levelUpNewLevel, '0', '0')

def bomb_exploded(event_var):
    # Set vars
    userid = int(event_var['userid'])
    gungamePlayer = gungame.getPlayer(userid)
    playerWeapon = gungamePlayer.get('weapon')
    
    # Cant skip the last level
    if int(gungamePlayer.get('level')) == int(getTotalLevels()) or playerWeapon == 'knife' or playerWeapon == 'hegrenade':
        es.tell(userid, '#multi', 'You can not skip the \4%s\1 level by planting the bomb!' % playerWeapon)
    
    # Level them up
    levelUpOldLevel = gungamePlayer.get('level')
    levelUpNewLevel = levelUpOldLevel + 1
    triggerLevelUpEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_username'], event_var['es_userteam'], levelUpOldLevel, levelUpNewLevel, '0', '0')

def gg_levelup(event_var):
    global list_leaderNames
    
    # Check for a winner first
    if int(event_var['old_level']) == getTotalLevels():
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
        gungamePlayer = gungame.getPlayer(userid)
        # Set the player's level in the GunGame Core Dictionary
        gungamePlayer.set('level', int(event_var['new_level']))
        # Reset the player's multikill in the GunGame Core Dictionary
        gungamePlayer.set('multikill', 0)
        # -----------------------------------------
        # END REGULAR LEVELUP CODE
        
        # BEGIN LEADER LEVEL COMPARISONS & MESSAGING
        # -------------------------------------------------------------------------
        
        # Let's see if this player is the new leader
        newLeaderLevel = int(getLeaderLevel())
        oldLeaderLevel = int(getGunGameVar('oldleaderlevel'))
        if newLeaderLevel == int(event_var['new_level']):
            if len(getLevelUseridList(newLeaderLevel)) == 1:
                # Congratulations, player! You have become the new leader.
                # Now, let's add the new leader's name to the list "list_leaderNames"
                list_leaderNames = []
                list_leaderNames.append(removeReturnChars(event_var['name']))
                # Rebuild the leaders menu
                rebuildLeaderMenu()
                # Set this new level to be the new oldLeaderLevel
                setGunGameVar('oldleaderlevel', int(event_var['old_level']))
                # Loop through the players and send a saytext2 message
                for userid in es.getUseridList():
                    usermsg.saytext2(userid, gungamePlayer.attributes['index'], '\3%s\1 is now leading on level \4%d' % (event_var['name'], int(event_var['new_level'])))
            # Let's see if the player has tied the other leaders
            else:
                # OK. They have tied someone else.
                # Now we add their name to the leader list ("list_leaderNames")
                list_leaderNames.append(removeReturnChars(event_var['name']))
                # Let's find out how many people are on the leader level
                leaderCount = int(len(list_leaderNames))
                # There are 2 leaders
                if leaderCount == 2:
                    # Loop through the players and send a saytext2 message
                    for userid in es.getUseridList():
                        usermsg.saytext2(userid, gungamePlayer.attributes['index'], '\4[2-way tie]\3 %s\1 has tied the other leader on level \4%d' % (event_var['name'], int(event_var['new_level'])))
                # There are more than 2 leaders
                elif leaderCount > 2:
                    # Loop through the players and send a saytext2 message
                    for userid in es.getUseridList():
                        usermsg.saytext2(userid, gungamePlayer.attributes['index'], '\4[%d-way tie]\3 %s\1 has tied the other leaders on level \4%d' % (leaderCount, event_var['name'], int(event_var['new_level'])))
                # Rebuild the leaders menu
                rebuildLeaderMenu()
        # ----------------------------------------------------------------------
        # END LEADER LEVEL COMPARISONS & MESSAGING
        
        if not dict_gungameRegisteredAddons.has_key('gungame\\included_addons\\gg_warmup_round'):
            # Get levels behind leader
            levelsBehindLeader = newLeaderLevel - gungamePlayer.get('level')
            
            # Get list of leaders userids
            list_leadersUserid = getLevelUseridList(newLeaderLevel)
                
            # How many levels behind the leader?
            if levelsBehindLeader == 0:
                # Is there more than 1 leader?
                if len(list_leadersUserid) == 1:    
                    HudHintText = 'Current level: %d of %d\nCurrent weapon: %s\n\nYou are the leader.' % (gungamePlayer.get('level'), getTotalLevels(), gungamePlayer.get('weapon'))
                else:
                    HudHintText = 'Current level: %d of %d\nCurrent weapon: %s\n\nYou are amongst the leaders (' % (gungamePlayer.get('level'), getTotalLevels(), gungamePlayer.get('weapon'))
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
                HudHintText = 'Current level: %d of %d\nCurrent weapon: %s\n\nLeader (%s) level: %d of %d (%s)' %(gungamePlayer.get('level'), getTotalLevels(), gungamePlayer.get('weapon'), es.getplayername(list_leadersUserid[0]), newLeaderLevel, getTotalLevels(), getLevelWeapon(newLeaderLevel))
                
            gamethread.delayed(0.5, usermsg.hudhint, (event_var['userid'], HudHintText))
        
        # BEGIN CODE FOR TRIGGERING CUSTOM EVENT "GG_VOTE"
        # ----------------------------------------------------------------------------------
        if newLeaderLevel == getTotalLevels() - int(getGunGameVar('gg_vote_trigger')):
            # Only continue if no other script has set the next map
            if es.ServerVar('eventscripts_nextmapoverride') == '':
                if not getGunGameVar('gungame_voting_started'):
                    es.event('initialize', 'gg_vote')
                    es.event('fire', 'gg_vote')
            else:
                es.dbgmsg(0, '[GunGame] - Map vote failed because eventscripts_nextmapoverride was previously set by another script.')
        # ----------------------------------------------------------------------------------
        # END CODE FOR TRIGGERING CUSTOM EVENT "GG_VOTE"

def gg_leveldown(event_var):
    global list_leaderNames
    
    userid = int(event_var['userid'])
    gungamePlayer = gungame.getPlayer(userid)
    
    # Set the player's level in the GunGame Core Dictionary
    gungamePlayer.set('level', int(event_var['new_level']))
    
    # Remove the player's name from the leaderlist, since they are no longer a leader
    name = removeReturnChars(event_var['name'])
    if name in list_leaderNames:
        list_leaderNames.remove(name)
        rebuildLeaderNameList()
        rebuildLeaderMenu()
        if int(event_var['new_level']) == int(getLeaderLevel()):
            setGunGameVar('oldleaderlevel', int(getGunGameVar('oldleaderlevel')) - 1)

def unload():
    global gungameWeaponOrderMenu
    #popuplib.delete('gungameWeaponOrderMenu.delete()
    global dict_gungameRegisteredAddons
    for addonName in dict_gungameRegisteredAddons:
        es.unload(addonName.replace('\\', '/'))
        
    # Enable Buyzones
    userid = es.getuserid()
    es.server.cmd('es_xfire %d func_buyzone Enable' %userid)
    
    # Check to see if objectives need to be enabled/disabled
    mapObjectives = int(getGunGameVar('gg_map_obj'))
    
    # Get the map prefix for the following checks
    mapPrefix = getGunGameVar('gungame_currentmap_prefix')
    
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
    es.unload('gungame/included_addons/gg_sounds')
    
    # Fire gg_unload event
    es.event('initialize','gg_unload')
    es.event('fire','gg_unload')

def gg_vote(event_var):
    setGunGameVar('gungame_voting_started', True)
    if getGunGameVar('gg_map_vote') == '2':
        es.server.cmd('ma_voterandom end %s' %getGunGameVar('gg_map_vote_size'))

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
    
    # Reset Players in the GunGame Core Database
    registerPlayers()
    
    # SayText2 the message to the world
    for pUserid in playerlib.getUseridList('#all'):
        usermsg.saytext2(pUserid, event_var['es_userindex'], '\3%s\1 won the game!' % playerName)
    
    # Now centermessage it
    es.centermsg('%s won!' %playerName)
    gamethread.delayed(2, es.centermsg, ('%s won!' %playerName))
    gamethread.delayed(4, es.centermsg, ('%s won!' %playerName))
    
    if int(getGunGameVar('gg_save_winners')) > 0:
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

def gg_variable_changed(event_var):
    global list_includedAddonsDir
    global dict_gungameRegisteredAddons
    global dict_gungameRegisteredDependencies
    global list_allWeapons
    cvarName = event_var['cvarname']
    newValue = event_var['newvalue']
    oldValue = event_var['oldvalue']
    
    # GG_MAPVOTE
    if cvarName == 'gg_map_vote':
        if newValue == '1' and  not dict_gungameRegisteredAddons.has_key('gungame\\included_addons\\gg_map_vote'):
            es.server.queuecmd('es_load gungame/included_addons/gg_map_vote')
        elif newValue != '1' and dict_gungameRegisteredAddons.has_key('gungame\\included_addons\\gg_map_vote'):
            es.unload('gungame/included_addons/gg_map_vote')
    # GG_NADE_BONUS
    elif cvarName == 'gg_nade_bonus':
        if newValue != '0' and newValue != 'knife' and newValue in list_allWeapons:
            es.server.queuecmd('es_load gungame/included_addons/gg_nade_bonus')
        elif newValue == '0' and dict_gungameRegisteredAddons.has_key('gungame\\included_addons\\gg_nade_bonus'):
            es.unload('gungame/included_addons/gg_nade_bonus')
    # GG_SPAWN_PROTECTION
    elif cvarName == 'gg_spawn_protect':
        if int(newValue) > 0 and  not dict_gungameRegisteredAddons.has_key('gungame\\included_addons\\gg_spawn_protect'):
            es.server.queuecmd('es_load gungame/included_addons/gg_spawn_protect')
        elif newValue == '0' and dict_gungameRegisteredAddons.has_key('gungame\\included_addons\\gg_spawn_protect'):
            es.unload('gungame/included_addons/gg_spawn_protect')
    # GG_FRIENDLYFIRE
    elif cvarName == 'gg_friendlyfire':
        if int(newValue) > 0 and  not dict_gungameRegisteredAddons.has_key('gungame\\included_addons\\gg_friendlyfire'):
            es.server.queuecmd('es_load gungame/included_addons/gg_friendlyfire')
        elif newValue == '0' and dict_gungameRegisteredAddons.has_key('gungame\\included_addons\\gg_friendlyfire'):
            es.unload('gungame/included_addons/gg_friendlyfire')
    # All other included addons
    elif cvarName in list_includedAddonsDir:
        if newValue == '1':
            es.server.queuecmd('es_load gungame/included_addons/%s' %cvarName)
        elif newValue == '0' and dict_gungameRegisteredAddons.has_key('gungame\\included_addons\\%s' %cvarName):
            es.unload('gungame/included_addons/%s' %cvarName)
            

# ===================================================================================================
# ===================================================================================================
#                !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! END GAME EVENTS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
# ===================================================================================================
# ===================================================================================================


# ===================================================================================================
#   HELPER FUNCTIONS
# ===================================================================================================
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

def update_afk_dict(userid):
    global dict_afk
    # check if player is a bot
    if not es.isbot(userid):
        list_playerlocation = es.getplayerlocation(userid)
        afk_math_total = int(sum(list_playerlocation)) - list_playerlocation[2] + int(es.getplayerprop(userid,'CCSPlayer.m_angEyeAngles[0]')) + int(es.getplayerprop(userid,'CCSPlayer.m_angEyeAngles[1]'))
        dict_afk[userid].int_afk_math_total = int(afk_math_total)


# ===================================================================================================
#   MESSAGE CLASS
# ===================================================================================================
class Message:
    def __init__(self, userid = None):
        # Is userid console?
        if userid == 0:
            # Set userid and object
            self.userid = 0
            self.object = None
            
            # Ignore the rest of init
            return
        
        # Set userid
        self.userid = userid
        
        # Set the player object
        if userid:
            self.object = playerlib.getPlayer(userid)
    
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
        
        # Return
        return string
    
    def getString(self, message, tokens = None, object = None):
        # If no object set, use the class default
        if not object and self.userid != 0:
            object = self.object
        
        # Return the string
        try:
            return self.langStrings(message, tokens, object.get('lang'))
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
            es.tell(self.userid, '%s%s' % (prefix, self.getString(string, tokens)))
        else:
            # Loop through the players
            for userid in es.getUseridList():
                # Get some vars
                userid = int(userid)
                object = playerlib.getPlayer(userid)
                
                # Send it
                es.tell(userid, '%s%s' % (prefix, self.getString(string, tokens)))
                
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
            usermsg.saytext2(self.userid, index, self.getString(string, tokens))
        else:
            # Loop through the players
            for userid in es.getUseridList():
                # Get some vars
                userid = int(userid)
                object = playerlib.getPlayer(userid)
                
                # Send it
                usermsg.saytext2(userid, index, self.getString(string, tokens, object))
                
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