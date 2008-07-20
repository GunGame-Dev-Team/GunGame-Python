''' (c) 2008 by the GunGame Coding Team

    Title: gg_reload
    Version: 1.0.415
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
import ggweaponlib
reload(ggweaponlib)

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_reload Addon for GunGame: Python'
info.version  = '1.0.415'
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
    
    # Is a hegrenade or knife kill?
    if weapon in ('hegrenade', 'knife'):
        return
    
    # Set clip
    playerHandle = es.getplayerhandle(attacker)
    weaponInfo = ggweaponlib.getWeaponInfo(weapon)
    for weaponIndex in es.createentitylist('weapon_' + weapon):
        if playerHandle == es.getindexprop(weaponIndex, 'CBaseEntity.m_hOwnerEntity'):
            es.setindexprop(weaponIndex, 'CBaseCombatWeapon.LocalWeaponData.m_iClip1', weaponInfo.ammo)
            break
