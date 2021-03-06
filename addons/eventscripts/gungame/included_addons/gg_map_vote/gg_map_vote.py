''' (c) 2008 by the GunGame Coding Team

    Title: gg_map_vote
    Version: 5.0.560
    Description: Adds map voting capabilities to GunGame.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# Python imports
import os
import random
import time
from operator import itemgetter

# EventScripts imports
import es
import popuplib
import playerlib
import gamethread
import usermsg
import testrepeat as repeat

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_map_vote (for GunGame5)'
info.version  = '5.0.560'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_map_vote'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
# Console variables
dict_variables = {}
dict_variables['listFile'] = gungamelib.getVariable('gg_map_list_file')
dict_variables['listSource'] = gungamelib.getVariable('gg_map_list_source')
dict_variables['voteSize'] = gungamelib.getVariable('gg_map_vote_size')
dict_variables['showLastMaps'] = gungamelib.getVariable('gg_dont_show_last_maps')
dict_variables['voteTime'] = gungamelib.getVariable('gg_vote_time')
dict_variables['showVotes'] = gungamelib.getVariable('gg_show_player_vote')

# Dictionary for gg_map_list_source settings:
#  1 = mapcycle.txt
#  2 = maplist.txt
#  3 = specified file
#  4 = maps folder
dict_mapListFile = {}
dict_mapListFile[1] = 'mapcycle.txt'
dict_mapListFile[2] = 'maplist.txt'
dict_mapListFile[3] = str(dict_variables['listFile'])

# Dictionary of player vote choices
dict_playerChoice = {}

# Addon variables
dict_addonVars = {}
dict_addonVars['recentMaps'] = []
dict_addonVars['mapList'] = []
dict_addonVars['voteList'] = []
dict_addonVars['voteActive'] = 0
dict_addonVars['voteTimer'] = 0

# Old maphandler value
oldEventscriptsMaphandler = es.ServerVar('eventscripts_maphandler')
es.ServerVar('eventscripts_maphandler').set(1)

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_map_vote = gungamelib.registerAddon('gg_map_vote')
    gg_map_vote.setDisplayName('GG Map Vote')
    gg_map_vote.loadTranslationFile()

    # Create commands
    gg_map_vote.registerAdminCommand('vote_cancel', cancelVote)
    gg_map_vote.registerAdminCommand('vote_list', getVoteList)
    gg_map_vote.registerAdminCommand('vote_shuffle', shuffleVoteList)
    gg_map_vote.registerAdminCommand('vote_start', voteStart)
    
    # Set some globals
    gungamelib.setGlobal('voteActive', 0)
    
    # Add current map to list of recent maps
    if int(dict_variables['showLastMaps']):
        if str(es.ServerVar('eventscripts_currentmap')) != '':
            dict_addonVars['recentMaps'].append(str(es.ServerVar('eventscripts_currentmap')))
    
    initiateVote()

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_map_vote')
    
    # Restore original value for eventscripts_maphandler
    es.ServerVar('eventscripts_maphandler').set(oldEventscriptsMaphandler)
    
    # Delete popup
    if popuplib.exists('voteMenu'):
        popuplib.unsendname('voteMenu', es.getUseridList())
        popuplib.delete('voteMenu')
        
    # Delete repeat
    if repeat.status('gungameVoteCounter'):
        repeat.delete('gungameVoteCounter')


def player_disconnect(event_var):
    # Deduct from maximum votes
    if dict_addonVars['voteActive']:
        dict_playerChoice['maximumVotes'] -= 1

def es_map_start(event_var):
    # Add current map to list of recent maps
    if int(dict_variables['showLastMaps']):
        dict_addonVars['recentMaps'].append(event_var['mapName'])
        
        # Check size of recent map list
        if len(dict_addonVars['recentMaps']) > int(dict_variables['showLastMaps']):
            del dict_addonVars['recentMaps'][0]
    
    # Delete popup
    if popuplib.exists('voteMenu'):
        popuplib.unsendname('voteMenu', es.getUseridList())
        popuplib.delete('voteMenu')
    
    # Delete repeat
    if repeat.status('gungameVoteCounter'):
        repeat.delete('gungameVoteCounter')
    
    # Get vote ready
    initiateVote()

def gg_vote(event_var):
    if not dict_addonVars['voteActive'] and popuplib.exists('voteMenu'):
        startVote()

def gg_win(event_var):
    if dict_addonVars['voteActive']:
        if repeat.status('gungameVoteCounter'):
            repeat.delete('gungameVoteCounter')
        voteResults()
    
    winningMap = dict_playerChoice['winningMap']
    
    if winningMap != None:
        es.set('nextlevel', winningMap)
        gungamelib.msg('gg_map_vote', '#all', 'Nextmap', {'map': winningMap})

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def initiateVote():
    # =========================
    # GET LIST FROM MAPS FOLDER
    # =========================
    # Initialize variables
    mapDir = []
    files = os.listdir(gungamelib.getGameDir('maps'))
    
    # Get files
    for x in files:
        mapName, extension = os.path.splitext(x)
        
        if extension == '.bsp':
            mapDir.append(mapName)

    # Create a of maps for voting
    if int(dict_variables['listSource']) == 4:
        dict_addonVars['mapList'] = mapDir
    
    # =====================
    # GET LIST FROM MAPLIST
    # =====================
    # [ mapcycle.txt, maplist.txt or gg_maplist.txt ]
    else:
        # Get lines
        lines = gungamelib.getFileLines(dict_mapListFile[int(dict_variables['listSource'])])
        
        # Loop through the lines
        dict_addonVars['mapList'] = []
        for line in lines:
            # Is a valid map?
            if line in mapDir:
                dict_addonVars['mapList'].append(line)
    
    # Remove maps in the recent maps list
    for map in dict_addonVars['recentMaps']:
        if map in dict_addonVars['mapList'] and len(dict_addonVars['mapList']) > int(dict_variables['voteSize']):
            dict_addonVars['mapList'].remove(map)
    
    setVoteList()

def setVoteList():
    # Set the size of the vote list
    mapsQuantity = len(dict_addonVars['mapList'])
    
    if int(dict_variables['voteSize']) and mapsQuantity > int(dict_variables['voteSize']):
        dict_addonVars['voteList'] = random.sample(dict_addonVars['mapList'], int(dict_variables['voteSize']))
    else:
        dict_addonVars['voteList'] = dict_addonVars['mapList']
    
    # Create the menu popup
    votePopup = popuplib.easymenu('voteMenu', '_popup_choice', voteMenuSelect)
    
    # Set title for the menu
    votePopup.settitle('GG Map Vote: Next Map')
    
    # Loop through maps to build list
    for map in dict_addonVars['voteList']:
        votePopup.addoption(map, map)
    
    # Reset the player choice dict
    dict_playerChoice.clear()
    dict_playerChoice['votedMaps'] = {}
    dict_playerChoice['totalVotes'] = 0
    dict_playerChoice['winningMap'] = None
    dict_playerChoice['winningMapVotes'] = 0
    dict_playerChoice['maximumVotes'] = 0

def startVote():
    # Send the map vote to the players
    gungamelib.msg('gg_map_vote', '#all', 'PlaceYourVotes')
    popuplib.send('voteMenu', es.getUseridList())
    
    # Play vote
    es.cexec_all('play admin_plugin/actions/startyourvoting.mp3')
    
    # Start the countdown
    dict_addonVars['voteTimer'] = int(dict_variables['voteTime'])
    repeat.create('gungameVoteCounter', VoteCountdown)
    repeat.start('gungameVoteCounter', 1, 0)
    
    # Bot vote code
    if int(es.ServerVar('gg_vote_bots_vote')):
        # Send menu
        for userid in playerlib.getUseridList('#bot'):
            gamethread.delayed(random.randint(1, 5), voteMenuSelect, (userid, random.choice(dict_addonVars['voteList']), 0))
    
    # Set the active vars
    dict_addonVars['voteActive'] = 1
    gungamelib.setGlobal('voteActive', 1)
    
    # Set maximum votes possible
    dict_playerChoice['maximumVotes'] = int(es.getplayercount())

def VoteCountdown():
    if not dict_addonVars['voteTimer']:
        # Play beep sound
        gungamelib.playSound('#all', 'countDownBeep')
        
        # Delete the repeat
        if repeat.status('gungameVoteCounter'):
            repeat.delete('gungameVoteCounter')
        
        # Get results
        voteResults()
        
        return
    
    # Countdown 5 or less?
    if dict_addonVars['voteTimer'] <= 5:
        gungamelib.playSound('#all', 'countDownBeep')
    
    # Get vote info
    voteInfo = ''
    for map in sorted(dict_playerChoice['votedMaps'].items(), key=itemgetter(1), reverse=True):
        voteInfo += gungamelib.lang('gg_map_vote', 'MapVotes', {'map': map[0], 'votes': map[1]})
    
    # Send the HudHint
    if dict_addonVars['voteTimer'] == 1:
        gungamelib.hudhint('gg_map_vote', '#all', 'Countdown_Singular', {'voteInfo': voteInfo, 'votes': dict_playerChoice['totalVotes'], 'totalVotes': dict_playerChoice['maximumVotes']})
    else:
        gungamelib.hudhint('gg_map_vote', '#all', 'Countdown_Plural', {'time': dict_addonVars['voteTimer'], 'voteInfo': voteInfo, 'votes': dict_playerChoice['totalVotes'], 'totalVotes': dict_playerChoice['maximumVotes']})

    # Decrement timer
    dict_addonVars['voteTimer'] -= 1
    
def voteMenuSelect(userid, mapChoice, popupid):
    # Pressed 1 before the anti-1 press protection time was up?
    if dict_addonVars['voteTimer'] > int(dict_variables['voteTime'])-1:
        gungamelib.msg('gg_map_vote', userid, 'OnePressProtection')
        popuplib.send('voteMenu', userid)
        return
    
    # Get index of userid
    gungamePlayer = gungamelib.getPlayer(userid)
    index = gungamePlayer.index
    
    # Loop through the map choices
    if mapChoice not in dict_addonVars['voteList']:
        return
    
    # Increment total votes
    dict_playerChoice['totalVotes'] += 1
    
    # Announce players choice if enabled
    if int(dict_variables['showVotes']):
        # Get player name
        name = gungamePlayer.name
        
        # Announce to the world
        gungamelib.saytext2('gg_map_vote', '#all', index, 'VotedFor', {'name': name, 'map': mapChoice})
    
    # Register the vote
    if mapChoice not in dict_playerChoice['votedMaps']:
        dict_playerChoice['votedMaps'][mapChoice] = 1
    else:
        dict_playerChoice['votedMaps'][mapChoice] += 1
    
    # Have got enough votes?
    if dict_playerChoice['votedMaps'][mapChoice] > dict_playerChoice['winningMapVotes']:
        dict_playerChoice['winningMap'] = mapChoice
        dict_playerChoice['winningMapVotes'] = dict_playerChoice['votedMaps'][mapChoice]
    
    # All people voted
    if dict_playerChoice['totalVotes'] == dict_playerChoice['maximumVotes']:
        # Delete the repeat
        if repeat.status('gungameVoteCounter'):
            repeat.delete('gungameVoteCounter')
        
        # Show results
        voteResults()

def voteResults():
    # Set vars
    dict_addonVars['voteActive'] = 0
    dict_addonVars['voteList'] = []
    gungamelib.setGlobal('voteActive', 0)
    
    # Close and delete popup
    popuplib.unsendname('voteMenu', es.getUseridList())
    popuplib.delete('voteMenu')
    
    # Announce winning map
    if dict_playerChoice['totalVotes']:
        # Set eventscripts_nextmapoverride to the winning map
        es.ServerVar('eventscripts_nextmapoverride').set(dict_playerChoice['winningMap'])
        
        #Set Mani 'nextmap' if Mani is loaded
        if str(es.ServerVar('mani_admin_plugin_version')) != '0':
            es.server.queuecmd('ma_setnextmap %s' % dict_playerChoice['winningMap'])
        
        #Set SourceMods 'nextmap' if SourceMod is loaded
        if str(es.ServerVar('sourcemod_version')) != '0':
            es.server.queuecmd('sm_nextmap %s' % dict_playerChoice['winningMap'])
        
        # Announce the winning map
        gungamelib.msg('gg_map_vote', '#all', 'WinningMap', {'map': dict_playerChoice['winningMap'], 'votes': dict_playerChoice['winningMapVotes'], 'totalVotes': dict_playerChoice['totalVotes']})
        gungamelib.hudhint('gg_map_vote', '#all', 'Nextmap', {'map': dict_playerChoice['winningMap']})
    else:
        # Announce not enough votes
        gungamelib.msg('gg_map_vote','#all', 'NotEnoughVotes')

    # Play end of vote sound
    es.cexec_all('play admin_plugin/actions/endofvote.mp3')

# ==============================================================================
#  CONSOLE COMMANDS
# ==============================================================================
def cancelVote(userid):
    if not dict_addonVars['voteActive']:
        gungamelib.echo('gg_map_vote', 0, 0, 'NoVoteToCancel')
        return
    
    # Set variables
    dict_addonVars['voteActive'] = 0
    
    # Stop the counter
    if repeat.status('gungameVoteCounter'):
        repeat.delete('gungameVoteCounter')
    
    # Unsend popups
    popuplib.unsendname('voteMenu', es.getUseridList())
    popuplib.delete('voteMenu')
    
    # Cancel vote
    gungamelib.msg('gg_map_vote', '#all', 'VoteCancelled')

def getVoteList(userid):
    if not dict_addonVars['voteList']:
        gungamelib.echo('gg_map_vote', 0, 0, 'VoteListEmpty')
        return
    
    # Echo vote list
    gungamelib.echo('gg_map_vote', 0, 0, 'ListOfMaps')
    es.dbgmsg(0, ' '.join(dict_addonVars['voteList']))

def shuffleVoteList(userid):
    if dict_addonVars['voteActive']:
        gungamelib.echo('gg_map_vote', 0, 0, 'VoteAlreadyInProgress')
        return
    
    # Get new vote list
    setVoteList()
    
    # Echo new map list
    gungamelib.echo('gg_map_vote', 0, 0, 'NewMapList')
    es.dbgmsg(0, ' '.join(dict_addonVars['voteList']))

def voteStart(userid):
    if dict_addonVars['voteActive']:
        gungamelib.echo('gg_map_vote', 0, 0, 'VoteAlreadyInProgress')
        return
    
    if not popuplib.exists('voteMenu'):
        setVoteList()
    
    startVote()