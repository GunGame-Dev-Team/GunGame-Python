''' (c) 2008 by the GunGame Coding Team

    Title: gg_retry_punish
    Version: 1.0.302
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
info.version  = '1.0.302'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_retry_punish'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
dict_reconnectingPlayers = {}

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
    dict_reconnectingPlayers.clear()
    
def player_activate(event_var):
    # Retrieve the uniqueid from the player's attributes
    gungamePlayer = gungamelib.getPlayer(event_var['userid'])
    steamid = gungamePlayer['steamid']
    
    # We don't want this to happen for BOTS
    if 'BOT' in steamid:
        return
        
    # See if this player was set up in the Reconnecting Players Dictionary
    if dict_reconnectingPlayers.has_key(steamid):
        # Yes, they were. Therefore, we set their level to be whatever it needs to be
        gungamePlayer['level'] = dict_reconnectingPlayers[steamid]
        
        # Delete the player from the Reconnecting Players Dictionary
        del dict_reconnectingPlayers[steamid]

def player_disconnect(event_var):
    userid = int(event_var['userid'])

    if not gungamelib.playerExists(userid):
        return

    # Retrieve the uniqueid from the player's attributes
    gungamePlayer = gungamelib.getPlayer(userid)
    steamid = gungamePlayer['steamid']
    
    # We don't want this to happen for BOTS
    if 'BOT' in steamid:
        return
        
    # See if this player is already in the Reconnecting Players Dictionary (shouldn't ever be, but we will check anyhow, just to be safe)
    if not dict_reconnectingPlayers.has_key(steamid):
        # Set this player up in the Reconnecting Players Dictionary
        reconnectLevel = gungamePlayer['level'] - gungamelib.getVariableValue('gg_retry_punish')
        if reconnectLevel > 0:
            dict_reconnectingPlayers[steamid] = reconnectLevel
        else:
            dict_reconnectingPlayers[steamid] = 1
            
def gg_win(event_var):
    # Clear out the dictionary on unload
    dict_reconnectingPlayers.clear()
    
def gg_round_win(event_var):
    # Clear out the dictionary on unload
    dict_reconnectingPlayers.clear()