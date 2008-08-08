''' (c) 2008 by the GunGame Coding Team

    Title: gg_warmup_round
    Version: 1.0.442
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
import usermsg
import playerlib
import testrepeat as repeat

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_warmup_round Addon for GunGame: Python'
info.version  = '1.0.442'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
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

dict_addonVars = {'warmupTime':0,
                  'mp_freezetimeBackUp':0,
                  'unloadDeathmatch':0,
                  'unloadElimination':0}

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():    
    # Set the warmupTime variable for new use
    dict_addonVars['warmupTime'] = warmupTimeVariable + 1
    
    # Register addon with gungamelib
    gg_warmup_round = gungamelib.registerAddon('gg_warmup_round')
    gg_warmup_round.setDisplayName('GG Warmup Round')

    # Set "isWarmup" global
    gungamelib.setGlobal('isWarmup', 1)
    
    # Check to see if we should load deathmatch for warmup round
    if gungamelib.getVariableValue('gg_warmup_deathmatch'):
        if not gungamelib.getVariableValue('gg_deathmatch'):
            dict_addonVars['unloadDeathmatch'] = 1
            es.server.cmd('gg_deathmatch 1')
        
    # Check to see if we should load elimination for warmup round
    if gungamelib.getVariableValue('gg_warmup_elimination'):
        if not gungamelib.getVariableValue('gg_elimination'):
            dict_addonVars['unloadElimination'] = 1
            es.server.cmd('gg_elimination 1')
    
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
        if warmupWeapon not in gungamelib.getWeaponList('all'):
            # Nope, the admin typoed it. Let's set it to 0 so that we don't have to worry about this later
            gungamelib.setVariableValue('gg_warmup_weapon', 0)
            
            # Kick out an error due to the typo by the admin
            raise WarmUpWeaponError, warmupWeapon + ' is not a valid weapon. Setting \'gg_warmup_weapon\' to level 1\'s weapon.'
            
    # Backup "mp_freezetime" variable to reset it later
    dict_addonVars['mp_freezetimeBackUp'] = int(es.ServerVar('mp_freezetime'))
    
    # Set "mp_freezetime" to 0
    es.forcevalue('mp_freezetime', 0)

def unload():
    # Check to see if we should load deathmatch for warmup round
    if dict_addonVars['unloadDeathmatch']:
        es.server.cmd('gg_deathmatch 0')
        
    # Check to see if we should load elimination for warmup round
    if dict_addonVars['unloadElimination']:
        es.server.cmd('gg_elimination 0')
    
    # Set everyone's PreventLevel to 0
    gamethread.delayed(3, gungamelib.setPreventLevelAll, (0, 'gg_warmup_round'))
    
    # Cancel the "gungameWarmUpRound" delay
    gamethread.cancelDelayed('gungameWarmUpRound')
    
    # Check to see if repeat is still going
    if repeat.find('gungameWarmupTimer'):
        if repeat.status('gungameWarmupTimer'):
            repeat.delete('gungameWarmupTimer')
    
    # Return "mp_freezetime" to what it was originally
    es.forcevalue('mp_freezetime', dict_addonVars['mp_freezetimeBackUp'])
    
    # Set "isWarmup" global
    gungamelib.setGlobal('isWarmup', 0)
    gungamelib.setGlobal('isIntermission', 0)
    '''We will leave preventlevel active, as we will be setting it to 0 with a 3 second delay
    NOTE: It is not customary or advisable to use the "removePreventLevel=False" argument in
          scripts unless you will be using a delay to gungamelib.setPreventLevelAll(0). This
          is the ONLY reason we provide the "removePreventLevel" argument with the
          "unregisterAddon" command.
    '''
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_warmup_round', removePreventLevel=False)

def player_activate(event_var):
    userid = int(event_var['userid'])
    
    # Set the PreventLevel to "1" for late joiners
    gungamelib.getPlayer(userid).setPreventLevel(1, 'gg_warmup_round')

def player_spawn(event_var):
    userid = int(event_var['userid'])

    # Is a spectator or dead?
    if int(event_var['es_userteam']) <= 1 or es.getplayerprop(userid, 'CCSPlayer.baseclass.pl.deadflag'):
        return
    
    # See if the admin wants to give something other than the level 1 weapon
    if gungamelib.getVariableValue('gg_warmup_weapon') != 0:
        # Check to make sure that the WarmUp Weapon is not a knife
        if gungamelib.getVariableValue('gg_warmup_weapon') != 'knife':
            # Give the player the WarmUp Round Weapon
            es.sexec(userid, 'use weapon_knife')
            es.server.cmd('es_xgive %s weapon_%s' % (userid, gungamelib.getVariableValue('gg_warmup_weapon')))
        else:
            es.sexec(userid, 'use weapon_knife')
    else:
        # It looks like we are giving them the level 1 weapon...
        gungamePlayer = gungamelib.getPlayer(userid)
        gungamePlayer.giveWeapon()

def hegrenade_detonate(event_var):
    # Get player userid and player object
    userid = event_var['userid']
    
    # Is the client on the server?
    if not gungamelib.clientInServer(userid):
        return
    
    playerlibPlayer = playerlib.getPlayer(userid)
    
    # Give user a hegrenade, if eligable
    if int(event_var['es_userteam']) > 1 and not playerlibPlayer.get('isdead') and gungamelib.getVariableValue('gg_warmup_weapon') == 'hegrenade':
        es.server.cmd('es_xgive %s weapon_hegrenade' % userid)

def startTimer():
    # Create a repeat
    repeat.create('gungameWarmupTimer', countDown)
    repeat.start('gungameWarmupTimer', 1, warmupTimeVariable + 3)
    
    # Create timeleft global
    gungamelib.setGlobal('warmupTimeLeft', dict_addonVars['warmupTime'])

# ==============================================================================
#  COUNTDOWN CODE
# ==============================================================================
def countDown():
    # If the remaining time is greater than 1
    if dict_addonVars['warmupTime'] >= 1:
        # Send hint
        if dict_addonVars['warmupTime'] > 1:
            gungamelib.hudhint('gg_warmup_round', '#all', 'Timer_Plural', {'time': dict_addonVars['warmupTime']})
        else:
            gungamelib.hudhint('gg_warmup_round', '#all', 'Timer_Singular')
        
        # Set timeleft global
        gungamelib.setGlobal('warmupTimeLeft', dict_addonVars['warmupTime'])
        
        # Countdown 5 or less?
        if dict_addonVars['warmupTime'] <= 5:
            gungamelib.playSound('#all', 'countDownBeep')
        
        # If warmuptime is 1, start game restart
        if dict_addonVars['warmupTime'] == 2:
            es.server.cmd('mp_restartgame 2')
        
        # Decrement the timeleft counter
        dict_addonVars['warmupTime'] -= 1
    elif dict_addonVars['warmupTime'] == 0:
        # Send hint
        gungamelib.hudhint('gg_warmup_round', '#all', 'Timer_Ended')
        
        # Play beep
        gungamelib.playSound('#all', 'countDownBeep')
        
        # Stop the timer
        repeat.delete('gungameWarmupTimer')
        
        gungamelib.setGlobal('isWarmup', 0)
        
        # Unload "gungame/included_addons/gg_warmup_round"
        es.unload('gungame/included_addons/gg_warmup_round')
        
        # Fire gg_start event
        es.event('initialize','gg_start')
        es.event('fire','gg_start')