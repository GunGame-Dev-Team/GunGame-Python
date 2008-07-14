''' (c) 2008 by the GunGame Coding Team

    Title: gg_reload
    Version: 1.0.406
    Description: When a player makes a kill the ammo in their clip is
                 replenished.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es

# GunGame imports
import gungamelib
import ggweaponlib
reload(ggweaponlib)

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_reload Addon for GunGame: Python'
info.version  = '1.0.406'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_reload'
info.author   = 'GunGame Development Team'

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
    weapon = event_var['weapon']
    
    # We will only reload weapons that the attacker is on the level for
    if weapon != gungamelib.getPlayer(attacker).getWeapon():
        return
    
    weaponInfo = ggweaponlib.getWeaponInfo(weapon)
    if weaponInfo.slot in (1, 2):
        es.setplayerprop(userid, weaponInfo.prop, weaponInfo.ammo)