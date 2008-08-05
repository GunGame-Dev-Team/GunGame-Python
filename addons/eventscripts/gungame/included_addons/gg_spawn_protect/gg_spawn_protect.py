''' (c) 2008 by the GunGame Coding Team

    Title: gg_spawn_protection
    Version: 1.0.439
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
info.version  = '1.0.439'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_spawn_protect'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
playerColor = None
noisyBefore = 0

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    global noisyBefore
    global playerColor
    
    # Register with GunGame
    gg_spawn_protect = gungamelib.registerAddon('gg_spawn_protect')
    gg_spawn_protect.setDisplayName('GG Spawn Protection')
    
    #
    if gungamelib.getVariable('gg_spawn_protect_cancelonfire'):
        noisyBefore = int(es.ServerVar('eventscripts_noisy'))
        es.ServerVar('eventscripts_noisy').set(1)
        
    # Retrieve player color settings
    playerColor = (gungamelib.getVariable('gg_spawn_protect_red'),
                   gungamelib.getVariable('gg_spawn_protect_green'),
                   gungamelib.getVariable('gg_spawn_protect_blue'),
                   gungamelib.getVariable('gg_spawn_protect_alpha'))
    
def unload():
    # Set noisy back
    es.ServerVar('eventscripts_noisy').set(noisyBefore)
    
    # Unregister
    gungamelib.unregisterAddon('gg_spawn_protect')

def server_cvar(event_var):
    global noisyBefore
    global playerColor
    
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
            
    elif cvarname in ['gg_spawn_protect_red', 'gg_spawn_protect_green',
                      'gg_spawn_protect_blue', 'gg_spawn_protect_alpha']:
                      
        # Set the color tuple
        playerColor = (gungamelib.getVariable('gg_spawn_protect_red'),
                       gungamelib.getVariable('gg_spawn_protect_green'),
                       gungamelib.getVariable('gg_spawn_protect_blue'),
                       gungamelib.getVariable('gg_spawn_protect_alpha'))

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
    red, green, blue, alpha = playerColor
    playerlibPlayer.set('color', (red, green, blue, alpha))
    
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
    gungamePlayer.preventlevel = 0