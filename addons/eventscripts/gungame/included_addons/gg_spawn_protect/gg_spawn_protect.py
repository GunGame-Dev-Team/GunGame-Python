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

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_spawn_protection Addon for GunGame: Python"
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

def load():
    # Register addon with gungamelib
    gg_spawn_protect = gungamelib.registerAddon('gg_spawn_protect')
    gg_spawn_protect.setMenuText('GG Spawn Protection')

def unload():
    # Unregister this addon with bunbamelib
    gungamelib.unregisterAddon('gg_spawn_protect')

def server_cvar(event_var):
    # Register change in gg_map_list_file
    if event_var['cvarname'] == 'gg_spawn_protect':
        dict_SpawnProtectVars['delay'] = gungamelib.getVariableValue('gg_spawn_protect')
    # watch for changes in map vote variables
    elif dict_SpawnProtectVars.has_key(event_var['cvarname']):
        dict_SpawnProtectVars[event_var['cvarname']] = int(event_var['cvarvalue'])

def player_spawn(event_var):
    # If not warmup round...
    if gungamelib.getGlobal('isWarmup') != '1':
        # Get userid and player objects
        userid = int(event_var['userid'])
        gungamePlayer = gungamelib.getPlayer(userid)
        playerlibPlayer = playerlib.getPlayer(userid)
        
        # Set protected settings
        playerlibPlayer.set('health', 999)
        playerlibPlayer.set('color', (dict_SpawnProtectVars['red'], dict_SpawnProtectVars['green'], dict_SpawnProtectVars['blue'], dict_SpawnProtectVars['alpha']))
        
        # Set un-protected settings
        gamethread.delayed(dict_SpawnProtectVars['delay'], playerlibPlayer.set, ('health', 100))
        gamethread.delayed(dict_SpawnProtectVars['delay'], playerlibPlayer.set, ('color', (255, 255, 255, 255)))
        
        # See if prevent level is already turned on
        if not gungamePlayer['preventlevel']:
            gungamePlayer['preventlevel'] = 1
            gamethread.delayed(dict_SpawnProtectVars['delay'], setPreventLevelZero, (userid))
            
def setPreventLevelZero(userid):
    gungamePlayer = gungamelib.getPlayer(userid)
    gungamePlayer['preventlevel'] = 0