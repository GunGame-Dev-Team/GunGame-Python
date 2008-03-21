'''
(c)2007 by the GunGame Coding Team

    Title:      gg_spawn_protection
Version #:      1.0.163
Description:    This will make players invincible and marked with color when
                ever a player spawns.  Protected players cannot level up during
                spawn protection.
'''

# EventScripts imports
import es
import gamethread
import repeat
import playerlib
from playerlib import UseridError

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_spawn_protection"
info.version  = "1.0.163"
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
dict_SpawnProtectVars['cancelOnFire'] = gungamelib.getVariableValue('gg_spawn_protect_cancelonfire')

playerCounters = {}
noisyBefore = 0

def load():
    # Register
    gg_spawn_protect = gungamelib.registerAddon('gg_spawn_protect')
    gg_spawn_protect.setMenuText('GG Spawn Protection')
    
    if dict_SpawnProtectVars['cancelOnFire']:
        noisyBefore = int(es.ServerVar('eventscripts_noisy'))
        es.ServerVar('eventscripts_noisy').set(1)
    
def unload():
    # Set noisy back
    es.ServerVar('eventscripts_noisy').set(noisyBefore)
    
    # Unregister
    gungamelib.unregisterAddon('gg_spawn_protect')
    
def server_cvar(event_var):
    # Register change in gg_map_list_file
    if event_var['cvarname'] == 'gg_spawn_protect':
        dict_SpawnProtectVars['delay'] = gungamelib.getVariableValue('gg_spawn_protect')

def weapon_fire(event_var):
    if not dict_SpawnProtectVars['cancelOnFire']:
        return
    
    # Finish countdown for player if they are protected
    if repeat.status('CombatCounter%s' % userid):
        finishCountdown(int(event_var['userid']))

def player_spawn(event_var):
    # Is a warmup round?
    if gungamelib.getGlobal('isWarmup') == 1:
        return
    
    # Get userid and player object
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Is player alive?
    if gungamelib.isDead(userid) or gungamelib.isSpectator(userid):
        return
    
    # Start countdown
    startCountdown(userid)
    
    # See if prevent level is already turned on
    if not gungamePlayer['preventlevel']:
        gungamePlayer['preventlevel'] = 1

def player_disconnect(event_var):
    # Get userid
    userid = int(event_var['userid'])
    
    # Is the player invincible?
    if repeat.status('CombatCounter%s' % userid):
        repeat.delete('CombatCounter%s' % userid)
    
    # Remove from counters
    if playerCounters.has_key(userid):
        del playerCounters[userid]

def player_death(event_var):
    # Get userid
    userid = int(event_var['userid'])
    
    # Is the player invincible?
    if repeat.status('CombatCounter%s' % userid):
        repeat.delete('CombatCounter%s' % userid)

def combatCountdown(userid, repeatInfo):
    # Get player
    try:
        player = playerlib.getPlayer(userid)
    except UseridError:
        repeat.delete('CombatCounter%s' % userid)
    
    # Keep them invincible
    player.set('health', 999)
    
    # Is plural
    if playerCounters[userid] > 1:
        gungamelib.centermsg('gg_spawn_protect', userid, 'CombatCountdown_Plural', {'time': playerCounters[userid]})
    
    # Is singular
    elif playerCounters[userid] == 1:
        gungamelib.centermsg('gg_spawn_protect', userid, 'CombatCountdown_Singular')
    
    # Set the players health back and return
    if playerCounters[userid] <= 0:
        # Finish the countdown
        finishCountdown(userid)
        return
    
    # Decrement the timer
    playerCounters[userid] -= 1

def finishCountdown(userid):
    # Init vars
    userid = int(userid)
    player = playerlib.getPlayer(userid)
    gungamePlayer = gungamelib.getPlayer(userid)

    # Remove them from the counters
    repeat.delete('CombatCounter%s' % userid)
    del playerCounters[userid]

    # Set color and health and preventLevel
    player.set('health', 100)
    player.set('color', (255, 255, 255, 255))
    gungamePlayer['preventlevel'] = 0
    
    # Tell them they are uninvicible
    gungamelib.centermsg('gg_spawn_protect', userid, 'CombatStarted')

def startCountdown(userid):
    # Is it warmup round?
    if int(gungamelib.getGlobal('isWarmup')):
        return
    
    # Init vars
    userid = int(userid)
    player = playerlib.getPlayer(userid)
    delay = dict_SpawnProtectVars['delay']
    
    # Set player counter
    playerCounters[userid] = delay

    # Set color and health
    player.set('health', 999)
    player.set('color', (dict_SpawnProtectVars['red'], dict_SpawnProtectVars['green'], dict_SpawnProtectVars['blue'], dict_SpawnProtectVars['alpha']))
    
    # Start counter
    repeat.create('CombatCounter%s' % userid, combatCountdown, (userid))
    repeat.start('CombatCounter%s' % userid, 1, delay + 2)