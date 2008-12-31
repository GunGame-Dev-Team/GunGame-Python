''' (c) 2008 by the GunGame Coding Team

    Title: gg_dead_strip
    Version: 5.0.559
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
info.name     = 'gg_dead_strip (for GunGame5)'
info.version  = '5.0.559'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_dead_strip'
info.author   = 'GunGame Development Team'


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


def round_start(event_var):
    # This makes it so there can be no idle weapons in the world, other than the
    # BSP entities.
    es.server.queuecmd('es_xfire %s game_weapon_manager AddOutput "maxpieces 0"' % es.getuserid())

def item_pickup(event_var):
    # Get variables
    item = event_var['item']
    userid = int(event_var['userid'])
    
    # Is a weapon?
    if item not in gungamelib.getWeaponList('all'):
        return
    
    # Client in server?
    if not gungamelib.clientInServer(userid) or not gungamelib.playerExists(userid):
        return
    
    # Get player objects
    gungamePlayer = gungamelib.getPlayer(userid)
    weapon = gungamePlayer.getWeapon()
    
    # Check to see if the weapon is their gungame weapon or in their strip exceptions
    if item == weapon or item in gungamePlayer.stripexceptions + ['flashbang', 'smokegrenade']:
        return
    
    # Get the players current weapon
    playerlibPlayer = playerlib.getPlayer(userid)
    currentWeapon = playerlibPlayer.attributes['weapon']
    
    # Remove the weapon they just picked up
    gungamelib.safeRemove(playerlibPlayer.get('weaponindex', item))
    
    # If the player did not switch to the weapon they just picked up, no need to switch them back to their previous weapon
    if currentWeapon:
        if currentWeapon[7:] != item:
            return
    
    # Switch to knife just incase they don't have their grenade
    if weapon == 'hegrenade':
        es.sexec(userid, 'use weapon_knife')
    
    # Switch to their gungame weapon
    es.sexec(userid, 'use weapon_%s' % weapon)

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def filterDrop(userid, args):
    # If command not drop, continue
    if args[0].lower() != 'drop':
        return 1
    
    # Get player and their info
    gungamePlayer = gungamelib.getPlayer(userid)
    weapon = gungamePlayer.getWeapon()
    playerlibPlayer = playerlib.getPlayer(userid)
    curWeapon = playerlibPlayer.attributes['weapon']
    
    # Check to see if their current weapon is their level weapon
    if weapon != 'hegrenade':
        return int(curWeapon != 'weapon_%s' % weapon)
    
    # ================
    # NADE BONUS CHECK
    # ================
    nadeBonusWeapons = str(gungamelib.getVariableValue('gg_nade_bonus')).split(',')
    
    # Is nade bonus enabled?
    if nadeBonusWeapons[0] == '0':
        return int(curWeapon != 'weapon_%s' % weapon)
    
    # Loop through the nade bonus weapons
    for nadeWeapon in nadeBonusWeapons:
        # Prefix weapon_
        if not nadeWeapon.startswith('weapon_'):
            nadeWeapon = 'weapon_%s' % nadeWeapon
        
        # Don't allow them to drop it
        if nadeWeapon == curWeapon:
            return 0
    
    # Allow them to drop it
    return 1