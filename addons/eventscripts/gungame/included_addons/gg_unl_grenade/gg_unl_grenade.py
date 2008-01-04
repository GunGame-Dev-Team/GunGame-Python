"""
(c)2007 by the GunGame Coding Team

    Title:      gg_unl_grenade
Version #:      11.29.2007
Description:    When a player reaches grenade level, they are given another grenade when their 
                thrown grenade detonates.  This will automatically disable the Earn Hegrenades addon.
"""

import es
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_unl_grenade Addon for GunGame: Python" 
info.version  = "11.29.2007"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_unl_grenade" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007"


def load():
    # Register this addon with GunGame
    global dict_playerWeapons
    gungame.registerAddon('gungame/included_addons/gg_unl_grenade', 'GG Unlimited Grenade')
    
    if gungame.getGunGameVar('gg_xtra_grenades') == '1':
        gungame.setGunGameVar('gg_xtra_grenades', '0')
        
        
def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_unl_grenade')
    
    
def gg_variable_changed(event_var):
    # Watch for required addon load/unload
    if event_var['cvarname'] == 'gg_xtra_grenades' and event_var['newvalue'] == '1':
        gungame.setGunGameVar('gg_xtra_grenades', 0)
        es.msg('#lightgreen', 'WARNING: gg_xtra_grenades cannot be loaded while gg_unl_grenade is enabled!')
        
        
def hegrenade_detonate(event_var):
    userid = event_var['userid']
    gungamePlayer = gungame.getPlayer(userid)
    if event_var['es_userteam'] > 1 and gungamePlayer.get('weapon') == 'hegrenade':
        es.server.cmd('es_give %s weapon_hegrenade' % userid)