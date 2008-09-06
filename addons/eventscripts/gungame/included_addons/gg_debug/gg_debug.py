''' (c) 2008 by the GunGame Coding Team

    Title: gg_debug
    Version: 1.0.462
    Description: Removes dead player's weapons.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# Eventscripts imports
import es
import time

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_debug (for GunGame: Python)'
info.version  = '1.0.462'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_debug'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register this addon with GunGame
    gg_debug = gungamelib.registerAddon('gg_debug')
    gg_debug.setDisplayName('GG Debug')
    
    gg_debug.registerAdminCommand('print_debug', printDebugInfo)

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_debug')

def printDebugInfo(userid):
    logPath = gungamelib.getGameDir('addons/eventscripts/gungame/logs/debug%s.txt' % time.time())
    
    registeredAddons = gungamelib.getRegisteredAddonlist()
    weaponOrder = dict(gungamelib.getCurrentWeaponOrder().order)
    
    debugfile = open(logPath, 'w')
    
    debugfile.write('GunGame5 version: %s \n' % es.ServerVar('eventscripts_ggp'))
    debugfile.write('File created: %s \n\n\n' % time.strftime('%d/%m/%Y @ [%H:%M:%S]'))
    
    debugfile.write('Registered Addons:\n-----------------------\n')
    for addon in registeredAddons:
        debugfile.write('%s\n' % addon)
    
    debugfile.write('\n\nWeaponOrder:\n-----------------------\n')
    for level in weaponOrder:
        debugfile.write('%s: [%s] %s\n' % (level, weaponOrder[level][1], weaponOrder[level][0]))
    
    debugfile.write('\n\nGungamePlayerAttributes:\n-----------------------\n')
    for userid in es.getUseridList():
        debugfile.write('\nUserid:%s ' % userid)
        gungamePlayer = gungamelib.getPlayer(userid)
        for attribute in gungamePlayer.__slots__:
            debugfile.write(' %s:%s ' %(attribute, gungamePlayer[attribute]))
        debugfile.write(' weapon:%s ' % gungamePlayer.getWeapon())
    
    debugfile.close()