'''
(c)2007 by the GunGame Coding Team

    Title:      gg_dead_strip
Version #:      02.19.08
Description:    When a player dies all his weapons are imidiately removed from the game.
'''

import es
import playerlib
import gungamelib
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_dead_strip Addon for GunGame: Python" 
info.version  = "02.19.08"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_dead_strip" 
info.author   = "GunGame Development Team"

list_allWeapons = ['glock', 'usp', 'p228', 'deagle', 'elite', 'fiveseven', 'awp', 'scout', 'aug', 'mac10', 'tmp', 'mp5navy', 'ump45', 'p90', 'galil', 'famas', 'ak47', 'sg552', 'sg550', 'g3sg1', 'm249', 'm3', 'xm1014', 'm4a1', 'hegrenade', 'flashbang', 'smokegrenade']

def load():
    # Register this addon with GunGame
    global dict_playerWeapons
    gungame.registerAddon('gg_dead_strip', 'GG Dead Strip')
    es.addons.registerClientCommandFilter(filterDrop)

def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gg_dead_strip')
    es.addons.unregisterClientCommandFilter(filterDrop)

def item_pickup(event_var):
    global list_allWeapons
    item = event_var['item']
    if item in list_allWeapons:
        userid = event_var['userid']
        gungamePlayer = gungamelib.getPlayer(userid)
        playerWeapon = gungamePlayer.getWeapon()
        #playerWeapon = gungamePlayer.get('weapon')
        playerlibPlayer = playerlib.getPlayer(userid)
        if gungame.getRegisteredAddons().has_key('gg_warmup_round'):
            if item != gungame.getGunGameVar('gg_warmup_weapon') and gungame.getGunGameVar('gg_warmup_weapon') != '0':
                es.server.cmd('es_remove %i' % playerlibPlayer.get('weaponindex', item))
        else:
            if playerWeapon != item and playerWeapon != 'hegrenade' or playerWeapon == 'hegrenade' and gungame.getGunGameVar('gg_nade_bonus') != item and item != 'hegrenade':
                es.server.cmd('es_remove %i' % playerlibPlayer.get('weaponindex', item))


def filterDrop(userid, args):
    if args[0] == 'drop':
        gungamePlayer = gungamelib.getPlayer(userid)
        playerlibPlayer = playerlib.getPlayer(userid)
        if playerlibPlayer.attributes['weapon'] == 'weapon_%s' %gungamePlayer.getWeapon():
            return 0
    return 1

def player_death(event_var):
    # remove dropped weapon from the map
    dict_entityList = es.createentitylist()
    list_idleWeapons = filter(lambda x: dict_entityList[x]['classname'].startswith('weapon_') and es.getindexprop(x, 'CBaseEntity.m_hOwnerEntity') == -1 and dict_entityList[x]['classname'] != 'weapon_c4', dict_entityList)
    for idleWeapon in list_idleWeapons:
        es.server.cmd('es_xremove %d' %idleWeapon)