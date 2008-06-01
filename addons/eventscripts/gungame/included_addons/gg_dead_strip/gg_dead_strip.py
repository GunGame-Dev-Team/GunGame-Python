''' (c) 2008 by the GunGame Coding Team

    Title: gg_dead_strip
    Version: 1.0.340
    Description: Removes dead player's weapons.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# Eventscripts imports
import es
import playerlib

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_dead_strip (for GunGame: Python)'
info.version  = '1.0.340'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_dead_strip'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
list_allWeapons = ['glock', 'usp', 'p228', 'deagle',
                   'elite', 'fiveseven', 'awp', 'scout',
                   'aug', 'mac10', 'tmp', 'mp5navy', 'ump45',
                   'p90', 'galil', 'famas', 'ak47', 'sg552',
                   'sg550', 'g3sg1', 'm249', 'm3', 'xm1014',
                   'm4a1', 'hegrenade', 'flashbang', 'smokegrenade']

roundActive = 1

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register this addon with GunGame
    gg_dead_strip = gungamelib.registerAddon('gg_dead_strip')
    gg_dead_strip.setDisplayName('GG Dead Strip')
    
    es.addons.registerClientCommandFilter(filterDrop)

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_dead_strip')
    
    es.addons.unregisterClientCommandFilter(filterDrop)

def es_map_start(event_var):
    global roundActive
    roundActive = 0

def round_start(event_var):
    global roundActive
    roundActive = 1
    
    # This makes it so there can be no idle weapons in the world, other than the
    # BSP entities.
    es.server.cmd('es_xfire %s game_weapon_manager AddOutput "maxpieces 0"' % es.getuserid())

def round_end(event_var):
    global roundActive
    roundActive = 0

def item_pickup(event_var):
    # Get variables
    item = event_var['item']
    userid = int(event_var['userid'])
    
    # Is a weapon?
    if item not in list_allWeapons:
        return
    
    # Client in server?
    if not gungamelib.clientInServer(userid):
        return
    
    # Get player objects
    gungamePlayer = gungamelib.getPlayer(userid)
    playerWeapon = gungamePlayer.getWeapon()
    playerlibPlayer = playerlib.getPlayer(userid)
    
    # Is warmup round?
    if gungamelib.getGlobal('isWarmup') == 1:
        # Only remove if the weapon is not the warmup weapon
        if item != gungamelib.getVariableValue('gg_warmup_weapon') and gungamelib.getVariableValue('gg_warmup_weapon') != 0:
            es.server.cmd('es_xremove %i' % playerlibPlayer.get('weaponindex', item))
    else:
        # Check to see if this is the right weapon for their level
        if playerWeapon == item:
            return
        
        if playerWeapon == 'hegrenade':
            # Is nade bonus loaded?
            nadeBonus = gungamelib.getVariableValue('gg_nade_bonus')
            
            # Check to see if the grenade level bonus weapon is active
            if nadeBonus:
                # Only remove if the item is not the nade bonus weapon
                if nadeBonus != item:
                    es.sexec(userid, 'use weapon_%s' % nadeBonus)
                    es.server.cmd('es_xremove %d' % playerlibPlayer.get('weaponindex', item))
            else:
                es.sexec(userid, 'use weapon_knife')
                es.server.cmd('es_xremove %d' % playerlibPlayer.get('weaponindex', item))
        else:
            es.sexec(userid, 'use weapon_%s' % playerWeapon)
            es.server.cmd('es_xremove %d' % playerlibPlayer.get('weaponindex', item))

'''OLD CODE:
def player_death(event_var):
    global roundActive
    if not roundActive:
        return
        
    # Make sure the player is on a team
    if int(event_var['es_userteam']) < 2:
        return
        
    # Get entity list
    dict_entityList = es.createentitylist()
    
    # Get list of idle weapons
    list_idleWeapons = filter(lambda x: dict_entityList[x]['classname'].startswith('weapon_') and es.getindexprop(x, 'CBaseEntity.m_hOwnerEntity') == -1 and dict_entityList[x]['classname'] != 'weapon_c4', dict_entityList)
    
    # Remove weapon
    for idleWeapon in list_idleWeapons:
        es.server.cmd('es_xremove %d' % idleWeapon)
'''

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def filterDrop(userid, args):
    # If command not drop, continue
    if args[0] != 'drop':
        return 1
    
    # Get player
    gungamePlayer = gungamelib.getPlayer(userid)
    playerlibPlayer = playerlib.getPlayer(userid)
    
    # Check to see if their current weapon is their level weapon
    if playerlibPlayer.attributes['weapon'] == 'weapon_%s' % gungamePlayer.getWeapon():
        # Don't let them drop it
        return 0
    else:
        # Let them drop it
        return 1