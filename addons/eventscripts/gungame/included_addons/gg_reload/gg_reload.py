''' (c) 2008 by the GunGame Coding Team

    Title: gg_reload
    Version: 1.0.331
    Description: When a player makes a kill the ammo in their clip is replenished.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import playerlib

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_reload Addon for GunGame: Python'
info.version  = '1.0.331'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/reload'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
clipSize        = {'usp': 12, 
                   'glock': 20,
                   'deagle': 7,
                   'p228': 13,
                   'elite': 30,
                   'fiveseven': 20,
                   'm3': 8,
                   'xm1014': 7,
                   'mp5navy': 30,
                   'tmp': 30,
                   'p90': 50,
                   'mac10': 30,
                   'ump45': 25,
                   'galil': 35,
                   'famas': 25,
                   'ak47': 30,
                   'sg552': 30,
                   'm4a1': 30,
                   'aug': 30,
                   'scout': 10,
                   'awp': 10,
                   'g3sg1': 20,
                   'sg550': 30,
                   'm249': 100}

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_reload = gungamelib.registerAddon('gg_reload')
    gg_reload.setDisplayName('GG Reload')

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_reload')


def player_death(event_var):
    if event_var['attacker'] != '0' and event_var['attacker'] != event_var['userid']:
        # Get vars
        weapon = event_var['weapon']
        if weapon != 'hegrenade' and weapon != 'knife':
            playerlibPlayer = playerlib.getPlayer(event_var['attacker'])
            
            # Set the clip size based on the player's weapon
            playerlibPlayer.set('clip', [weapon, clipSize[weapon]])