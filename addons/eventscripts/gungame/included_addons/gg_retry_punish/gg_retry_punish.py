''' (c) 2008 by the GunGame Coding Team

    Title: gg_retry_punish
    Version: 1.0.348
    Description: Punishes players for disconnecting and
                 reconnecting in the same GunGame round.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts Imports
import es

# GunGame Imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_retry_punish (for GunGame: Python)'
info.version  = '1.0.348'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_retry_punish'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
dict_savedLevels = {}

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register this addon with GunGame
    gg_retry_punish = gungamelib.registerAddon('gg_retry_punish')
    gg_retry_punish.setDisplayName('GG Retry Punish')

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_retry_punish')
    
    # Clear out the dictionary on unload
    dict_savedLevels.clear()


def es_map_start(event_var):
    dict_savedLevels.clear()

def player_activate(event_var):
    steamid = event_var['es_steamid']
    
    # We don't want this to happen for BOTs
    if 'BOT' in steamid:
        return
    
    # Reconnecting?
    if dict_savedLevels.has_key(steamid):
        # Reset level
        gungamePlayer['level'] = dict_savedLevels[steamid]
        
        # Delete the saved level
        del dict_savedLevels[steamid]

def player_disconnect(event_var):
    userid = int(event_var['userid'])
    steamid = event_var['networkid']
    
    # Does the player exist?
    if not gungamelib.playerExists(userid):
        return
    
    # Don't save level
    if 'BOT' in steamid:
        return
    
    # Set reconnect level
    reconnectLevel = gungamelib.getPlayer(userid)['level'] - gungamelib.getVariableValue('gg_retry_punish')
    
    if reconnectLevel > 0:
        dict_savedLevels[steamid] = reconnectLevel
    else:
        dict_savedLevels[steamid] = 1

def gg_win(event_var):
    dict_savedLevels.clear()

def gg_round_win(event_var):
    dict_savedLevels.clear()