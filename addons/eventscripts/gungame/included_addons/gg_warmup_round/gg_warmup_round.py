''' (c) 2008 by the GunGame Coding Team

    Title: gg_warmup_round
    Version: 5.0.577
    Description: GunGame WarmUp Round allows players to begin warming up for
                 the upcoming GunGame round without allowing them to level up,
                 also allowing connecting players to get a full connection to
                 the server prior to the GunGame Round starting.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import gamethread
import playerlib
import testrepeat as repeat

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_warmup_round (for GunGame5)'
info.version  = '5.0.577'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_warmup_round'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  ERROR CLASSES
# ==============================================================================
class WarmUpWeaponError(Exception):
    pass

# ==============================================================================
#  GLOBALS
# ==============================================================================
if gungamelib.getGlobal('isIntermission'):
    warmupTimeVariable = gungamelib.getVariable('gg_round_intermission')
else:
    warmupTimeVariable = gungamelib.getVariable('gg_warmup_timer')

dict_addonVars = {'mp_freezetimeBackUp':0,
                  'unloadDeathmatch':0,
                  'unloadElimination':0}

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_warmup_round = gungamelib.registerAddon('gg_warmup_round')
    gg_warmup_round.setDisplayName('GG Warmup Round')
    gg_warmup_round.loadTranslationFile()
    
    # Set "isWarmup" global
    gungamelib.setGlobal('isWarmup', 1)
    
    # Set "unloadWarmup" global
    gungamelib.setGlobal('unloadWarmUp', 0)
    
    # Check to see if we should load deathmatch for warmup round
    if gungamelib.getVariableValue('gg_warmup_deathmatch'):
        if not gungamelib.getVariableValue('gg_deathmatch'):
            dict_addonVars['unloadDeathmatch'] = 1
            es.server.queuecmd('gg_deathmatch 1')
        
    # Check to see if we should load elimination for warmup round
    if gungamelib.getVariableValue('gg_warmup_elimination'):
        if not gungamelib.getVariableValue('gg_elimination'):
            dict_addonVars['unloadElimination'] = 1
            es.server.queuecmd('gg_elimination 1')
    
    # Cancel the delay to set PreventLevel for everyone to "0"
    gamethread.cancelDelayed('setPreventAll0')
    
    # Set PreventAll to "1" for everyone
    gungamelib.setPreventLevelAll(1, 'gg_warmup_round')
    
    # Retrieve the warmup weapon
    warmupWeapon = gungamelib.getVariableValue('gg_warmup_weapon')
    
    # Start the countdown timer
    gamethread.delayed(3, startTimer, ())
    
    # Make sure there is supposed to be a warmup weapon
    if str(warmupWeapon) != '0':
        # Make sure the warmup weapon is a valid weapon choice
        if warmupWeapon not in gungamelib.getWeaponList('valid') + ['flashbang', 'smokegrenade']:
            # Nope, the admin typoed it. Let's set it to 0 so that we don't have to worry about this later
            gungamelib.setVariableValue('gg_warmup_weapon', 0)
            
            # Kick out an error due to the typo by the admin
            raise WarmUpWeaponError, warmupWeapon + ' is not a valid weapon. Setting \'gg_warmup_weapon\' to level 1\'s weapon.'
            
    # Backup "mp_freezetime" variable to reset it later
    dict_addonVars['mp_freezetimeBackUp'] = int(es.ServerVar('mp_freezetime'))
    
    # Set "mp_freezetime" to 0
    es.forcevalue('mp_freezetime', 0)

def unload():
    # Set everyone's PreventLevel to 0
    gungamelib.setPreventLevelAll(0, 'gg_warmup_round')
    
    # Cancel the "gungameWarmUpRound" delay
    gamethread.cancelDelayed('gungameWarmUpRound')
    
    # Check to see if repeat is still going
    if repeat.find('gungameWarmupTimer'):
        if repeat.status('gungameWarmupTimer'):
            repeat.delete('gungameWarmupTimer')
    
    # Return "mp_freezetime" to what it was originally
    es.forcevalue('mp_freezetime', dict_addonVars['mp_freezetimeBackUp'])
    
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_warmup_round')

def es_map_start(event_var):
    warmupCountDown = repeat.find('gungameWarmupTimer')
    
    if warmupCountDown:
        # Restart the repeat
        warmupCountDown.stop()
        warmupCountDown.start(1, warmupTimeVariable + 3)

def round_start(event_var):
    if not gungamelib.getGlobal('unloadWarmup'):
        return
    
    gungamelib.setGlobal('isWarmup', 0)
    gungamelib.setGlobal('isIntermission', 0)
    
    # Unload warmup
    es.unload('gungame/included_addons/gg_warmup_round')
    
def player_activate(event_var):
    userid = int(event_var['userid'])
    
    # Set the PreventLevel to "1" for late joiners
    gungamelib.getPlayer(userid).setPreventLevel(1, 'gg_warmup_round')

def player_spawn(event_var):
    if gungamelib.getGlobal('unloadWarmup'):
        return
    
    userid = int(event_var['userid'])

    # Is a spectator or dead?
    if int(event_var['es_userteam']) <= 1 or gungamelib.isDead(userid):
        return
    
    # Get player object
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Check if the warmup weapon is the level 1 weapon
    if gungamelib.getVariableValue('gg_warmup_weapon') == 0:
        gungamePlayer.giveWeapon()
        return
    
    # Check if the warmup weapon is a knife
    if gungamelib.getVariableValue('gg_warmup_weapon') == 'knife':
        es.sexec(userid, 'use weapon_knife')
        return
    
    # Do we need this line? They will only spawn with a knife, and should already be holding it.
    # es.sexec(userid, 'use weapon_knife')
    
    # Delay giving the weapon by a split second, because the code in round start removes all weapons
    gamethread.delayed(0, gungamePlayer.give, (gungamelib.getVariableValue('gg_warmup_weapon')))

def hegrenade_detonate(event_var):
    if gungamelib.getGlobal('unloadWarmup'):
        return
    
    # Get player userid and player object
    userid = event_var['userid']
    
    # Is the client on the server?
    if not gungamelib.clientInServer(userid):
        return
    
    # Give user a hegrenade, if eligable
    if int(event_var['es_userteam']) > 1 and not gungamelib.isDead(userid) and gungamelib.getVariableValue('gg_warmup_weapon') == 'hegrenade':
        gungamelib.getPlayer(userid).give('hegrenade')

def startTimer():
    # Create a repeat
    warmupCountDown = repeat.create('gungameWarmupTimer', countDown)
    warmupCountDown.start(1, warmupTimeVariable + 3)

# ==============================================================================
#  COUNTDOWN CODE
# ==============================================================================
def countDown():
    warmupCountDown = repeat.find('gungameWarmupTimer')
    
    if not warmupCountDown:
        return
        
    # If the remaining time is greater than 1
    if warmupCountDown['remaining'] >= 1:
        # Send hint
        if warmupCountDown['remaining'] > 1:
            gungamelib.hudhint('gg_warmup_round', '#all', 'Timer_Plural', {'time': warmupCountDown['remaining']})
        else:
            gungamelib.hudhint('gg_warmup_round', '#all', 'Timer_Singular')
        
        # Countdown 5 or less?
        if warmupCountDown['remaining'] <= 5:
            gungamelib.playSound('#all', 'countDownBeep')
        
        # mp_restartgame and trigger round_end
        if warmupCountDown['remaining'] == 1:
            es.server.queuecmd('mp_restartgame 1')
            gungamelib.setGlobal('unloadWarmUp', 1)
    
    # No time left
    elif warmupCountDown['remaining'] == 0:
        # Send hint
        gungamelib.hudhint('gg_warmup_round', '#all', 'Timer_Ended')
        
        # Play beep
        gungamelib.playSound('#all', 'countDownBeep')
        
        # Stop the timer
        repeat.delete('gungameWarmupTimer')
        
        # Fire gg_start event
        es.event('initialize', 'gg_start')
        es.event('fire', 'gg_start')
        
        # Set "isWarmup" global
        gungamelib.setGlobal('isWarmup', 0)
        gungamelib.setGlobal('isIntermission', 0)
        
        # Check to see if we should load deathmatch for warmup round
        if dict_addonVars['unloadDeathmatch']:
            es.server.queuecmd('gg_deathmatch 0')
        
        # Check to see if we should load elimination for warmup round
        if dict_addonVars['unloadElimination']:
            es.server.queuecmd('gg_elimination 0')
        
        # Don't allow anyone to spawn until next round
        gungamelib.setGlobal('respawn_allowed', 0)