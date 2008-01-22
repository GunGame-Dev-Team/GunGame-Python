"""
(c)2007 by the GunGame Coding Team

    Title:      gg_unl_grenade
Version #:      1.0.30
Description:    When a player reaches grenade level, they are given another grenade when their 
                thrown grenade detonates.  This will automatically disable the Earn Hegrenades addon.
"""

import es
import playerlib
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_unl_grenade Addon for GunGame: Python" 
info.version  = "1.0.30"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_unl_grenade" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007"


def load():
    # Register this addon with GunGame
    global dict_playerWeapons
    gungame.registerAddon('gg_unl_grenade', 'GG Unlimited Grenade')
    
    if gungame.getGunGameVar('gg_earn_nade') == '1':
        gungame.setGunGameVar('gg_earn_nade', '0')
        
        
def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gg_unl_grenade')
    
    
def gg_variable_changed(event_var):
    # Watch for required addon load/unload
    if event_var['cvarname'] == 'gg_earn_nade' and event_var['newvalue'] == '1':
        gungame.setGunGameVar('gg_earn_nade', 0)
        es.msg('#lightgreen', 'WARNING: gg_xtra_grenades cannot be loaded while gg_unl_grenade is enabled!')
        
        
def hegrenade_detonate(event_var):
    userid = event_var['userid']
    gungamePlayer = gungame.getPlayer(userid)
    playerlibPlayer = playerlib.getPlayer(userid)
    
    if event_var['es_userteam'] > 1 and gungamePlayer.get('weapon') == 'hegrenade' and not int(playerlibPlayer.get('isdead')):
        es.server.cmd('es_give %s weapon_hegrenade' % userid)