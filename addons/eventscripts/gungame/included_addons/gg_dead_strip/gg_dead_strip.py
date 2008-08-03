''' (c) 2008 by the GunGame Coding Team

    Title: gg_dead_strip
    Version: 1.0.432
    Description: Removes dead player's weapons.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# Eventscripts imports
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
info.name     = 'gg_dead_strip (for GunGame: Python)'
info.version  = '1.0.432'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_dead_strip'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
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
    if item not in gungamelib.getWeaponList('all'):
        return
    
    # Client in server?
    if not gungamelib.clientInServer(userid):
        return
    
    # Get player objects
    gungamePlayer = gungamelib.getPlayer(userid)
    weapon = gungamePlayer.getWeapon()
    playerlibPlayer = playerlib.getPlayer(userid)
    
    # Is warmup round?
    if gungamelib.getGlobal('isWarmup') == 1:
        # Only remove if the weapon is not the warmup weapon
        if item != gungamelib.getVariableValue('gg_warmup_weapon') and gungamelib.getVariableValue('gg_warmup_weapon') != 0:
            es.server.cmd('es_xremove %i' % playerlibPlayer.get('weaponindex', item))
        
        return
    
    # Check to see if this is the right weapon for their level
    if weapon == item:
        return
    
    # Get their current weapon
    currentWeapon = playerlibPlayer.attributes['weapon']
    
    if weapon == 'hegrenade':
        # Is nade bonus loaded?
        nadeBonus = gungamelib.getVariableValue('gg_nade_bonus')
        
        # Check to see if the grenade level bonus weapon is active
        if nadeBonus:
            # Only remove if the item is not the nade bonus weapon
            if nadeBonus == item:
                return
    
    # Remove the weapon they just picked up
    es.server.cmd('es_xremove %d' % playerlibPlayer.get('weaponindex', item))
    
    # If the player did not switch to the weapon they just picked up, no need to switch them back to their previous weapon
    if currentWeapon:
        if currentWeapon[7:] != item:
            return
    
    # Switch the player back to their previous weapon, wait for the next game frame
    gamethread.delayed(0, getLastWeapon, (userid, gungamePlayer, item))

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def getLastWeapon(userid, gungamePlayer, item):
    weapon = gungamePlayer.getWeapon()
    
    if weapon == item:
        return
    
    myWeapons = {1: 'knife',
                 2: weapon,
                 3: weapon,
                 4: 'hegrenade',
                 5: 'smokegrenade',
                 6: 'flashbang'}
    
    # Get their last weapon index
    lastWeapon = es.getplayerprop(userid, 'CBasePlayer.localdata.m_hLastWeapon')
    
    # Loop through all the current held weapons
    for slot in myWeapons:
        slotWeapon = es.getplayerprop(userid, 'CBaseCombatCharacter.bcc_localdata.m_hMyWeapons.%.3i' % slot)
        
        # Do the indexes not match?
        if lastWeapon != slotWeapon:
            es.sexec(userid, 'use weapon_%s' % myWeapons[slot])
            break

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