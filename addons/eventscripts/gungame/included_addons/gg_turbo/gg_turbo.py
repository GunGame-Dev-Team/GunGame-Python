'''
(c)2007 by the GunGame Coding Team

    Title:      gg_turbo
Version #:      1.0.119
Description:    GunGame Turbo is allows players to recieve the weapon for their new
                level immediately, instead of having to wait for the following round.
                This addon makes the GunGame round a little more fast-paced.
'''

# EventScripts imports
import es

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_turbo Addon for GunGame: Python"
info.version  = "1.0.119"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_turbo"
info.author   = "GunGame Development Team"

def load():
    # Register this addon with GunGame
    gg_turbo = gungamelib.registerAddon('gg_turbo')
    gg_turbo.setMenuText('GG Turbo')

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_turbo')

def gg_levelup(event_var):
    userid = int(event_var['userid'])
    gungamePlayer = gungamelib.getPlayer(userid)
    if gungamePlayer.getWeapon() == 'knife':
        es.sexec(userid, 'use weapon_knife')
    gungamePlayer.stripPlayer()
    gungamePlayer.giveWeapon()