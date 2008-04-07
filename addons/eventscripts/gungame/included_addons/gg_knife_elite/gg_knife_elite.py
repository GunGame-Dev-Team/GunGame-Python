''' (c) 2008 by the GunGame Coding Team

    Title: gg_knife_elite
    Version: 1.0.258
    Description: After a player levels up, they only get a knife until the next
                 round.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import playerlib
import gamethread

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_knife_elite (for GunGame: Python)'
info.version  = '1.0.258'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_knife_elite'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
list_allWeapons = ['glock', 'usp', 'p228', 'deagle', 'elite',
                   'fiveseven', 'awp', 'scout', 'aug', 'mac10',
                   'tmp', 'mp5navy', 'ump45', 'p90', 'galil',
                   'famas', 'ak47', 'sg552', 'sg550', 'g3sg1',
                   'm249', 'm3', 'xm1014', 'm4a1', 'hegrenade',
                   'flashbang', 'smokegrenade']

dict_playerIsElite = {}

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_knife_elite = gungamelib.registerAddon('gg_knife_elite')
    gg_knife_elite.setDisplayName('GG Knife Elite')
    gg_knife_elite.addDependency('gg_dead_strip', 1)
    gg_knife_elite.addDependency('gg_turbo', 0)
    
    for userid in es.getUseridList():
        userid = str(userid)
        dict_playerIsElite[userid] = 0

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_knife_elite')


def player_spawn(event_var):
    userid = event_var['userid']
    dict_playerIsElite[userid] = 0
    gungamePlayer = gungamelib.getPlayer(userid)
    es.sexec(userid, 'use weapon_%s' % gungamePlayer.getWeapon())

def item_pickup(event_var):
    userid = event_var['userid']
    if dict_playerIsElite[userid]:
        item = event_var['item']
        if item in list_allWeapons:
            playerlibPlayer = playerlib.getPlayer(userid)
            es.server.cmd('es_remove %i' % playerlibPlayer.get('weaponindex', item))

def gg_levelup(event_var):
    userid = event_var['userid']
    gungamePlayer = gungamelib.getPlayer(userid)
    if gungamePlayer['preventlevel'] == 0 and gungamePlayer.getWeapon() != 'knife':
        es.sexec(userid, 'use weapon_knife')
        gungamePlayer.stripPlayer()
        dict_playerIsElite[userid] = 1