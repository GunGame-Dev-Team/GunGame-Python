''' (c) 2008 by the GunGame Coding Team

    Title: gg_save_winners
    Version: 1.0.340
    Description: Saves the GunGame winners to a local-disk database.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts Imports
import es
import popuplib

# GunGame Imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_save_winners (for GunGame: Python)'
info.version  = '1.0.340'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_save_winners'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register this addon with GunGame
    gg_save_winners = gungamelib.registerAddon('gg_save_winners')
    gg_save_winners.setDisplayName('GG Save Winners')
    
    # Register command
    gg_save_winners.registerCommand('winners', sendWinnerMenu, console=False, log=False)
    
    # Load the winners database into memory from file
    gungamelib.loadWinnerDatabase()
    
    # Loop through all the players
    for userid in es.getUseridList():
        # Get steamid
        steamid = es.getplayersteamid(userid)
        
        # Is a bot?
        if 'BOT' in steamid: continue
        
        # Update timestamp
        if gungamelib.getWins(steamid):
            gungamelib.updateTimeStamp(steamid)

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_save_winners')
    
    # Save the database
    gungamelib.saveWinnerDatabase()


def player_activate(event_var):
    # Get steamid
    steamid = event_var['es_steamid']
    
    # Is a bot?
    if 'BOT' in steamid: return
    
    # Update their timestamp
    if gungamelib.getWins(steamid):
        gungamelib.updateTimeStamp(steamid)

def player_disconnect(event_var):
    # Get steamid
    steamid = event_var['networkid']
    
    # Is a bot?
    if 'BOT' in steamid: return
    
    # Update their timestamp
    if gungamelib.getWins(steamid):
        gungamelib.updateTimeStamp(steamid)

def gg_win(event_var):
    addWin(event_var['userid'])
    
def gg_round_win(event_var):
    addWin(event_var['userid'])

# ==============================================================================
#  WINNER MENU
# ==============================================================================
def sendWinnerMenu(userid):
    buildWinnerMenu()
    popuplib.send('gg_winners', userid)

def buildWinnerMenu():
    menu = popuplib.easylist('gg_winners')
    menu.settitle('GG Winners')
    
    for winner in gungamelib.getOrderedWinners():
        # Get winner information
        name = gungamelib.getWinnerName(winner)
        wins = gungamelib.getWins(winner)
        plural = '' if wins == 1 else 's'
        
        # Add menu item
        menu.additem('%s: %s win%s' % (name, wins, plural))

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def addWin(userid):
    # Get steamid
    steamid = es.getplayersteamid(userid)
    
    # Is a bot?
    if 'BOT' in steamid: return
    
    # Add win to database
    gungamelib.addWin(steamid)
    
    # Prune old winners and save the database
    gungamelib.pruneWinnerDatabase(gungamelib.getVariableValue('gg_prune_database'))
    gungamelib.saveWinnerDatabase()