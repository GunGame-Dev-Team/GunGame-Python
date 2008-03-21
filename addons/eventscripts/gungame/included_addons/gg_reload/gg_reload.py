'''
(c) 2008 by the GunGame Coding Team

    Title:      gg_reload
Version #:      1.0.157
Description:    When a player makes a kill the ammo in their clip is replenished.
'''

# EventScripts imports
import es
import playerlib

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_reload Addon for GunGame: Python"
info.version  = "1.0.157"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/reload"
info.author   = "GunGame Development Team"

def load():
    # Register addon with gungamelib
    gg_reload = gungamelib.registerAddon('gg_reload')
    gg_reload.setMenuText('GG Reload')

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_reload')

def player_death(event_var):
    if event_var['attacker'] != '0' and event_var['attacker'] != event_var['userid']:
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