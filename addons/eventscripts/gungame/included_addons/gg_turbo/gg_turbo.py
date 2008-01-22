'''
(c)2007 by the GunGame Coding Team

    Title:      gg_turbo
Version #:      12.21.2007
Description:    GunGame Turbo is allows players to recieve the weapon for their new
                level immediately, instead of having to wait for the following round.
                This addon makes the GunGame round a little more fast-paced.
'''

import es
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_turbo Addon for GunGame: Python" 
info.version  = "12.12.2007"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_turbo" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007"

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gg_turbo', 'GG Turbo')

def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gg_turbo')

def gg_levelup(event_var):
    userid = int(event_var['userid'])
    gungamePlayer = gungame.getPlayer(userid)
    if gungamePlayer.get('weapon') == 'knife':
        es.sexec(userid, 'use weapon_knife')
    gungame.stripPlayer(userid)
    gungame.giveWeapon(userid)