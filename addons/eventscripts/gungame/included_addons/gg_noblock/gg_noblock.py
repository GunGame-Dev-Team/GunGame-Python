'''
(c)2008 by the GunGame Coding Team

    Title:      gg_noblock
Version #:      1.0.102
Description:    No player can block another, they are like ghosts.
'''

import es
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_noblock Addon for GunGame: Python" 
info.version  = "1.0.102"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_noblock" 
info.author   = "GunGame Development Team"

def load():
    # Register this addon with GunGame
    gungame.registerAddon("gg_noblock", "GG NoBlock")

def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon("gg_noblock")

def player_spawn(event_var):
    # Set player's collisiongroup to 2, noblock
    es.setplayerprop(event_var["userid"], "CCSPlayer.baseclass.baseclass.baseclass.baseclass.baseclass.baseclass.m_CollisionGroup", 2)