'''
(c)2007 by the GunGame Coding Team

    Title:      gg_spawn_protection
Version #:      12.31.2007
Description:    This will make players invincable and marked with color when
                ever a player spawns.  Protected players cannot level up during
                spawn protection.
'''

import es
import playerlib
import gamethread
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_spawn_protection Addon for GunGame: Python" 
info.version  = "08.01.2007"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_spawn_protect"
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007"

# Addon settings
dict_SpawnProtectVars = {}
dict_SpawnProtectVars['red'] = int(gungame.getGunGameVar('gg_spawn_protect_red'))
dict_SpawnProtectVars['green'] = int(gungame.getGunGameVar('gg_spawn_protect_green'))
dict_SpawnProtectVars['blue'] = int(gungame.getGunGameVar('gg_spawn_protect_blue'))
dict_SpawnProtectVars['alpha'] = int(gungame.getGunGameVar('gg_spawn_protect_alpha'))
dict_SpawnProtectVars['delay'] = int(gungame.getGunGameVar('gg_spawn_protect'))

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_spawn_protect', 'GG Spawn Protection')

def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_spawn_protect')

def gg_variable_changed(event_var):
    global dict_SpawnProtectVars
    
    # Register change in gg_map_list_file
    if event_var['cvarname'] == 'gg_spawn_protect':
        dict_SpawnProtectVars['delay'] = int(gungame.getGunGameVar('gg_spawn_protect'))
    # watch for changes in map vote variables
    elif dict_SpawnProtectVars.has_key(event_var['cvarname']):
        dict_SpawnProtectVars[event_var['cvarname']] = int(event_var['newvalue'])

def player_spawn(event_var):
    # If not warmup round...
    if not gungame.getRegisteredAddons().has_key('gungame\\included_addons\\gg_warmup_round'):
        # Get userid and player objects
        userid = int(event_var['userid'])
        gungamePlayer = gungame.getPlayer(userid)
        playerlibPlayer = playerlib.getPlayer(userid)
        
        # Set protected settings
        playerlibPlayer.set('health', 999)
        playerlibPlayer.set('color', (dict_SpawnProtectVars['red'], dict_SpawnProtectVars['green'], dict_SpawnProtectVars['blue'], dict_SpawnProtectVars['alpha']))
        
        # Set un-protected settings
        gamethread.delayed(dict_SpawnProtectVars['delay'], playerlibPlayer.set, ('health', 100))
        gamethread.delayed(dict_SpawnProtectVars['delay'], playerlibPlayer.set, ('color', (255, 255, 255, 255)))
        
        # See if prevent level is already turned on
        if not gungamePlayer.get('preventlevel'):
            gungamePlayer.set('preventlevel', 1)
            gamethread.delayed(dict_SpawnProtectVars['delay'], gungamePlayer.set, ('preventlevel', 0))
