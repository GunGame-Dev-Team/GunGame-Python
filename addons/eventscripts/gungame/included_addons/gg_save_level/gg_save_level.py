''' (c) 2008 by the GunGame Coding Team

    Title: gg_save_level
    Version: 1.0.382
    Description: Saves a players level when they disconnect and restores it when
                 they reconnect (will reset at the end of a game).
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
info.name     = 'gg_save_level (for GunGame: Python)'
info.version  = '1.0.382'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_save_level'
info.author   = 'GunGame Development Team'

# ==============================================================================
#   GLOBALS
# ==============================================================================
gLevels = {}

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    # Register
    gg_save_level = gungamelib.registerAddon('gg_save_level')
    gg_save_level.setDisplayName('GG Save Level')
    
    # Dependencies
    gg_save_level.addDependency('gg_retry_punish', 0)
    gg_save_level.addDependency('gg_handicap', 0)

def unload():
    gungamelib.unregisterAddon('gg_save_level')


def es_map_start(event_var):
    # Clear the levels dictionary
    gLevels.clear()

def gg_win(event_var):
    # Clear the levels dictionary
    gLevels.clear()

def gg_round_win(event_var):
    # Clear the levels dictionary
    gLevels.clear()

def player_activate(event_var):
    # Get player info
    userid = int(event_var['userid'])
    
    # Set players level
    gungamePlayer = gungamelib.getPlayer(userid)
    uniqueid = gungamePlayer['steamid']
    
    # No stored level information?
    if not gLevels.has_key(uniqueid):
        return
    
    # Display message
    gungamelib.msg('gg_save_level', userid, 'RestoredLevel', {'level': gLevels[uniqueid]})
    
    # Level up
    gungamelib.triggerLevelUpEvent(userid, gungamePlayer['level'], gLevels[uniqueid])
    
    # Remove from the dictionary
    del gLevels[uniqueid]

def player_disconnect(event_var):
    # Get player info
    userid = int(event_var['userid'])
    
    # Try to get the player
    try:
        gungamePlayer = gungamelib.getPlayer(userid)
    except gungamelib.UseridError:
        return
    
    # Save level
    gLevels[gungamePlayer['steamid']] = gungamePlayer['level']