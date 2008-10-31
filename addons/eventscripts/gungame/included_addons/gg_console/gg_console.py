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
info.name     = 'gg_console (for GunGame5)'
info.version  = '1.0.302'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_console'
info.author   = 'GunGame Development Team'

"""

# ==============================================================================
#   GLOBALS
# ==============================================================================
commands = {
    'levelup':
        {
            'type': playerFunc,
            'syntax': '<userid> <levels to award>',
            'attribute': 'levelup',
        },
}

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    # Register
    gg_console = gungamelib.registerAddon('gg_console')
    gg_console.setDisplayName('GG Console Interface')
    
    # Command registration
    gg_console.registerAdminCommand('gg', cmd_gg, '<command> <...>')

# ==============================================================================
#   CONSOLE COMMANDS
# ==============================================================================
def cmd_gg(userid, name, *args):
    # Check the command exists
    if name not in commands:
        #TODO: Show invalid command error
        return
    
    # Get command info
    info = commands[name]
    
    # Show the syntax
    if len(args) == 0:
        gungamelib.msg('gungame', 0, 0, 'InvalidSyntax', {'cmd': name, 'syntax': info['syntax']})
        return
    
    # Pass over to the type
    info['type'](userid, name, info, args)

def playerFunc(userid, name, info, args):
    # Get the target userid
    target = args[0]
    
    # Check the client is in the server
    if not gungamelib.clientInServer(target):
        gungamelib.msg('gungame', 0, 0, 'InvalidUserid', {'userid': target})
        return
    
    player = gungamelib.getPlayer(target)
    
    # Get the function
    func = getattr(player, info['attribute'], None)
    
    # Did we successfully get it?
    if func == None:
        gungamelib.msg('gungame', 0, 0, 'InternalError', {'cmd': name})
        return
    
    # Try and call the function
    
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
"""