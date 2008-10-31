''' (c) 2008 by the GunGame Coding Team

    Title: gg_knife_elite
    Version: 1.0.442
    Description: After a player levels up, they only get a knife until the next
                 round.
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
info.name     = 'gg_knife_elite (for GunGame5)'
info.version  = '1.0.442'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_knife_elite'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
dict_elite = {}

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
        dict_elite[userid] = 0

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_knife_elite')


def player_spawn(event_var):
    userid = int(event_var['userid'])
    
    # Reset elite status
    dict_elite[userid] = 0
    
    # Use weapon
    player = gungamelib.getPlayer(userid)
    es.sexec(userid, 'use weapon_%s' % gungamePlayer.getWeapon())

def item_pickup(event_var):
    userid = int(event_var['userid'])
    item = event_var['item']
    
    # Not elite?
    if not dict_elite[userid]:
        return
    
    # Not a valid item?
    if item not in gungamelib.getWeaponList('all'):
        return
    
    # Remove item
    player = playerlib.getPlayer(userid)
    es.server.cmd('es_xremove %i' % player.get('weaponindex', item))

def gg_levelup(event_var):
    attacker = int(event_var['attacker'])
    player = gungamelib.getPlayer(attacker)
    
    # Is using knife already?
    if player.getWeapon() == 'knife':
        return
    
    # Strip them
    es.sexec(attacker, 'use weapon_knife')
    player.stripPlayer()
    
    # Set elite status
    dict_elite[attacker] = 1