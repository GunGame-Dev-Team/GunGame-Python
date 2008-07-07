''' (c) 2008 by the GunGame Coding Team

    Title: gg_reload
    Version: 1.0.389
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

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_reload Addon for GunGame: Python'
info.version  = '1.0.389'
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
            'weapon_m249': 100}
            
primaryWeapons = ['weapon_awp', 'weapon_scout', 'weapon_aug', 'weapon_mac10', 'weapon_tmp', 'weapon_mp5navy',
                  'weapon_ump45', 'weapon_p90', 'weapon_galil', 'weapon_famas', 'weapon_ak47', 'weapon_sg552',
                  'weapon_sg550', 'weapon_g3sg1', 'weapon_m249', 'weapon_m3', 'weapon_xm1014', 'weapon_m4a1']
                  
secondaryWeapons = ['weapon_glock', 'weapon_usp', 'weapon_p228', 'weapon_deagle', 'weapon_elite', 'weapon_fiveseven']

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
    weapon = es.createplayerlist(userid)[userid]['weapon']
    
    # We will only reload weapons that the attacker is on the level for
    if weapon != str('weapon_%s' %gungamelib.getPlayer(attacker).getWeapon()):
        return
    
    # Is a hegrenade or knife kill?
    if weapon in ('weapon_hegrenade', 'weapon_knife'):
        return
    
    # Reload the weapon
    if weapon in primaryWeapons:
        es.getplayerprop(userid, 'CCSPlayer.baseclass.localdata.m_iAmmo.001', clipSize[weapon])
    elif weapon in secondaryWeapons:
        es.getplayerprop(userid, 'CCSPlayer.baseclass.localdata.m_iAmmo.002', clipSize[weapon])