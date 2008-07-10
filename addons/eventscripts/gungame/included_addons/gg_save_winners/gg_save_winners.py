''' (c) 2008 by the GunGame Coding Team

    Title: gg_save_winners
    Version: 1.0.402
    Description: Saves the GunGame winners to a local-disk database.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts Imports
import es
import popuplib
import gamethread
import usermsg

# GunGame Imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_save_winners (for GunGame: Python)'
info.version  = '1.0.402'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_save_winners'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register this addon with GunGame
    gg_save_winners = gungamelib.registerAddon('gg_save_winners')
    gg_save_winners.setDisplayName('GG Winners')
    
    # Register command
    gg_save_winners.registerPublicCommand('winners', sendWinnerMenu)
    gg_save_winners.registerPublicCommand('top', sendTopMenu)
    gg_save_winners.registerPublicCommand('rank', sendRankMsg)
    
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
#  RANK MENU
# ==============================================================================
def sendRankMsg(userid):
    steamid = es.getplayersteamid(userid)
    wins = gungamelib.getWins(steamid)
    
    # No wins?
    if not wins:
        gungamelib.msg('gg_save_winners', userid, 'NoWins')
        return
    
    # Get the rank
    rank = gungamelib.getWinnerRank(steamid)
    total = gungamelib.getTotalWinners()
    
    gungamelib.msg('gg_save_winners', userid, 'CurrentRank', {'rank': rank, 'total': total, 'wins': wins})

# ==============================================================================
#  TOP 10 WINNERS MENU
# ==============================================================================
def sendTopMenu(userid):
    buildTopMenu()
    gungamelib.sendOrderedMenu('top_winners', userid)

def buildTopMenu():
    menu = gungamelib.OrderedMenu('top_winners')
    menu.setTitle('GunGame: Top 10 Winners')
    
    for winner in gungamelib.getOrderedWinners()[:10]:
        # Get winner information
        name = gungamelib.getWinnerName(winner)
        wins = gungamelib.getWins(winner)
        plural = '' if wins == 1 else 's'
        
        # Add menu item
        menu.addItem('%s: %s win%s' % (name, wins, plural))

# ==============================================================================
#  WINNER MENU
# ==============================================================================
def sendWinnerMenu(userid):
    buildWinnerMenu()
    gungamelib.sendOrderedMenu('winners', userid)

def buildWinnerMenu():
    menu = gungamelib.OrderedMenu('winners')
    menu.setTitle('GunGame: All Winners')
    
    for winner in gungamelib.getOrderedWinners():
        # Get winner information
        name = gungamelib.getWinnerName(winner)
        wins = gungamelib.getWins(winner)
        plural = '' if wins == 1 else 's'
        
        # Add menu item
        menu.addItem('%s: %s win%s' % (name, wins, plural))

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