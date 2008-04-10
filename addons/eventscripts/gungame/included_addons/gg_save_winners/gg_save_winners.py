''' (c) 2008 by the GunGame Coding Team

    Title: gg_save_winners
    Version: 1.0.274
    Description: Saves the GunGame winners to a database to
                 be queried.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts Imports
import es
import playerlib

# GunGame Imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_save_winners (for GunGame: Python)'
info.version  = '1.0.274'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_save_winners'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register this addon with GunGame
    gg_retry_punish = gungamelib.registerAddon('gg_save_winners')
    gg_retry_punish.setDisplayName('GG Save Winners')
    
    # Load the winners database into memory from file
    gungamelib.loadWinnersDataBase()
    
    for userid in es.getUseridList():
        gungamePlayer = gungamelib.getPlayer(userid)
        steamid = gungamePlayer['steamid']
        if not 'BOT' in steamid:
            if gungamelib.getWins(steamid):
                # Yes, they have won before...let's be nice and update their timestamp
                gungamelib.updateTimeStamp(steamid)

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_save_winners')
    
    # Save the database
    gungamelib.saveWinnerDatabase()
    
def player_activate(event_var):
    gungamePlayer = gungamelib.getPlayer(event_var['userid'])
    steamid = gungamePlayer['steamid']
    
    # We don't want this to happen for BOTS
    if 'BOT' in steamid:
        return
    
    # See if the player has won before
    if gungamelib.getWins(steamid):
        # Yes, they have won before...let's be nice and update their timestamp
        gungamelib.updateTimeStamp(steamid)
        
def player_disconnect(event_var):
    userid = event_var['userid']
    
    if not gungamelib.playerExists(userid):
        return
        
    # Retrieve the uniqueid from the player's attributes
    gungamePlayer = gungamelib.getPlayer(userid)
    steamid = gungamePlayer['steamid']
    
    # We don't want this to happen for BOTS
    if 'BOT' in steamid:
        return
    
    # See if the player has won before
    if gungamelib.getWins(steamid):
        # Yes, they have won before...let's be nice and update their timestamp
        gungamelib.updateTimeStamp(steamid)
        
def gg_win(event_var):
    # Retrieve the uniqueid and set it to a variable
    gungamePlayer = gungamelib.getPlayer(event_var['userid'])
    steamid = gungamePlayer['steamid']
    
    # Add the win to the database
    gungamelib.addWin(steamid)
    
    # Clear out old entries in the winners database
    gungamelib.cleanWinnersDataBase(gungamelib.getVariableValue('gg_prune_database'))
    
    # Save the database
    gungamelib.saveWinnerDatabase()
    
def gg_round_win(event_var):
    # Retrieve the uniqueid and set it to a variable
    gungamePlayer = gungamelib.getPlayer(event_var['userid'])
    steamid = gungamePlayer['steamid']
    
    # Add the win to the database
    gungamelib.addWin(steamid)
    
    # Clear out old entries in the winners database
    gungamelib.cleanWinnersDataBase(gungamelib.getVariableValue('gg_prune_database'))
    
    # Save the database
    gungamelib.saveWinnerDatabase()