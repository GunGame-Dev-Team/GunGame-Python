'''
(c) 2008 by the GunGame Coding Team

    Title:      gg_reload
Version #:      1.0.102
Description:    When a player makes a kill the ammo in their clip is replenished.
'''

import es
from gungame import gungame
import playerlib

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_reload Addon for GunGame: Python" 
info.version  = "1.0.102"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/reload" 
info.author   = "GunGame Development Team"

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gg_reload', 'GG Reload')

def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gg_reload')

def player_death(event_var):
    # Get vars
    weapon = event_var['weapon']
    playerlibPlayer = playerlib.getPlayer(event_var['attacker'])
    
    # Check what weapon the attacker has
    if weapon == 'm3' or weapon == 'xm1014':
        playerlibPlayer.set('clip', ['weapon_m3', 8])
    elif weapon == 'xm1014':
        playerlibPlayer.set('clip', ['weapon_xm1014', 8])
    elif weapon == 'm249':
        playerlibPlayer.set('clip', ['weapon_m249', 255])
    else:
        playerlibPlayer.set('clip', ['weapon_' + weapon, 30])