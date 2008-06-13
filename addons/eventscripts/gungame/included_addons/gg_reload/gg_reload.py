''' (c) 2008 by the GunGame Coding Team

    Title: gg_reload
    Version: 1.0.348
    Description: When a player makes a kill the ammo in their clip is
                 replenished.
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
info.version  = '1.0.348'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_reload'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
clipSize = {'weapon_usp': 12, 
            'weapon_glock': 20,
            'weapon_deagle': 7,
            'weapon_p228': 13,
            'weapon_elite': 30,
            'weapon_fiveseven': 20,
            'weapon_m3': 8,
            'weapon_xm1014': 7,
            'weapon_mp5navy': 30,
            'weapon_tmp': 30,
            'weapon_p90': 50,
            'weapon_mac10': 30,
            'weapon_ump45': 25,
            'weapon_galil': 35,
            'weapon_famas': 25,
            'weapon_ak47': 30,
            'weapon_sg552': 30,
            'weapon_m4a1': 30,
            'weapon_aug': 30,
            'weapon_scout': 10,
            'weapon_awp': 10,
            'weapon_g3sg1': 20,
            'weapon_sg550': 30,
            'weapon_m249': 100
            }

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
    # Get event info
    attacker = int(event_var['attacker'])
    userid = int(event_var['userid'])
    
    # Fallen to death?
    if not attacker:
        return
    
    # Killed self?
    if attacker == userid:
        return
    
    # Get weapon
    weapon = 'weapon_%s' %event_var['weapon']
    
    # Not a weapon
    if weapon[:6] != 'weapon':
        return
    
    # Is a hegrenade or knife kill?
    if weapon in ('weapon_hegrenade', 'weapon_knife'):
        return
    
    # Set clip
    player = playerlib.getPlayer(attacker)
    player.set('clip', [weapon, clipSize[weapon]])