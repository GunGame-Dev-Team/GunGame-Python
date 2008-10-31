''' (c) 2008 by the GunGame Coding Team

    Title: gg_info_menus
    Version: 1.0.476
    Description: GG Stats controls all stat related commands (level, score, top,
                 rank, etc).
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import popuplib
import playerlib
import gamethread

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_info_menus (for GunGame5)'
info.version  = '1.0.476'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_info_menus'
info.author   = 'GunGame Development Team'

orderedWinners = []
levelRankUseridList = []

def load():
    # Register addon
    gg_info_menus = gungamelib.registerAddon('gg_info_menus')
    gg_info_menus.setDisplayName('GG Info Menus')
    
    # Load the winners database into memory from file
    gungamelib.loadWinnerDatabase()
    
    # Loop through all the players
    for userid in es.getUseridList():
        # Get steamid
        steamid = gungamelib.getPlayer(userid).steamid
        
        # Is a bot?
        if 'BOT' in steamid:
            continue
        
        # Update timestamp
        if gungamelib.getWins(steamid):
            gungamelib.updateTimeStamp(steamid)
    
    # Build menus
    buildLevelMenu()
    buildLeaderMenu()
    buildTopMenu()
    buildScoreMenu()
    
    # Register commands
    gg_info_menus.registerPublicCommand('level', displayLevelMenu)
    gg_info_menus.registerPublicCommand('leader', displayLeadersMenu)
    gg_info_menus.registerPublicCommand('leaders', displayLeadersMenu)
    gg_info_menus.registerPublicCommand('top', displayTopMenu)
    gg_info_menus.registerPublicCommand('top10', displayTopMenu)
    gg_info_menus.registerPublicCommand('winners', displayTopMenu)
    gg_info_menus.registerPublicCommand('rank', displayRankMenu)
    gg_info_menus.registerPublicCommand('score', displayScoreMenu)

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_info_menus')
    
    # Save the database
    gungamelib.saveWinnerDatabase()

def server_cvar(event_var):
    if event_var['cvarname'] == 'gg_stats':
        buildLevelMenu()

def player_activate(event_var):
    # Get steamid
    steamid = gungamelib.getPlayer(event_var['userid']).steamid
    
    # Rebuild the score menu
    rebuildScoreMenu()
    
    # Is a bot?
    if 'BOT' in steamid:
        return
    
    # Update their timestamp
    if gungamelib.getWins(steamid):
        gungamelib.updateTimeStamp(steamid)

def player_disconnect(event_var):
    userid = int(event_var['userid'])
    
    # Rebuild the score menu
    rebuildScoreMenu()
    
    # Do not continue if the player does not exist
    if not gungamelib.playerExists(userid):
        return
    
    # Get steamid
    steamid = gungamelib.getPlayer(event_var['userid']).steamid
    
    # Is a bot?
    if 'BOT' in steamid:
        return
    
    # Update their timestamp
    if gungamelib.getWins(steamid):
        gungamelib.updateTimeStamp(steamid)

def gg_win(event_var):
    addWin(event_var['winner'])
    buildTopMenu()

def gg_levelup(event_var):
    # Get leader level
    leaderLevel = gungamelib.leaders.getLeaderLevel()
    
    # Make new leader menu
    if leaderLevel == int(event_var['new_level']):
        rebuildLeaderMenu()
    
    # Rebuild the score menu
    rebuildScoreMenu()

def gg_leveldown(event_var):
    # Rebuild the score menu
    rebuildScoreMenu()

def gg_new_leader(event_var):
    rebuildLeaderMenu()

def gg_tied_leader(event_var):
    rebuildLeaderMenu()

def gg_leader_lostlevel(event_var):
    rebuildLeaderMenu()

def displayLevelMenu(userid, player=None):
    if not player:
        popuplib.send('gungameLevelMenu', userid)
        return
    
    checkUserid = es.getuserid(player)
    
    if not checkUserid:
        gungamelib.msg('gungame', userid, 'LevelInfo_PlayerSearchFailed', {'player': player})
        return
    
    gungamePlayer = gungamelib.getPlayer(checkUserid)
    gungamelib.saytext2('gungame', userid, gungamePlayer['index'], 'LevelInfo_PlayerSearch',
                        {'player': gungamePlayer['name'], 'level': gungamePlayer['level'],
                        'weapon': gungamePlayer.getWeapon()}, False)

def buildLevelMenu():
    # Delete the popup if it exists
    if popuplib.exists('gungameLevelMenu'):
        popuplib.unsendname('gungameLevelMenu', playerlib.getUseridList('#human'))
        popuplib.delete('gungameLevelMenu')
    
    # Let's create the "gungameLevelMenu" popup
    gungameLevelMenu = popuplib.create('gungameLevelMenu')
    if gungamelib.getVariableValue('gg_multikill_override') == 0:
        gungameLevelMenu.addline('->1. LEVEL') # Line #1
        gungameLevelMenu.addline('   * You are on level <level number>') # Line #2
        gungameLevelMenu.addline('   * You need a <weapon name> kill to advance') # Line #3
        gungameLevelMenu.addline('   * There currently is no leader') # Line #4
    else:
        gungameLevelMenu.addline('->1. LEVEL') # Line #1
        gungameLevelMenu.addline('   * You are on level <level number> (<weapon name>)') # Line #2
        gungameLevelMenu.addline('   * You have made #/# of your required kills') # Line #3
        gungameLevelMenu.addline('   * There currently is no leader') # Line #4
    
    # Stats information
    if gungamelib.getVariableValue('gg_stats'):
        gungameLevelMenu.addline('->2. WINS') # Line #5
        gungameLevelMenu.addline('   * You have won <player win count> time(s)') # Line #6
        gungameLevelMenu.addline('->3. LEADER(s)') # Line #7
    else:
        gungameLevelMenu.addline('->2. LEADER(s)') # Line #5
    
    gungameLevelMenu.addline('   * Leader Level: There are no leaders') # Line #6
    gungameLevelMenu.addline('->   9. View Leaders Menu') # Line #7
    
    gungameLevelMenu.submenu(9, 'gungameLeadersMenu')
    gungameLevelMenu.prepuser = prepGunGameLevelMenu
    gungameLevelMenu.timeout('send', 5)
    gungameLevelMenu.timeout('view', 5)

def prepGunGameLevelMenu(userid, popupid):
    gungameLevelMenu = popuplib.find('gungameLevelMenu')
    gungamePlayer = gungamelib.getPlayer(userid)
    
    if gungamelib.getVariableValue('gg_multikill_override') == 0:
        gungameLevelMenu.modline(2, '   * You are on level %d' %gungamePlayer['level']) # Line #2
        gungameLevelMenu.modline(3, '   * You need a %s kill to advance' %gungamePlayer.getWeapon()) # Line #3
    else:
        gungameLevelMenu.modline(2, '   * You are on level %d (%s)' %(gungamePlayer['level'], gungamePlayer.getWeapon())) # Line #2
        gungameLevelMenu.modline(3, '   * You have made %d/%d of your required kills' %(gungamePlayer['multikill'], gungamelib.getVariableValue('gg_multikill_override'))) # Line #3
    
    leaderLevel = gungamelib.leaders.getLeaderLevel()
    playerLevel = gungamePlayer['level']
    
    if leaderLevel > 1:
        # See if the player is a leader:
        if playerLevel == leaderLevel:
            # See if there is more than 1 leader
            if gungamelib.leaders.getLeaderCount() > 1:
                # This player is tied with other leaders
                gungameLevelMenu.modline(4, '   * You are currently tied for the leader position') # Line #4
            else:
                # This player is the only leader
                gungameLevelMenu.modline(4, '   * You are currently the leader') # Line #4
        # This player is not a leader
        else:
            levelsBehindLeader = leaderLevel - playerLevel
            if levelsBehindLeader == 1:
                gungameLevelMenu.modline(4, '   * You are 1 level behind the leader') # Line #4
            else:
                gungameLevelMenu.modline(4, '   * You are %d levels behind the leader' %levelsBehindLeader) # Line #4
    else:
        # There are no leaders
        gungameLevelMenu.modline(4, '   * There currently is no leader') # Line #4
    if gungamelib.getVariableValue('gg_stats'):
        gungameLevelMenu.modline(6, '   * You have won %d time(s)' %gungamelib.getWins(gungamePlayer['steamid'])) # Line #6
        if leaderLevel > 1:
            gungameLevelMenu.modline(8, '   * Leader Level: %d (%s)' %(leaderLevel, gungamelib.getLevelWeapon(leaderLevel))) # Line #8
        else:
            gungameLevelMenu.modline(8, '   * Leader Level: There are no leaders') # Line #8
    else:
        if leaderLevel > 1:
            gungameLevelMenu.modline(6, '   * Leader Level: %d (%s)' %(leaderLevel, gungamelib.getLevelWeapon(leaderLevel))) # Line #6
        else:
            gungameLevelMenu.modline(6, '   * Leader Level: There are no leaders') # Line #6

def displayLeadersMenu(userid):
    popuplib.send('gungameLeadersMenu', userid)

def buildLeaderMenu():
    # Check if the popup exists
    if popuplib.exists('gungameLeadersMenu'):
        # Unsend and delete is
        popuplib.unsendname('gungameLeadersMenu', playerlib.getUseridList('#human'))
        popuplib.delete('gungameLeadersMenu')
    
    # Create the menu
    gungameLeadersMenu = popuplib.create('gungameLeadersMenu')
    gungameLeadersMenu.addline('->1. Current Leaders:')
    gungameLeadersMenu.addline('--------------------------')
    gungameLeadersMenu.addline('   * There currently is no leader')
    gungameLeadersMenu.addline('--------------------------')
    gungameLeadersMenu.addline('0. Exit')
    gungameLeadersMenu.timeout('send', 5)
    gungameLeadersMenu.timeout('view', 5)

def rebuildLeaderMenu():
    # Un-send and delete the menu
    if popuplib.exists('gungameLeadersMenu'):
        popuplib.unsendname('gungameLeadersMenu', playerlib.getUseridList('#human'))
        popuplib.delete('gungameLeadersMenu')
    
    # Get leader info
    leaderLevel = gungamelib.leaders.getLeaderLevel()
    leaderNames = gungamelib.leaders.getLeaderNames()
    
    # Let's create the "gungameLeadersMenu" popup
    gungameLeadersMenu = popuplib.create('gungameLeadersMenu')
    gungameLeadersMenu.addline('->1. Current Leaders:')
    gungameLeadersMenu.addline('    Level %d (%s)' % (leaderLevel, gungamelib.getLevelWeapon(leaderLevel)))
    gungameLeadersMenu.addline('--------------------------')
    
    # Add leaders
    for name in leaderNames:
        gungameLeadersMenu.addline('   * %s' % name)
    
    # Finish off the menu
    gungameLeadersMenu.addline('--------------------------')
    gungameLeadersMenu.addline('0. Exit')
    gungameLeadersMenu.timeout('send', 5)
    gungameLeadersMenu.timeout('view', 5)

def displayTopMenu(userid):
    if gungamelib.getVariableValue('gg_stats'):
        gungamelib.sendOrderedMenu('top_menu', userid)

def buildTopMenu():
    global orderedWinners
    orderedWinners = gungamelib.getOrderedWinners()
    
    menu = gungamelib.OrderedMenu('top_menu', [], 10, prepTopMenu)
    menu.setTitle('GunGame: Top Players')
    
    for winner in orderedWinners:
        # Get winner information
        name = gungamelib.getWinnerName(winner)
        wins = gungamelib.getWins(winner)
        plural = '' if wins == 1 else 's'
        
        # Add menu item
        menu.addItem('%s: %s win%s' % (name, wins, plural))
    
    menu.buildMenu()

def prepTopMenu(userid, popupid):
    steamid = gungamelib.getPlayer(userid).steamid
    if steamid not in orderedWinners:
        return
    
    rank = orderedWinners.index(steamid) + 1
    page = int((rank - 1) / 10) + 1
    
    if popupid != 'OrderedMenu_top_menu:%s' % page:
        return
    
    lineNumber = rank - (page * 10) + 12 if page > 1 else rank + 2
    name = gungamelib.getWinnerName(steamid)
    wins = gungamelib.getWins(steamid)
    plural = '' if wins == 1 else 's'
    
    menu = popuplib.find(popupid)
    menu.modline(lineNumber, '->%i. %s: %s win%s' % (rank, name, wins, plural))
    gamethread.delayed(0, menu.modline, (lineNumber, '%i. %s: %s win%s' % (rank, name, wins, plural)))

def displayRankMenu(userid):
    if not gungamelib.getVariableValue('gg_stats'):
        return
    
    steamid = gungamelib.getPlayer(userid).steamid
    if steamid in orderedWinners:
        rank = orderedWinners.index(steamid) + 1
        page = int((rank - 1) / 10) + 1
        gungamelib.sendOrderedMenu('top_menu', userid, page)
    else:
        gungamelib.sendOrderedMenu('top_menu', userid)

def displayScoreMenu(userid):
    if userid in levelRankUseridList:
        rank = levelRankUseridList.index(userid) + 1
        page = int((rank - 1) / 10) + 1
        gungamelib.sendOrderedMenu('score_menu', userid, page)
    else:
        gungamelib.sendOrderedMenu('score_menu', userid)
    
def buildScoreMenu():
    global levelRankUseridList
    levelRankUseridList = []

    menu = gungamelib.OrderedMenu('score_menu', [], 10, prepScoreMenu)
    menu.setTitle('GunGame: Player Score')
    
    if len(es.getUseridList()):
        levelCounter = gungamelib.getTotalLevels() + 1
        
        while levelCounter > 0:
            levelCounter -= 1
            for playerid in gungamelib.getLevelUseridList(levelCounter):
                menu.addItem('[%i] %s' % (levelCounter, gungamelib.getPlayer(playerid)['name']))
                levelRankUseridList.append(playerid)
        
        for emptySlot in range(0, es.getmaxplayercount() - len(levelRankUseridList)):
            menu.addItem(' ')
        
    else:
        menu.addItem('No Players.')
    
    menu.buildMenu()
    
def rebuildScoreMenu():
    global levelRankUseridList
    levelRankUseridList = []

    menu = gungamelib.OrderedMenu('score_menu', [], 10, prepScoreMenu)
    
    levelCounter = gungamelib.getTotalLevels() + 1
    while levelCounter > 0:
        levelCounter -= 1
        for playerid in gungamelib.getLevelUseridList(levelCounter):
            playerName = gungamelib.getPlayer(playerid)['name']
            if not playerName:
                continue
                
            menu.addItem('[%i] %s' % (levelCounter, playerName))
            levelRankUseridList.append(playerid)
    
    for emptySlot in range(0, es.getmaxplayercount() - len(levelRankUseridList)):
        menu.addItem(' ')
    
    menu.rebuildMenu()
    
    popupMenu = popuplib.find('OrderedMenu_score_menu:1')
    for userid in es.getUseridList():
        popupMenu.update(userid)

def prepScoreMenu(userid, popupid):
    rank = levelRankUseridList.index(userid) + 1
    page = int((rank - 1) / 10) + 1
    
    if popupid != 'OrderedMenu_score_menu:%s' % page:
        return
    
    lineNumber = rank - (page * 10) + 12 if page > 1 else rank + 2
    gungamePlayer = gungamelib.getPlayer(userid)
    level = gungamePlayer['level']
    name = gungamePlayer['name']
    
    menu = popuplib.find(popupid)
    menu.modline(lineNumber, '->%i. [%i] %s' % (rank, level, name))
    gamethread.delayed(0, menu.modline, (lineNumber, '%i. [%i] %s' % (rank, level, name)))

def addWin(userid):
    # Get steamid
    steamid = gungamelib.getPlayer(userid).steamid
    
    # Is a bot?
    if 'BOT' in steamid:
        return
    
    # Add win to database
    gungamelib.addWin(steamid)
    
    # Prune old winners and save the database
    gungamelib.pruneWinnerDatabase(gungamelib.getVariableValue('gg_prune_database'))
    gungamelib.saveWinnerDatabase()
