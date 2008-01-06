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
info.version  = "12.31.2007"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_spawn_protect" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007"

gg_spawn_protect = int(gungame.getGunGameVar('gg_spawn_protect'))

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_spawn_protect', 'GG Spawn Protection')

def unload():
    #Unregister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_spawn_protect')

def gg_variable_changed(event_var):
    # register change in gg_map_list_file
    if event_var['cvarname'] == 'gg_spawn_protect':
        global gg_spawn_protect
        gg_spawn_protect = int(gungame.getGunGameVar('gg_spawn_protect'))

def player_spawn(event_var):
    global gg_spawn_protect
    if not gungame.getRegisteredAddons().has_key('gungame\\included_addons\\gg_warmup_round'):
        userid = int(event_var['userid'])
        gungamePlayer = gungame.getPlayer(userid)
        playerlibPlayer = playerlib.getPlayer(userid)
        gungamePlayer.set('preventlevel', 1)
        playerlibPlayer.set('health', 9999)
        playerlibPlayer.set('color', (255, 0, 0))
        gamethread.delayed(gg_spawn_protect, gungamePlayer.set, ('preventlevel', 0))
        gamethread.delayed(gg_spawn_protect, playerlibPlayer.set, ('health', 100))
        gamethread.delayed(gg_spawn_protect, playerlibPlayer.set, ('color', (255, 255, 255)))
