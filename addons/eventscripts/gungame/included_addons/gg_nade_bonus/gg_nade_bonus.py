'''
(c)2007 by the GunGame Coding Team

    Title:      gg_nade_bonus
Version #:      1.0.102
Description:    When players are on grenade level, by default, they are just given
                an hegrenade. This addon will give them an additional weapon of the
                admin's choice.
'''

import es
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_nade_bonus Addon for GunGame: Python" 
info.version  = "1.0.102"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_nade_bonus" 
info.author   = "GunGame Development Team"

global bonusWeapon
bonusWeapon = gungame.getGunGameVar('gg_nade_bonus')
if 'weapon_' not in gungame.getGunGameVar('gg_nade_bonus'):
    bonusWeapon = 'weapon_' + str(bonusWeapon)

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gg_nade_bonus', 'GG Nade Bonus')

def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gg_nade_bonus')

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