''' (c) 2008 by the GunGame Coding Team

    Title: gungame
    Version: 1.0.360
    Description: The main addon, handles leaders and events.
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python Imports
import os

# EventScripts Imports
import es
import gamethread
import playerlib
import usermsg
import popuplib
import keyvalues
import services
from configobj import ConfigObj

# ==============================================================================
#   ADDON REGISTRATION
# ==============================================================================
# Version info
__version__ = '1.0.365'
es.ServerVar('eventscripts_ggp', __version__).makepublic()

# Register with EventScripts
info = es.AddonInfo()
info.name     = 'GunGame: Python'
info.version  = __version__
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame'
info.author   = 'Michael Barr (XE_ManUp), Paul (RideGuy), Saul Rennison (Cheezus)'

# ==============================================================================
#   LOAD GUNGAMELIB
# ==============================================================================
import gungamelib
reload(gungamelib)

# ==============================================================================
#   GLOBALS
# ==============================================================================
dict_variables = {}
list_primaryWeapons = ['awp', 'scout', 'aug', 'mac10', 'tmp', 'mp5navy',
                       'ump45', 'p90', 'galil', 'famas', 'ak47', 'sg552',
                       'sg550', 'g3sg1', 'm249', 'm3', 'xm1014', 'm4a1']
list_secondaryWeapons = ['glock', 'usp', 'p228', 'deagle', 'elite', 'fiveseven']
list_allWeapons = ['glock', 'usp', 'p228', 'deagle', 'elite', 'fiveseven',
                   'awp', 'scout', 'aug', 'mac10', 'tmp', 'mp5navy', 'ump45',
                   'p90', 'galil', 'famas', 'ak47', 'sg552', 'sg550', 'g3sg1',
                   'm249', 'm3', 'xm1014', 'm4a1', 'hegrenade', 'flashbang',
                   'smokegrenade']
list_includedAddonsDir = []
list_customAddonsDir = []
list_stripExceptions = []

# ==============================================================================
#   ERROR CLASSES
# ==============================================================================
class UseridError(Exception):
    pass

class PlayerError(Exception):
    pass

class ArgumentError(Exception):
    pass
    
class LevelValueError(Exception):
    pass

class MultiKillValueError(Exception):
    pass
    
class AFKValueError(Exception):
    pass

class TripleValueError(Exception):
    pass

class VariableError(Exception):
    pass

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    global countBombDeathAsSuicide
    global list_stripExceptions
    
    # Register addon
    gungame = gungamelib.registerAddon('gungame')
    gungame.setDisplayName('GunGame')
    
    # Print load started
    es.dbgmsg(0, '[GunGame] %s' % ('=' * 50))
    gungamelib.echo('gungame', 0, 0, 'LoadStarted')
    es.dbgmsg(0, '[GunGame] %s' % ('=' * 50))
    
    try:
        # Load custom events
        es.loadevents('declare', 'addons/eventscripts/gungame/events/es_gungame_events.res')
        
        # Loop through included addons
        for includedAddon in os.listdir(gungamelib.getGameDir('/addons/eventscripts/gungame/included_addons/')):
            if includedAddon[0:3] == 'gg_':
                list_includedAddonsDir.append(includedAddon)
        
        # Loop through custom addons
        for customAddon in os.listdir(gungamelib.getGameDir('/addons/eventscripts/gungame/custom_addons/')):
            if customAddon[0:3] == 'gg_':
                list_customAddonsDir.append(customAddon)
        
        # Load configs
        gungamelib.getConfig('gg_en_config.cfg')
        gungamelib.getConfig('gg_default_addons.cfg')
        gungamelib.getConfig('gg_map_vote.cfg')
        es.dbgmsg(0, '[GunGame] %s' % ('=' * 50))
        
        # Fire the gg_server.cfg
        es.server.cmd('exec gungame/gg_server.cfg')
        
        '''Possibly upcoming integrity checker code when we go gold... D:
        
        # Generate hashes
        # DEVS: Comment this when commiting the code to SVN
        gungamelib.generateHashes()
        
        # Integrity check
        check = gungamelib.fileHashCheck()
        if not check[0]:
            # Announce that the check failed
            es.dbgmsg(0, '[GunGame] Unable to load GunGame: integrity check failed:')
            es.dbgmsg(0, '[GunGame]  File: %s' % check[1])
            es.dbgmsg(0, '[GunGame]  Reason: %s' % check[2])
            es.dbgmsg(0, '[GunGame] Please try the following solutions:')
            es.dbgmsg(0, '[GunGame]  1. Re-upload GunGame to your server.')
            es.dbgmsg(0, '[GunGame]  2. Re-download GunGame, then upload again.')
            es.dbgmsg(0, '[GunGame]  3. If none of the above fix the issue then file a bug report.')
            es.dbgmsg(0, '[GunGame] %s' % ('=' * 50))
            
            # Unload gungame
            es.unload('gungame')
            return
        '''
        
        # Update
        es.dbgmsg(0, '[GunGame]     * Update check')
        es.dbgmsg(0, '[GunGame] %s' % ('=' * 50))
        gungamelib.update()
        
        # Get strip exceptions
        if gungamelib.getVariableValue('gg_map_strip_exceptions') != 0:
            list_stripExceptions = gungamelib.getVariableValue('gg_map_strip_exceptions').split(',')
        
        # Get weapon order file
        baseDir = gungamelib.getGameDir('cfg/gungame/weapon_orders/')
        files = os.listdir(baseDir)
        
        for x in files:
            file, ext = os.path.splitext(x)
            ext = ext[1:]
            
            if ext != 'txt':
                continue
            
            # Parse the file
            weaponOrder = gungamelib.getWeaponOrder(file)
            
            # Is not the one we want?
            if file != gungamelib.getVariableValue('gg_weapon_order_file'):
                continue
            
            # Set this as the weapon order
            weaponOrder.setWeaponOrderFile()
            
            # Set order type
            if gungamelib.getVariableValue('gg_weapon_order') != '#default':
                weaponOrder.changeWeaponOrderType(gungamelib.getVariableValue('gg_weapon_order'))
            
            # Set multikill override
            if gungamelib.getVariableValue('gg_multikill_override') > 1:
                weaponOrder.setMultiKillOverride(gungamelib.getVariableValue('gg_multikill_override'))
            
            # Echo to console
            es.dbgmsg(0, '[GunGame] %s' % ('=' * 50))
            gungamelib.echo('gungame', 0, 0, 'WeaponOrder:Echo:Info')
            es.dbgmsg(0, '[GunGame] %s' % ('=' * 50))
            weaponOrder.echo()
            es.dbgmsg(0, '[GunGame] %s' % ('=' * 50))
        
        # Build menus
        buildLevelMenu()
        buildLeaderMenu()
        
        # Register commands
        gungame.registerPublicCommand('weapons', displayWeaponOrderMenu)
        gungame.registerPublicCommand('level', displayLevelMenu)
        gungame.registerPublicCommand('leader', displayLeadersMenu)
        gungame.registerPublicCommand('leaders', displayLeadersMenu)
        
        # Clear out the GunGame system
        gungamelib.resetGunGame()
        
        # Set Up a custom variable for voting in dict_variables
        dict_variables['gungame_voting_started'] = False
        
        # Set up a custom variable for tracking multi-rounds
        dict_variables['roundsRemaining'] = gungamelib.getVariableValue('gg_multi_round')
        
        # Start warmup timer
        if gungamelib.inMap():
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
        
        # Set map prefix global
        list_mapPrefix = str(es.ServerVar('eventscripts_currentmap')).split('_')
        gungamelib.setGlobal('gungame_currentmap_prefix', list_mapPrefix[0])
        
        # Create a variable to prevent bomb explosion deaths from counting a suicides
        countBombDeathAsSuicide = False
        
        # Load sound pack
        gungamelib.getSoundPack(gungamelib.getVariableValue('gg_soundpack'))
        
        # Load gg_console -- the console interface
        es.load('gungame/included_addons/gg_console')
        
        # Fire gg_load event
        es.event('initialize', 'gg_load')
        es.event('fire', 'gg_load')
        
        # Print load completed
        es.dbgmsg(0, '[GunGame] %s' % ('=' * 50))
        gungamelib.echo('gungame', 0, 0, 'LoadCompleted')
        es.dbgmsg(0, '[GunGame] %s' % ('=' * 50))
    except Exception, e:
        es.dbgmsg(0, '[GunGame] %s' % ('=' * 50))
        es.dbgmsg(0, '[GunGame] Unable to load GunGame: exception raised during load:')
        es.dbgmsg(0, '[GunGame] %s: %s' % (e.__class__.__name__, e))
        es.dbgmsg(0, '[GunGame] %s' % ('=' * 50))
        es.unload('gungame')

def unload():
    global gungameWeaponOrderMenu
    
    # Unload all enabled addons
    for addonName in gungamelib.getRegisteredAddonlist():
        if addonName in list_includedAddonsDir:
            es.unload('gungame/included_addons/%s' % addonName)
        elif addonName in list_customAddonsDir:
            es.unload('gungame/custom_addons/%s' % addonName)
        
    # Enable Buyzones
    userid = es.getuserid()
    es.server.cmd('es_xfire %d func_buyzone Enable' % userid)
    
    # Get map if
    mapObjectives = gungamelib.getVariableValue('gg_map_obj')
    mapPrefix = gungamelib.getGlobal('gungame_currentmap_prefix')
    
    # Re-enable objectives
    if mapObjectives < 3:
        # Re-enable all objectives
        if mapObjectives == 0:
            if mapPrefix == 'de':
                es.server.cmd('es_xfire %d func_bomb_target Enable' %userid)
            elif mapPrefix == 'cs':
                es.server.cmd('es_xfire %d func_hostage_rescue Enable' %userid)
        
        # Enable bomb zone
        elif mapObjectives == 1:
            if mapPrefix == 'de':
                es.server.cmd('es_xfire %d func_bomb_target Enable' %userid)
        
        # Enable hostage objectives
        elif mapObjectives == 2:
            if mapPrefix == 'cs':
                es.server.cmd('es_xfire %d func_hostage_rescue Enable' %userid)
    
    # Unregister commands
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


def es_map_start(event_var):
    # Load custom GunGame events
    es.loadevents('declare', 'addons/eventscripts/gungame/events/es_gungame_events.res')
    
    # Execute GunGame's autoexec.cfg
    es.delayed('1', 'exec gungame/gg_server.cfg')
    
    # Split the map name into a list separated by "_"
    list_mapPrefix = event_var['mapname'].split('_')
    
    # Insert the new map prefix into the GunGame Variables
    gungamelib.setGlobal('gungame_currentmap_prefix', list_mapPrefix[0])
    
    # Reset the "gungame_voting_started" variable
    dict_variables['gungame_voting_started'] = False
    
    # Reset the "rounds remaining" variable for multi-rounds
    dict_variables['roundsRemaining'] = gungamelib.getVariableValue('gg_multi_round')
    
    if gungamelib.getVariableValue('gg_weapon_order') == '#random':
        # Re-randomize the weapon order
        myWeaponOrder = gungamelib.getWeaponOrder(gungamelib.getCurrentWeaponOrderFile())
        myWeaponOrder.changeWeaponOrderType('#random')
    
    # Update
    es.dbgmsg(0, '[GunGame]     * Update check')
    es.dbgmsg(0, '[GunGame] %s' % ('=' * 50))
    gungamelib.update()
    
    # Check to see if the warmup round needs to be activated
    if gungamelib.getVariableValue('gg_warmup_timer') > 0:
        es.load('gungame/included_addons/gg_warmup_round')
    else:
        # Fire gg_start event
        es.event('initialize','gg_start')
        es.event('fire','gg_start')
    
    # Reset the GunGame Round
    gungamelib.resetGunGame()
    
    # Make sounds downloadbale
    gungamelib.addDownloadableSounds()

def round_start(event_var):
    global list_stripExceptions
    global list_allWeapons
    global countBombDeathAsSuicide
    
    # Set a global for round_active
    gungamelib.setGlobal('round_active', 1)
    
    # Create a variable to prevent bomb explosion deaths from counting a suicides
    countBombDeathAsSuicide = False
    
    # Disable Buyzones
    userid = es.getuserid()
    es.server.cmd('es_xfire %d func_buyzone Disable' % userid)
    
    # Remove weapons
    for weapon in list_allWeapons:
        # Make sure that the admin doesn't want the weapon left on the map
        if weapon not in list_stripExceptions:
            # Remove the weapon from the map
            es.server.cmd('es_xfire %d weapon_%s kill' % (userid, weapon))
    
    # Equip players
    equipPlayer()

    # Get map info
    mapObjectives = gungamelib.getVariableValue('gg_map_obj')
    mapPrefix = gungamelib.getGlobal('gungame_currentmap_prefix')
    
    # If both the BOMB and HOSTAGE objectives are enabled, we don't do anything else
    if mapObjectives < 3:
        # Remove all objectives
        if mapObjectives == 0:
            if mapPrefix == 'de':
                es.server.cmd('es_xfire %d func_bomb_target Disable' %userid)
                es.server.cmd('es_xfire %d weapon_c4 Kill' %userid)
            
            elif mapPrefix == 'cs':
                es.server.cmd('es_xfire %d func_hostage_rescue Disable' %userid)
                es.server.cmd('es_xfire %d hostage_entity Kill' %userid)
        
        # Remove bomb objectives
        elif mapObjectives == 1:
            if mapPrefix == 'de':
                es.server.cmd('es_xfire %d func_bomb_target Disable' %userid)
                es.server.cmd('es_xfire %d weapon_c4 Kill' % userid)
        
        # Remove hostage objectives
        elif mapObjectives == 2:
            if mapPrefix == 'cs':
                es.server.cmd('es_xfire %d func_hostage_rescue Disable' %userid)
                es.server.cmd('es_xfire %d hostage_entity Kill' % userid)
    
    if gungamelib.getVariableValue('gg_leaderweapon_warning'):
        leaderWeapon = gungamelib.getLevelWeapon(gungamelib.leaders.getLeaderLevel())
        
        # Play knife sound
        if leaderWeapon == 'knife':
            gungamelib.playSound('#all', 'knifelevel')
        
        # Play nade sound
        if leaderWeapon == 'hegrenade':
            gungamelib.playSound('#all', 'nadelevel')

def round_freeze_end(event_var):
    global countBombDeathAsSuicide
    
    # Create a variable to prevent bomb explosion deaths from counting a suicides
    countBombDeathAsSuicide = True

def round_end(event_var):
    global countBombDeathAsSuicide
    
    # Set a global for round_active
    gungamelib.setGlobal('round_active', 0)
    
    # Create a variable to prevent bomb explosion deaths from counting a suicides
    countBombDeathAsSuicide = False
    
    # Equip player
    equipPlayer()
    
    # Was a ROUND_DRAW or GAME_COMMENCING?
    if int(event_var['reason']) == 10 or int(event_var['reason']) == 16:
        return
    
    # Do we punish AFKers?
    if gungamelib.getVariableValue('gg_afk_rounds') == 0:
        return
    
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
    # Setup the player
    gungamelib.getPlayer(event_var['userid'])
    
def player_disconnect(event_var):
    userid = int(event_var['userid'])
    
    # Game over?
    if gungamelib.getGlobal('gameOver') == 1:
        return
    
    # Player doesn't exist?
    if not gungamelib.playerExists(userid):
        return
    
    # Is leader?
    if gungamelib.leaders.isLeader(userid):
        gungamelib.leaders.removeLeader(userid)

def player_spawn(event_var):
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    
    if gungamelib.isSpectator(userid):
        return
    
    if gungamelib.isDead(userid):
        return
    
    # Reset AFK status
    if not es.isbot(userid):
        gamethread.delayed(0.6, gungamePlayer.resetPlayerLocation, ())

    # Check to see if the WarmUp Round is Active
    if not gungamelib.getGlobal('isWarmup'):
        # Since the WarmUp Round is not Active, give the player the weapon relevant to their level
        gungamePlayer.giveWeapon()
        
        levelInfoHint(userid)
    
    if gungamelib.getVariableValue('gg_map_obj') > 1:
        # Check to see if this player is a CT
        if int(event_var['es_userteam']) == 3:
            
            # Are we in a de_ map and want to give defuser?
            if gungamelib.getGlobal('gungame_currentmap_prefix') == 'de' and gungamelib.getVariableValue('gg_player_defuser') > 0:
                # Get player object
                playerlibPlayer = playerlib.getPlayer(userid)
                
                # Make sure the player doesn't already have a defuser
                if not playerlibPlayer.get('defuser'):
                    es.server.cmd('es_xgive %d item_defuser' % userid)

def player_jump(event_var):
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Set to not be AFK
    if not es.isbot(userid):
        gungamePlayer.playerNotAFK()

def player_death(event_var):
    global countBombDeathAsSuicide
    
    # Is warmup round?
    if gungamelib.getGlobal('isWarmup'):
        return
    
    # Get player stuff
    userid = int(event_var['userid'])
    attacker = int(event_var['attacker'])
    
    # Is the attacker on the server?
    if not gungamelib.clientInServer(attacker):
        return
    
    # Get victim object
    gungameVictim = gungamelib.getPlayer(userid)
    
    # =============
    # SUICIDE CHECK
    # =============
    if (attacker == 0 or attacker == userid) and countBombDeathAsSuicide:
        if gungamelib.getVariableValue('gg_suicide_punish') == 0:
            return
        
        # Set vars
        oldLevel = gungameVictim['level']
        newLevel = gungamelib.clamp(oldLevel - gungamelib.getVariableValue('gg_suicide_punish'), 1)
        
        # Trigger level down
        gungamelib.triggerLevelDownEvent(userid, oldLevel, newLevel, userid, 'suicide')
        
        gungamelib.msg('gungame', attacker, 'Suicide_LevelDown', {'newlevel': newLevel})
        
        # Play the leveldown sound
        gungamelib.playSound(userid, 'leveldown')
        
        return
    
    # Get attacker object
    gungameAttacker = gungamelib.getPlayer(attacker)
    
    # ===============
    # TEAM-KILL CHECK
    # ===============
    if (event_var['es_userteam'] == event_var['es_attackerteam']):
        if gungamelib.getVariableValue('gg_tk_punish') == 0:
            return
        
        # Set vars
        oldLevel = gungameAttacker['level']
        newLevel = gungamelib.clamp(oldLevel - gungamelib.getVariableValue('gg_tk_punish'), 1)
        
        # Trigger level down
        gungamelib.triggerLevelDownEvent(attacker, oldLevel, newLevel, userid, 'tk')
        
        gungamelib.msg('gungame', attacker, 'TeamKill_LevelDown', {'newlevel': newLevel})
        
        # Play the leveldown sound
        gungamelib.playSound(attacker, 'leveldown')
        
        return
    
    # ===========
    # NORMAL KILL
    # ===========
    # Get weapon name
    weapon = event_var['weapon']
    
    # Check the weapon was correct
    if weapon != gungameAttacker.getWeapon():
        return
    
    # Don't continue if the victim is AFK
    if gungameVictim.isPlayerAFK():
        # Tell the attacker they were AFK
        gungamelib.hudhint('gungame', attacker, 'PlayerAFK', {'player': event_var['es_username']})
        
        # Check AFK punishment
        if not es.isbot(userid) and gungamelib.getVariableValue('gg_afk_rounds') > 0:
            afkPunishCheck(userid)
        
        return
    
    # Can't level up if the attacker can't
    if int(gungameAttacker['preventlevel']) == 1:
        return
    
    # No multikill? Just level up...
    multiKill = gungamelib.getLevelMultiKill(gungameAttacker['level'])
    if multiKill == 1:
        # Set level variables
        oldLevel = gungameAttacker['level']
        newLevel = oldLevel + 1
        
        # Level them up
        gungamelib.triggerLevelUpEvent(attacker, oldLevel, newLevel, userid, 'kill')
        
        # Play the levelup sound
        gungamelib.playSound(attacker, 'levelup')
        
        return
    
    # Using multikill
    if weapon != 'knife' and weapon != 'hegrenade':
        gungameAttacker['multikill'] += 1
        
        # Finished the multikill
        if gungameAttacker['multikill'] == multiKill:
            # Set level variables
            oldLevel = gungameAttacker['level']
            newLevel = oldLevel + 1
            
            # Level them up
            gungamelib.triggerLevelUpEvent(attacker, oldLevel, newLevel, userid, 'kill')
            
            # Reset multikill
            gungameAttacker['multikill'] = 0
            
            # Play the levelup sound
            gungamelib.playSound(attacker, 'levelup')
        
        # Increment their current multikill value
        else:
            # Message the attacker
            multiKill = gungamelib.getLevelMultiKill(gungameAttacker['level'])
            gungamelib.hudhint('gungame', attacker, 'MultikillNotification', {'kills': gungameAttacker['multikill'], 'total': multiKill})
            
            # Play the multikill sound
            gungamelib.playSound(attacker, 'multikill')

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
    oldLevel = gungamePlayer['level']
    newLevel = oldLevel + 1
    gungamelib.triggerLevelUpEvent(userid, oldLevel, newLevel, '0', 'bomb_defused')

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
    oldLevel = gungamePlayer['level']
    newLevel = oldLevel + 1
    gungamelib.triggerLevelUpEvent(userid, oldLevel, newLevel, '0', 'bomb_exploded')
    
def player_team(event_var):
    # Get userid
    userid = int(event_var['userid'])
    
    # Was a disconnect?
    if int(event_var['disconnect']) == 1:
        return
    
    # Play welcome sound
    if int(event_var['oldteam']) < 2 and int(event_var['team']) > 1:
        gungamelib.playSound(userid, 'welcome')

def gg_levelup(event_var):
    # ============
    # WINNER CHECK
    # ============
    if int(event_var['old_level']) == gungamelib.getTotalLevels() and int(event_var['new_level']) > gungamelib.getTotalLevels():
        # Multi-round game
        if dict_variables['roundsRemaining'] > 1:
            es.event('initialize', 'gg_round_win')
            es.event('setint', 'gg_round_win', 'userid', event_var['attacker'])
            es.event('setint', 'gg_round_win', 'loser', event_var['userid'])
            es.event('setstring', 'gg_round_win', 'steamid', event_var['es_attackersteamid'])
            es.event('setint', 'gg_round_win', 'team', event_var['es_attackerteam'])
            es.event('setstring', 'gg_round_win', 'name', event_var['es_attackername'])
            es.event('fire', 'gg_round_win')
        
        # Normal win
        else:
            es.event('initialize', 'gg_win')
            es.event('setint', 'gg_win', 'userid', event_var['attacker'])
            es.event('setint', 'gg_win', 'loser', event_var['userid'])
            es.event('setstring', 'gg_win', 'steamid', event_var['es_attackersteamid'])
            es.event('setint', 'gg_win', 'team', event_var['es_attackerteam'])
            es.event('setstring', 'gg_win', 'name', event_var['es_attackername'])
            es.event('fire', 'gg_win')
        
        return
    
    # ===============
    # REGULAR LEVELUP
    # ===============
    # Get attacker info
    attacker = int(event_var['attacker'])
    gungamePlayer = gungamelib.getPlayer(attacker)
    
    # Player on knife level?
    if gungamelib.getLevelWeapon(event_var['new_level']) == 'knife':
        gungamelib.playSound('#all', 'knifelevel')
    
    # Player on nade level?
    if gungamelib.getLevelWeapon(event_var['new_level']) == 'hegrenade':
        gungamelib.playSound('#all', 'nadelevel')
    
    # Set player's new level and multikil
    gungamePlayer['level'] = int(event_var['new_level'])
    gungamePlayer['multikill'] = 0
    
    # Get leader level
    leaderLevel = gungamelib.leaders.getLeaderLevel()
    
    # Make new leader menu
    if leaderLevel == int(event_var['new_level']):
        rebuildLeaderMenu()
    
    # Show level info HUDHint
    if gungamelib.canShowHints():
        levelInfoHint(attacker)
    
    # ==================
    # VOTE TRIGGER CHECK
    # ==================
    if leaderLevel == (gungamelib.getTotalLevels() - gungamelib.getVariableValue('gg_vote_trigger')):
        # Nextmap already set?
        if es.ServerVar('eventscripts_nextmapoverride') != '':
            gungamelib.echo('gungame', 0, 0, 'MapSetBefore')
            return
        
        # Vote already started?
        if dict_variables['gungame_voting_started']:
            return
        
        if dict_variables['roundsRemaining'] < 2:
            es.event('initialize', 'gg_vote')
            es.event('fire', 'gg_vote')

def gg_leveldown(event_var):
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Set the player's level
    gungamePlayer['level'] = int(event_var['new_level'])

def gg_new_leader(event_var):
    rebuildLeaderMenu()

def gg_tied_leader(event_var):
    rebuildLeaderMenu()

def gg_leader_lostlevel(event_var):
    rebuildLeaderMenu()

def gg_vote(event_var):
    dict_variables['gungame_voting_started'] = True
    
    if gungamelib.getVariableValue('gg_map_vote') == 2:
        es.server.queuecmd(gungamelib.getVariableValue('gg_map_vote_command'))

def gg_round_win(event_var):
    global countBombDeathAsSuicide
    
    userid = int(event_var['userid'])
    index = playerlib.getPlayer(userid).get('index')
    playerName = event_var['name']
    steamid = event_var['steamid']

    # Create a variable to prevent bomb explosion deaths from counting a suicides
    countBombDeathAsSuicide = False
    
    # Calculate rounds remaining
    dict_variables['roundsRemaining'] -= 1
    
    # End the GunGame Round
    es.server.cmd('mp_restartgame 2')
    
    # Check to see if the warmup round needs to be activated
    if gungamelib.getVariableValue('gg_round_intermission') > 0:
        gungamelib.setGlobal('isIntermission', 1)
        es.load('gungame/included_addons/gg_warmup_round')
    
    # Reset all the players
    for userid in es.getUseridList():
        gungamelib.getPlayer(userid).resetPlayer()
    
    # Tell the world
    gungamelib.msg('gungame', '#all', 'PlayerWonRound', {'player': playerName})
    gungamelib.centermsg('gungame', '#all', 'PlayerWon_Center', {'player': playerName})
    
    # Play the winner sound
    gungamelib.playSound('#all', 'roundwinner')
    
    # Remove all old players
    gungamelib.clearOldPlayers()

def gg_win(event_var):
    global countBombDeathAsSuicide
    
    # Get player info
    userid = int(event_var['userid'])
    index = playerlib.getPlayer(userid).get('index')
    playerName = es.getplayername(userid)
    
    # Game is over
    gungamelib.setGlobal('gameOver', 1)
    
    # Create a variable to prevent bomb explosion deaths from counting a suicides
    countBombDeathAsSuicide = False
    
    # End game
    es.server.cmd('es_xgive %d game_end' % userid)
    es.server.cmd('es_xfire %d game_end EndGame' % userid)
    
    # Enable alltalk
    es.server.cmd('sv_alltalk 1')
    
    # Reset all the players
    for userid in es.getUseridList():
        gungamelib.getPlayer(userid).resetPlayer()
    
    # Tell the world
    gungamelib.msg('gungame', '#all', 'PlayerWon', {'player': playerName})
    gungamelib.centermsg('gungame', '#all', 'PlayerWon_Center', {'player': playerName})
    
    # Play the winner sound
    gungamelib.playSound('#all', 'winner')
    
    # Remove all old players from the dict_players
    gungamelib.clearOldPlayers()

def server_cvar(event_var):
    cvarName = event_var['cvarname']
    newValue = event_var['cvarvalue']
    
    if gungamelib.isNumeric(newValue):
        newValue = int(newValue)
    
    if cvarName not in gungamelib.getVariableList():
        return
    
    # Is a dependency?
    if cvarName in gungamelib.getDependencyList() and newValue != gungamelib.getDependencyValue(cvarName):
        # Tell them its protected
        gungamelib.echo('gungame', 0, 0, 'ProtectedDependency', {'name': cvarName})
        
        # Set back value
        gungamelib.setVariableValue(cvarName, gungamelib.getDependencyValue(cvarName))
        
        return
    
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
    
    # GG_MULTI_LEVEL
    elif cvarName == 'gg_multi_level':
        if newValue > 0 and 'gg_multi_level' not in gungamelib.getRegisteredAddonlist():
            es.server.queuecmd('es_load gungame/included_addons/gg_multi_level')
        elif newValue == 0 and 'gg_spawn_protect' in gungamelib.getRegisteredAddonlist():
            es.unload('gungame/included_addons/gg_multi_level')
    
    # GG_SPAWN_PROTECTION
    elif cvarName == 'gg_spawn_protect':
        if newValue > 0 and 'gg_spawn_protect' not in gungamelib.getRegisteredAddonlist():
            es.server.queuecmd('es_load gungame/included_addons/gg_spawn_protect')
        elif newValue == 0 and 'gg_spawn_protect' in gungamelib.getRegisteredAddonlist():
            es.unload('gungame/included_addons/gg_spawn_protect')
    
    # GG_RETRY_PUNISH
    elif cvarName == 'gg_retry_punish':
        if newValue > 0 and 'gg_retry_punish' not in gungamelib.getRegisteredAddonlist():
            es.server.queuecmd('es_load gungame/included_addons/gg_retry_punish')
        elif newValue == 0 and 'gg_retry_punish' in gungamelib.getRegisteredAddonlist():
            es.unload('gungame/included_addons/gg_retry_punish')
    
    # GG_FRIENDLYFIRE
    elif cvarName == 'gg_friendlyfire':
        if newValue > 0 and 'gg_friendlyfire' not in gungamelib.getRegisteredAddonlist():
            es.server.queuecmd('es_load gungame/included_addons/gg_friendlyfire')
        elif newValue == 0 and 'gg_friendlyfire' in gungamelib.getRegisteredAddonlist():
            es.unload('gungame/included_addons/gg_friendlyfire')
    
    # GG Multi Round
    elif cvarName == 'gg_multi_round':
        # Reset the "rounds remaining" variable for multi-rounds
        dict_variables['roundsRemaining'] = gungamelib.getVariableValue('gg_multi_round')
    
    # Included addons
    elif cvarName in list_includedAddonsDir:
        if newValue == 1:
            es.server.queuecmd('es_load gungame/included_addons/%s' % cvarName)
        elif newValue == 0 and cvarName in gungamelib.getRegisteredAddonlist():
            es.unload('gungame/included_addons/%s' % cvarName)
    
    # Multikill override
    elif cvarName == 'gg_multikill_override':
        newValue = gungamelib.clamp(newValue, 0)
        
        # Get weapon order
        weaponOrder = gungamelib.getWeaponOrder(gungamelib.getVariableValue('gg_weapon_order_file'))
        
        # Set multikill
        if newValue == 0:
            weaponOrder.setMultiKillDefaults()
        else:
            weaponOrder.setMultiKillOverride(newValue)
    
    # Weapon order file
    elif cvarName == 'gg_weapon_order_file':
        # Dont set the weapon order file if its not registered
        if not gungamelib.dict_weaponOrders.has_key(newValue):
            gungamelib.echo('gungame', 0, 0, 'WeaponOrderNotRegistered', {'file': newValue})
            gungamelib.getVariable('gg_weapon_order_file').set('default_weapon_order.txt')
            return
        
        # Parse the new file
        myWeaponOrder = gungamelib.getWeaponOrder(newValue)
        myWeaponOrder.setWeaponOrderFile()
        
        # Set multikill override
        if gungamelib.getVariableValue('gg_multikill_override') != 0:
            myWeaponOrder.setMultiKillOverride(gungamelib.getVariableValue('gg_multikill_override'))
    
    # Fire event
    es.event('initialize', 'gg_variable_changed')
    es.event('setstring', 'gg_variable_changed', 'name', cvarName)
    es.event('setstring', 'gg_variable_changed', 'value', newValue)
    es.event('fire', 'gg_variable_changed')

# ==============================================================================
#   HELPER FUNCTIONS
# ==============================================================================
def loadCustom(addonName):
    es.load('gungame/custom_addons/' + str(addonName))
    
def unloadCustom(addonName):
    es.unload('gungame/custom_addons/' + str(addonName))

def afkPunishCheck(userid):
    gungamePlayer = gungamelib.getPlayer(userid)
    afkMaxAllowed = gungamelib.getVariableValue('gg_afk_rounds')
    
    # Is AFK punishment enabled?
    if afkMaxAllowed > 0:
        # Increment the afk round attribute
        gungamePlayer['afkrounds'] += 1
        
        # Have been AFK for too long
        if gungamePlayer['afkrounds'] >= afkMaxAllowed:
            # Kick the player
            if gungamelib.getVariableValue('gg_afk_action') == 1:
                es.server.cmd('kickid %d "You were AFK for too long."' % userid)
            
            # Show menu
            elif gungamelib.getVariableValue('gg_afk_action') == 2:
                # Send them to spectator
                es.server.cmd('es_xfire %d !self SetTeam 1' % userid)
                
                # Send a popup saying they were switched
                menu = popuplib.create('gungame_afk')
                menu.addline(gungamelib.lang('gungame', 'SwitchedToSpectator'))
                menu.send(userid)
                
            # Reset the AFK rounds back to 0
            gungamePlayer['afkrounds'] = 0

def equipPlayer():
    userid = es.getuserid()
    es.server.cmd('es_xremove game_player_equip')
    es.server.cmd('es_xgive %s game_player_equip' % userid)
    es.server.cmd('es_xfire %s game_player_equip AddOutput "weapon_knife 1"' % userid)
    
    # Retrieve the armor type
    armorType = gungamelib.getVariableValue('gg_player_armor')
    
    # Give the player full armor
    if armorType == 2:
        es.server.cmd('es_xfire %s game_player_equip AddOutput "item_assaultsuit 1"' % userid)
    
    # Give the player kevlar only
    elif armorType == 1:
        es.server.cmd('es_xfire %s game_player_equip AddOutput "item_kevlar 1"' % userid)

def levelInfoHint(userid):
    # Get variables
    gungamePlayer = gungamelib.getPlayer(userid)
    leaderLevel = gungamelib.leaders.getLeaderLevel()
    levelsBehindLeader = leaderLevel - gungamePlayer['level']
    multiKill = gungamelib.getLevelMultiKill(gungamePlayer['level'])
    
    # Start text
    text =  gungamelib.lang('gungame', 'LevelInfo_CurrentLevel', {'level': gungamePlayer['level'], 'total': gungamelib.getTotalLevels()})
    text += gungamelib.lang('gungame', 'LevelInfo_CurrentWeapon', {'weapon': gungamelib.getLevelWeapon(gungamePlayer['level'])})
    
    # Multikill?
    if multiKill > 1:
        text += gungamelib.lang('gungame', 'LevelInfo_RequiredKills', {'kills': gungamePlayer['multikill'], 'total': multiKill})
    
    # ===========
    # ONLY LEADER
    # ===========
    if levelsBehindLeader == 0 and gungamelib.leaders.getLeaderCount() == 1:
        text += gungamelib.lang('gungame', 'LevelInfo_CurrentLeader')
        
        # Send hint
        sendLevelInfoHint(userid, text)
        return
    
    # ==========
    # NO LEADERS
    # ==========
    if levelsBehindLeader == 0 and leaderLevel == 1:
        text += gungamelib.lang('gungame', 'LevelInfo_NoLeaders')
        
        # Send hint
        sendLevelInfoHint(userid, text)
        return
    
    # ================
    # MULTIPLE LEADERS
    # ================
    if levelsBehindLeader == 0 and gungamelib.leaders.getLeaderCount() > 1:
        text += gungamelib.lang('gungame', 'LevelInfo_AmongstLeaders')
        
        # Add leader name(s)
        text += gungamelib.lang('gungame', 'LevelInfo_LeaderName', {
            'plural': 's',
            'names': ', '.join(gungamelib.leaders.getLeaderNames())
        })
        
        # Send hint
        sendLevelInfoHint(userid, text)
        return
    
    # Add leader name(s)
    text += gungamelib.lang('gungame', 'LevelInfo_LeaderName', {
        'plural': 's' if gungamelib.leaders.getLeaderCount() > 1 else '',
        'names': ', '.join(gungamelib.leaders.getLeaderNames())
    })
    
    # Add leader level
    text += gungamelib.lang('gungame', 'LevelInfo_LeaderLevel', {
        'level': gungamelib.leaders.getLeaderLevel(),
        'total': gungamelib.getTotalLevels(),
        'weapon': gungamelib.getLevelWeapon(gungamelib.leaders.getLeaderLevel())
    })
    
    # Send hint
    sendLevelInfoHint(userid, text)

def sendLevelInfoHint(userid, text):
    # Is a vote active?
    if gungamelib.getGlobal('voteActive'):
        return
    
    # Is warmup round?
    if gungamelib.getGlobal('isWarmup'):
        return
    
    # Send hint
    gamethread.delayed(0.5, usermsg.hudhint, (str(userid), text))

# ==============================================================================
#   POPUP COMMANDS
# ==============================================================================
def displayWeaponOrderMenu(userid):
    gungamelib.sendWeaponOrderMenu(userid)

def displayLevelMenu(userid, player=None):
    if not player:
        popuplib.send('gungameLevelMenu', userid)
        return
    
    checkUserid = es.getuserid(player)
    
    if not checkUserid:
        gungamelib.msg('gungame', userid, 'LevelInfo_PlayerSearchFailed', {'player': player})
        return
    
    gungamePlayer = gungamelib.getPlayer(levelCheckUserid)
    gungamelib.saytext2('gungame', userid, gungamePlayer['index'], 'LevelInfo_PlayerSearch', {'player': es.getplayername(levelCheckUserid), 'level': gungamePlayer['level'], 'weapon': gungamePlayer.getWeapon()}, False)

def buildLevelMenu():
    # Delete the popup if it exists
    if popuplib.exists('gungameLevelMenu'):
        popuplib.unsendname('gungameLevelMenu', playerlib.getUseridList('#human'))
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
        gungameLevelMenu.modline(3, '   * You need a %s kills to advance' %gungamePlayer.getWeapon()) # Line #3
    else:
        gungameLevelMenu.modline(2, '   * You are on level %d (%s)' %(gungamePlayer['level'], gungamePlayer.getWeapon())) # Line #2
        gungameLevelMenu.modline(3, '   * You have made %d/%d of your required kills' %(gungamePlayer['multikill'], gungamelib.getVariableValue('gg_multikill_override'))) # Line #3
    
    leaderLevel = gungamelib.leaders.getLeaderLevel()
    playerLevel = gungamePlayer['level']
    
    if leaderLevel > 1:
        # See if the player is a leader:
        if playerLevel == leaderLevel:
            # See if there is more than 1 leader
            if gungamelib.leaders.getLeaderCount() > 1:
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
        gungameLevelMenu.modline(6, '   * You have won %d time(s)' %gungamelib.getWins(gungamePlayer['steamid'])) # Line #6
        if leaderLevel > 1:
            gungameLevelMenu.modline(8, '   * Leader Level: %d (%s)' %(leaderLevel, gungamelib.getLevelWeapon(leaderLevel))) # Line #8
        else:
            gungameLevelMenu.modline(8, '   * Leader Level: There are no leaders') # Line #8
    else:
        if leaderLevel > 1:
            gungameLevelMenu.modline(6, '   * Leader Level: %d (%s)' %(leaderLevel, gungamelib.getLevelWeapon(leaderLevel))) # Line #6
        else:
            gungameLevelMenu.modline(6, '   * Leader Level: There are no leaders') # Line #6

def displayLeadersMenu(userid):
    popuplib.send('gungameLeadersMenu', userid)

def buildLeaderMenu():
    # Check if the popup exists
    if popuplib.exists('gungameLeadersMenu'):
        # Unsend and delete is
        popuplib.unsendname('gungameLeadersMenu', playerlib.getUseridList('#human'))
        popuplib.delete('gungameLeadersMenu')
    
    # Create the menu
    gungameLeadersMenu = popuplib.create('gungameLeadersMenu')
    gungameLeadersMenu.addline('->1. Current Leaders:')
    gungameLeadersMenu.addline('--------------------------')
    gungameLeadersMenu.addline('   * There currently is no leader')
    gungameLeadersMenu.addline('--------------------------')
    gungameLeadersMenu.addline('0. Exit')
    gungameLeadersMenu.timeout('send', 5)
    gungameLeadersMenu.timeout('view', 5)

def rebuildLeaderMenu():
    # Un-send and delete the menu
    if popuplib.exists('gungameLeadersMenu'):
        popuplib.unsendname('gungameLeadersMenu', playerlib.getUseridList('#human'))
        popuplib.delete('gungameLeadersMenu')
    
    # Get leader info
    leaderLevel = gungamelib.leaders.getLeaderLevel()
    leaderNames = gungamelib.leaders.getLeaderNames()
    
    # Let's create the "gungameLeadersMenu" popup
    gungameLeadersMenu = popuplib.create('gungameLeadersMenu')
    gungameLeadersMenu.addline('->1. Current Leaders:')
    gungameLeadersMenu.addline('    Level %d (%s)' % (leaderLevel, gungamelib.getLevelWeapon(leaderLevel)))
    gungameLeadersMenu.addline('--------------------------')
    
    # Add leaders
    for name in leaderNames:
        gungameLeadersMenu.addline('   * %s' % name)
    
    # Finish off the menu
    gungameLeadersMenu.addline('--------------------------')
    gungameLeadersMenu.addline('0. Exit')
    gungameLeadersMenu.timeout('send', 5)
    gungameLeadersMenu.timeout('view', 5)