"""
(c)2007 by the GunGame Coding Team

    Title:      gg_nade_bonus
Version #:      11.27.2007
Description:    When players are on grenade level, by default, they are just given
                an hegrenade. This addon will give them an additional weapon of the
                admin's choice.
"""

import es
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_nade_bonus Addon for GunGame: Python" 
info.version  = "11.27.2007"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_nade_bonus" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007"

global bonusWeapon
bonusWeapon = gungame.getGunGameVar('gg_nade_bonus')
if 'weapon_' not in gungame.getGunGameVar('gg_nade_bonus'):
    bonusWeapon = 'weapon_' + str(bonusWeapon)

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_nade_bonus', 'GG Nade Bonus')

def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_nade_bonus')

def gg_variable_changed(event_var):
    if event_var['cvarname'] == 'gg_nade_bonus' and event_var['newvalue'] == '0':
        es.unload('gungame/included_addons/gg_nade_bonus')

def player_spawn(event_var):
    userid = int(event_var['userid'])
    gungamePlayer = gungame.getPlayer(userid)
    if gungamePlayer.get('weapon') == 'hegrenade':
        es.server.cmd('es_xdelayed 0.1 es_xgive %d %s' %(userid, bonusWeapon))
        es.server.cmd('es_xdelayed 0.2 es_xsexec %d use weapon_hegrenade' %userid)

def gg_levelup(event_var):
    userid = int(event_var['userid'])
    gungamePlayer = gungame.getPlayer(userid)
    if gungamePlayer.get('weapon') == 'hegrenade':
        es.server.cmd('es_xdelayed 0.1 es_xgive %d %s' %(userid, bonusWeapon))
        es.server.cmd('es_xdelayed 0.2 es_xsexec %d use weapon_hegrenade' %userid)