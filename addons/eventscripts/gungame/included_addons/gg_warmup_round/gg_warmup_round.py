'''
(c)2007 by the GunGame Coding Team

    Title:      gg_warmup_round
Version #:      1.2.2008
Description:    GunGame WarmUp Round allows players to begin warming up for
                the upcoming GunGame round without allowing them to level up,
                also allowing connecting players to get a full connection to
                the server prior to the GunGame Round starting.
'''

import es
import gamethread
import usermsg
import playerlib
import repeat

from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_warmup_round Addon for GunGame: Python" 
info.version  = "1.2.2008"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_warmup_round" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2008, Saul"

# Begin Multiple Error Classes
class _GunGameQueryError:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class WarmUpWeaponError(_GunGameQueryError):
    pass

list_allWeapons = ['knife', 'glock', 'usp', 'p228', 'deagle', 'elite', 'fiveseven', 'awp', 'scout', 'aug', 'mac10', 'tmp', 'mp5navy', 'ump45', 'p90', 'galil', 'famas', 'ak47', 'sg552', 'sg550', 'g3sg1', 'm249', 'm3', 'xm1014', 'm4a1', 'hegrenade', 'flashbang', 'smokegrenade']
mp_freezetimeBackUp = 0

def load():
    global mp_freezetimeBackUp
    global warmupTime
    
    # Cancel the delay to set PreventLevel for everyone to "0"
    gamethread.cancelDelayed('setPreventAll0')
    
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_warmup_round', 'GG WarmUp Round')
    
    # Create a dictionary of players on the server for the following loop
    dict_gungamePlayers = es.createplayerlist()
    
    # Set PreventAll to "1" for everyone
    gungame.setPreventLevelAll(1)
    
    # Set a variable to hold the amount of WarmUp Time
    warmupTime = int(gungame.getGunGameVar('gg_warmup_timer')) + 1
    
    # Retrieve the warmup weapon
    warmupWeapon = gungame.getGunGameVar('gg_warmup_weapon')
    
    # Start the countdown timer
    gamethread.delayed(3, startTimer, ())
    
    # Make sure there is supposed to be a warmup weapon
    if str(warmupWeapon) != '0':
        # Make sure the warmup weapon is a valid weapon choice
        if warmupWeapon not in list_allWeapons:
            # Nope, the admin typoed it. Let's set it to 0 so that we don't have to worry about this later
            gungame.setGunGameVar('gg_warmup_weapon', '0')
            
            # Kick out an error due to the typo by the admin
            raise WarmUpWeaponError, warmupWeapon + ' is not a valid weapon. Setting \'gg_warmup_weapon\' to level 1\'s weapon.'
            
    # Backup "mp_freezetime" variable to reset it later
    mp_freezetimeBackUp = int(es.ServerVar('mp_freezetime'))
    
    # Set "mp_freezetime" to 0
    es.server.cmd('mp_freezetime 0')

def unload():
    global mp_freezetimeBackUp
    
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_warmup_round')
    
    # Create a dictionary of players on the server for the following loop
    dict_gungamePlayers = es.createplayerlist()
    
    # Set everyone's PreventLevel to 0
    gungame.setPreventLevelAll(0)
    
    # Cancel the "gungameWarmUpRound" delay
    gamethread.cancelDelayed('gungameWarmUpRound')
    
    # Return "mp_freezetime" to what it was originally
    es.server.cmd('mp_freezetime %d' %mp_freezetimeBackUp)

def startTimer():
    # Create a repeat
    repeat.create('WarmupTimer', countDown)
    repeat.start('WarmupTimer', 1, 0)

def gg_variable_changed(event_var):
    # if the "gg_warmup_timer" is changed to 0, we need to unload this bad-boy
    if event_var['cvarname'] == 'gg_warmup_timer' and event_var['newvalue'] == '0':
        es.unload('gungame/included_addons/gg_warmup_round')

def player_activate(event_var):
    userid = int(event_var['userid'])
    
    # Set the PreventLevel to "1" for late joiners
    gungamePlayer = gungame.getPlayer(userid)
    gungamePlayer.set('PreventLevel', 1)

def player_spawn(event_var):
    # Is a spectator?
    if event_var['es_userteam'] == 1:
        return
    
    # Get player userid and player object
    userid = int(event_var['userid'])
    playerlibPlayer = playerlib.getPlayer(userid)
    
    # See if the admin wants to give something other than the level 1 weapon
    if event_var['es_userteam'] > 1 and not playerlibPlayer.get('isdead'):
        if str(gungame.getGunGameVar('gg_warmup_weapon')) != '0':
            # Check to make sure that the WarmUp Weapon is not a knife
            if gungame.getGunGameVar('gg_warmup_weapon') != 'knife':
                # Give the player the WarmUp Round Weapon
                es.sexec(userid, 'use weapon_knife')
                es.server.cmd('es_xgive %s weapon_%s' %(userid, gungame.getGunGameVar('gg_warmup_weapon')))
            else:
                es.sexec(userid, 'use weapon_knife')
        else:
            # It looks like we are giving them the level 1 weapon...
            gungame.giveWeapon(userid)

def hegrenade_detonate(event_var):
    # Get player userid and player object
    userid = event_var['userid']
    playerlibPlayer = playerlib.getPlayer(userid)
    
    # Give user a hegrenade, if eligable
    if event_var['es_userteam'] > 1 and not playerlibPlayer.get('isdead') and gungame.getGunGameVar('gg_warmup_weapon') == 'hegrenade':
        es.server.cmd('es_xgive %s weapon_hegrenade' % userid)

def countDown(repeatInfo):
    global warmupTime
    
    # If the remaining time is greater than 1
    if warmupTime >= 1:
        # Loop through the players
        for userid in playerlib.getUseridList('#all'):
            # Send a hudhint to userid with the remaining timeleft
            usermsg.hudhint(userid, 'Warmup round timer: %d' % warmupTime)
            
            # Countdown 5 or less?
            if warmupTime <= 5:
                es.cexec(userid, 'playgamesound hl1/fvox/beep.wav')
        
        # If warmuptime is 1, start game restart
        if warmupTime == 2:
            es.server.cmd('mp_restartgame 2')
        
        # Decrement the timeleft counter
        warmupTime -= 1
    elif warmupTime == 0:
        for userid in playerlib.getUseridList('#all'):
            # Send a hudhint to userid that the warmup round has ended
            usermsg.hudhint(userid, 'Warmup round timer: 0')
        
        # Play beep
        es.cexec_all('playgamesound hl1/fvox/beep.wav')
        
        # Stop the timer
        repeat.stop('WarmupTimer')
        
        # Unload "gungame/included_addons/gg_warmup_round" in 2 seconds
        gamethread.delayed(1, es.unload, ('gungame/included_addons/gg_warmup_round'))