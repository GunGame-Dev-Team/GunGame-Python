''' (c) 2008 by the GunGame Coding Team

    Title: gg_console
    Version: 1.0.302
    Description: Provides console interface to be used by admins.
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# EventScripts imports
import es

# GunGame imports
import gungamelib

# ==============================================================================
#   ADDON REGISTRATION
# ==============================================================================
# Register with EventScripts
info = es.AddonInfo()
info.name     = 'gg_console (for GunGame: Python)'
info.version  = '1.0.302'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_console'
info.author   = 'GunGame Development Team'

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    # Register
    gg_console = gungamelib.registerAddon('gg_console')
    gg_console.setDisplayName('GG Console Interface')
    
    # Command registration
    gg_console.registerAdminCommand('setlevel', cmd_setlevel, '<userid> <level>')
    gg_console.registerAdminCommand('teleport', cmd_teleport, '<userid> <x> <y> <z>')

# ==============================================================================
#   CONSOLE COMMANDS
# ==============================================================================
def cmd_setlevel(userid, target, level):
    # Make sure the client is in the server
    if not gungamelib.clientInServer(target):
        gungamelib.msg('gungame', 0, 0, 'InvalidUserid', {'userid': target})
    
    # Get player and fire gg_levelup
    player = gungamelib.getPlayer(target)
    gungamelib.triggerLevelUpEvent(target, player['level'], level)

def cmd_teleport(userid, target, x, y, z):
    # Make sure the client is in the server
    if not gungamelib.clientInServer(target):
        gungamelib.msg('gungame', 0, 0, 'InvalidUserid', {'userid': target})
    
    # Make locations ints
    x = int(x)
    y = int(y)
    z = int(z)
    
    player = gungamelib.getPlayer(target)
    player.teleportPlayer(x, y, z)