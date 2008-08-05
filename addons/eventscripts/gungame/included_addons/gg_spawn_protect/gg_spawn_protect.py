''' (c) 2008 by the GunGame Coding Team

    Title: gg_spawn_protection
    Version: 1.0.440
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
import playerlib

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_spawn_protection (for GunGame:Python)'
info.version  = '1.0.440'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_spawn_protect'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
noisyBefore = 0

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    global noisyBefore
    
    # Register with GunGame
    gg_spawn_protect = gungamelib.registerAddon('gg_spawn_protect')
    gg_spawn_protect.setDisplayName('GG Spawn Protection')
    
    # Set eventscripts_noisy to 1, and back up the original value
    if gungamelib.getVariable('gg_spawn_protect_cancelonfire'):
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
        
        if newValue == 1:
            # Set noisy vars
            noisyBefore = int(es.ServerVar('eventscripts_noisy'))
            es.ServerVar('eventscripts_noisy').set(1)
        else:
            # Set noisy back
            es.ServerVar('eventscripts_noisy').set(noisyBefore)

def weapon_fire(event_var):
    if not gungamelib.getVariable('gg_spawn_protect_cancelonfire'):
        return
        
    userid = int(event_var['userid'])
    
    # Cancel the delay
    gamethread.cancelDelayed('ggSpawnProtect%s' %userid)
    
    # Fire the end of the spawn protection immediately
    endProtect(userid)

def player_spawn(event_var):
    # Is a warmup round?
    if gungamelib.getGlobal('isWarmup') == 1:
        return
    
    # Get userid
    userid = int(event_var['userid'])
    
    # Is player alive?
    if gungamelib.isDead(userid) or gungamelib.isSpectator(userid):
        return
    
    startProtect(userid)

def startProtect(userid):
    # Retrieve player objects
    playerlibPlayer = playerlib.getPlayer(userid)
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Set health
    playerlibPlayer.set('health', 999)
    
    # Set color
    playerlibPlayer.set('color', (gungamelib.getVariable('gg_spawn_protect_red'),
                                  gungamelib.getVariable('gg_spawn_protect_green'),
                                  gungamelib.getVariable('gg_spawn_protect_blue'),
                                  gungamelib.getVariable('gg_spawn_protect_alpha')))
    
    # Remove hitboxes
    es.setplayerprop(userid, 'CBaseAnimating.m_nHitboxSet', 2)
    
    # Set PreventLevel if needed
    if not gungamePlayer.preventlevel and not gungamelib.getVariableValue('gg_spawn_protect_can_level_up'):
        gungamePlayer.preventlevel = 1
        
    # Start the delay to cancel spawn protection
    gamethread.delayedname(gungamelib.getVariableValue('gg_spawn_protect'), 'ggSpawnProtect%s' %userid, endProtect, (userid))
    
def endProtect(userid):
    # Retrieve player objects
    gungamePlayer = gungamelib.getPlayer(userid)
    playerlibPlayer = playerlib.getPlayer(userid)
    
    # Health
    playerlibPlayer.set('health', 100)
    
    # Color
    playerlibPlayer.set('color', (255, 255, 255, 255))
    
    # Hitbox
    es.setplayerprop(userid, 'CBaseAnimating.m_nHitboxSet', 0)
    
    # PreventLevel
    if not gungamelib.getVariableValue('gg_spawn_protect_can_level_up'):
        gungamePlayer.preventlevel = 0