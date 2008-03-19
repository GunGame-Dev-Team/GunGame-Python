'''
(c)2007 by the GunGame Coding Team

    Title:      gg_spawn_protection
Version #:      1.0.119
Description:    This will make players invincible and marked with color when
                ever a player spawns.  Protected players cannot level up during
                spawn protection.
'''

# EventScripts imports
import es
import playerlib
import gamethread
import repeat

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_spawn_protection"
info.version  = "1.0.119"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_spawn_protect"
info.author   = "GunGame Development Team"

# Addon settings
dict_SpawnProtectVars = {}
dict_SpawnProtectVars['red'] = gungamelib.getVariableValue('gg_spawn_protect_red')
dict_SpawnProtectVars['green'] = gungamelib.getVariableValue('gg_spawn_protect_green')
dict_SpawnProtectVars['blue'] = gungamelib.getVariableValue('gg_spawn_protect_blue')
dict_SpawnProtectVars['alpha'] = gungamelib.getVariableValue('gg_spawn_protect_alpha')
dict_SpawnProtectVars['delay'] = gungamelib.getVariableValue('gg_spawn_protect')

playerCounters = {}
originalNoisy = 0

def load():
    # Register
    gg_spawn_protect = gungamelib.registerAddon('gg_spawn_protect')
    gg_spawn_protect.setMenuText('GG Spawn Protection')
    
    # Set noisy to 1
    originalNoisy = int(es.ServerVar('eventscripts_noisy'))
    es.ServerVar('eventscripts_noisy').set(1)

def unload():
    # Unregister
    gungamelib.unregisterAddon('gg_spawn_protect')
    
    es.ServerVar('eventscripts_noisy').set(originalNoisy)

def server_cvar(event_var):
    # Register change in gg_map_list_file
    if event_var['cvarname'] == 'gg_spawn_protect':
        dict_SpawnProtectVars['delay'] = gungamelib.getVariableValue('gg_spawn_protect')

def player_spawn(event_var):
    # Is a warmup round?
    if gungamelib.getGlobal('isWarmup') == '1':
        return
    
    # Get userid and player object
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Start countdown
    startCountdown(userid)
    
    # See if prevent level is already turned on
    if not gungamePlayer['preventlevel']:
        gungamePlayer['preventlevel'] = 1
        gamethread.delayed(dict_SpawnProtectVars['delay'], setPreventLevelZero, (userid))

def player_disconnect(event_var):
    # Get userid
    userid = int(event_var['userid'])
    
    # Is the player invincible?
    if playerCounters.has_key(userid):
        finishCountdown(userid, False)

def player_death(event_var):
    # Get userid
    userid = int(event_var['userid'])
    
    # Is the player invincible?
    if playerCounters.has_key(userid):
        finishCountdown(userid, False)

def weapon_fire(event_var):
    # Get userid
    userid = int(event_var['userid'])
    
    # Is the player invincible?
    if playerCounters.has_key(userid):
        finishCountdown(userid)

def combatCountdown(userid, repeatInfo):
    # Set health
    player = playerlib.getPlayer(userid)
    player.set('health', 999)
    
    # Is plural
    if playerCounters[userid] > 1:
        gungamelib.centermsg('gg_spawn_protect', userid, 'CombatCountdown_Plural', {'time': playerCounters[userid]})
    
    # Is singular
    elif playerCounters[userid] == 1:
        gungamelib.centermsg('gg_spawn_protect', userid, 'CombatCountdown_Singular')
    
    # Set the players health back and return
    if playerCounters[userid] == 0:
        # Finish the countdown
        finishCountdown(userid)
        return
    
    # Decrement the timer
    playerCounters[userid] -= 1

def finishCountdown(userid, announce=True):
    # Init vars
    userid = int(userid)
    player = playerlib.getPlayer(userid)

    # Set color and health
    player.set('health', 100)
    player.set('color', (255, 255, 255, 255))
    
    # Tell them they are uninvicible
    if announce:
        gungamelib.centermsg('gg_spawn_protect', userid, 'CombatStarted')
    
    # Remove them from the counters
    repeat.delete('CombatCounter%s' % userid)
    del playerCounters[userid]

def startCountdown(userid):
    # Is it warmup round?
    if int(gungamelib.getGlobal('isWarmup')):
        return
    
    # Init vars
    userid = int(userid)
    player = playerlib.getPlayer(userid)
    
    playerCounters[userid] = dict_SpawnProtectVars['delay']

    # Set color and health
    player.set('health', 999)
    player.set('color', (dict_SpawnProtectVars['red'], dict_SpawnProtectVars['green'], dict_SpawnProtectVars['blue'], dict_SpawnProtectVars['alpha']))
    
    # Start counter
    repeat.create('CombatCounter%s' % userid, combatCountdown, (userid))
    repeat.start('CombatCounter%s' % userid, 1, 0)

def setPreventLevelZero(userid):
    gungamePlayer = gungamelib.getPlayer(userid)
    gungamePlayer['preventlevel'] = 0