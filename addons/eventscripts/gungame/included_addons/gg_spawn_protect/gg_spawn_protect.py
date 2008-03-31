''' (c) 2008 by the GunGame Coding Team

    Title: gg_spawn_protection
    Version: 1.0.226
    Description: This will make players invincible and marked with color when
                 ever a player spawns. Protected players cannot level up during
                 spawn protection.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import gamethread
import repeat
import usermsg
import playerlib
from playerlib import UseridError

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_spawn_protection (for GunGame:Python)'
info.version  = '1.0.226'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_spawn_protect'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
# Addon settings
dict_variables = {}
dict_variables['red'] = gungamelib.getVariable('gg_spawn_protect_red')
dict_variables['green'] = gungamelib.getVariable('gg_spawn_protect_green')
dict_variables['blue'] = gungamelib.getVariable('gg_spawn_protect_blue')
dict_variables['alpha'] = gungamelib.getVariable('gg_spawn_protect_alpha')
dict_variables['delay'] = gungamelib.getVariable('gg_spawn_protect')
dict_variables['cancelOnFire'] = gungamelib.getVariable('gg_spawn_protect_cancelonfire')

playerCounters = {}
noisyBefore = 0

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register
    gg_spawn_protect = gungamelib.registerAddon('gg_spawn_protect')
    gg_spawn_protect.setDisplayName('GG Spawn Protection')
    
    if int(dict_variables['cancelOnFire']):
        noisyBefore = int(es.ServerVar('eventscripts_noisy'))
        es.ServerVar('eventscripts_noisy').set(1)
    
def unload():
    # Set noisy back
    es.ServerVar('eventscripts_noisy').set(noisyBefore)
    
    # Unregister
    gungamelib.unregisterAddon('gg_spawn_protect')


def server_cvar(event_var):
    global noisyBefore
    
    cvarname = event_var['cvarname']
    
    if cvarname == 'gg_spawn_protect_cancelonfire':
        newValue = int(event_var['cvarvalue'])
        dict_variables['cancelOnFire'] = newValue
        
        if newValue == 1:
            # Set noisy vars
            noisyBefore = int(es.ServerVar('eventscripts_noisy'))
            es.ServerVar('eventscripts_noisy').set(1)
        else:
            # Set noisy back
            es.ServerVar('eventscripts_noisy').set(noisyBefore)

def weapon_fire(event_var):
    if not int(dict_variables['cancelOnFire']):
        return
    
    # Finish countdown for player if they are protected
    if repeat.status('CombatCounter%s' % event_var['userid']):
        finishCountdown(int(event_var['userid']))

def player_spawn(event_var):
    # Is a warmup round?
    if gungamelib.getGlobal('isWarmup') == 1:
        return
    
    # Get userid
    userid = int(event_var['userid'])
    
    # Is player alive?
    if gungamelib.isDead(userid) or gungamelib.isSpectator(userid):
        return
    
    # Start countdown
    startCountdown(userid)

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

# ==============================================================================
#  COUNTDOWN CODE
# ==============================================================================
def combatCountdown(userid, repeatInfo):
    # Get player
    try:
        player = playerlib.getPlayer(userid)
    except UseridError:
        repeat.delete('CombatCounter%s' % userid)
        return
    
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
        
    # Set the view tint
    # fade <userid> <0 = no fade, 1 = fade Out 2 = fade in> <time to fade (in frames)> <time faded (in frames)> <red> <green> <blue> <alpha>
    # usermsg.fade(userid,0,1,1000,0,255,0,30)
    
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
    
    # Set back the view tint
    # fade <userid> <0 = no fade, 1 = fade Out 2 = fade in> <time to fade (in frames)> <time faded (in frames)> <red> <green> <blue> <alpha>
    # usermsg.fade(userid,0,1,10,0,0,0,30)
    # usermsg.fade(userid,0,1,20,0,0,0,0)
    
    # Tell them they are uninvicible
    gungamelib.centermsg('gg_spawn_protect', userid, 'CombatStarted')

def startCountdown(userid):
    # Is it warmup round?
    if int(gungamelib.getGlobal('isWarmup')):
        return
    
    # Init vars
    userid = int(userid)
    player = playerlib.getPlayer(userid)
    delay = int(dict_variables['delay'])
    
    # Set player counter
    playerCounters[userid] = delay

    # Set color and health
    player.set('health', 999)
    player.set('color', (int(dict_variables['red']), int(dict_variables['green']), int(dict_variables['blue']), int(dict_variables['alpha'])))
    
    # See if prevent level is already turned on
    gungamePlayer = gungamelib.getPlayer(userid)
    if not gungamePlayer['preventlevel']:
        gungamePlayer['preventlevel'] = 1
    
    # Start counter
    repeat.create('CombatCounter%s' % userid, combatCountdown, (userid))
    repeat.start('CombatCounter%s' % userid, 1, delay + 2)