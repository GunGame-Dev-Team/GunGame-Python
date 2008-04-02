''' (c) 2008 by the GunGame Coding Team

    Title: gg_map_vote
    Version: 1.0.238
    Description: Adds map voting capabilities to GunGame.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# Python imports
import os
import random
from operator import itemgetter

# EventScripts imports
import es
import popuplib
import playerlib
import gamethread
import usermsg
import repeat

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_map_vote (for GunGame: Python)'
info.version  = '1.0.238'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
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
dict_mapListFile[1] = '/cstrike/mapcycle.txt'
dict_mapListFile[2] = '/cstrike/maplist.txt'
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

    # create commands
    if not es.exists('command','gg_vote_cancel'):
        es.regcmd('gg_vote_cancel','gungame/included_addons/gg_map_vote/cancelVote','Cancels an active map vote.')
    if not es.exists('command','gg_vote_list'):
        es.regcmd('gg_vote_list','gungame/included_addons/gg_map_vote/getVoteList','Gets a list of maps in the upcoming vote.')
    if not es.exists('command','gg_vote_shuffle'):
        es.regcmd('gg_vote_shuffle','gungame/included_addons/gg_map_vote/shuffleVoteList','Gets a new random set of maps for the upcoming vote.')
    if not es.exists('command','gg_vote_start'):
        es.regcmd('gg_vote_start','gungame/included_addons/gg_map_vote/voteStart','Start a random map vote.')
    
    # Set some globals
    gungamelib.setGlobal('voteActive', 0)
    
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
    if repeat.status('voteCounter'):
        repeat.delete('voteCounter')


def es_map_start(event_var):
    # Add current map to list of recent maps
    if int(dict_variables['showLastMaps']):
        dict_addonVars['recentMaps'].append(event_var['mapName'])
        # check size of recent map list
        if len(dict_addonVars['recentMaps']) > int(dict_variables['showLastMaps']):
            del dict_addonVars['recentMaps'][0]
            
    # Delete popup
    if popuplib.exists('voteMenu'):
        popuplib.unsendname('voteMenu', es.getUseridList())
        popuplib.delete('voteMenu')
        
    # Delete repeat
    if repeat.status('voteCounter'):
        repeat.delete('voteCounter')
        
    # Get vote ready
    initiateVote()

def gg_vote(event_var):
    if not dict_addonVars['voteActive'] and popuplib.exists('voteMenu'):
        startVote()

def gg_win(event_var):
    if dict_addonVars['voteActive']:
        repeat.delete('voteCounter')
        voteResults()
    winningMap = dict_playerChoice['winningMap']
    if winningMap != None:
        es.set('nextlevel', winningMap)
        gungamelib.msg('gg_map_vote','#all', 'Nextmap', {'map': winningMap})

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def initiateVote():
    # Get list of maps from cstrike/maps
    list_mapDir = []
    mapsDir = os.listdir(os.getcwd() + '/cstrike/maps/')
    for map in mapsDir:
        (mapName, extension) = os.path.splitext(map)
        if extension == '.bsp':
            list_mapDir.append(mapName)

    # Create a of maps for voting
    if int(dict_variables['listSource']) == 4:
        # get list of maps from /cstrike/maps
        dict_addonVars['mapList'] = list_mapDir
    else:
        # get list of maps from mapcycle.txt, maplist.txt or gg_maplist.txt
        dict_addonVars['mapList'] = []
        list_mapListFile = open(os.getcwd() + dict_mapListFile[int(dict_variables['listSource'])], 'r')
        for line in list_mapListFile:
            line = line.strip()
            if not line.startswith('//') and line != '' and line in list_mapDir:
                dict_addonVars['mapList'].append(line)
    
    # Remove maps in the RecentMaps list
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
    votePopup.settitle('Next Map?')
    
    # Loop through maps to build list
    for map in dict_addonVars['voteList']:
        votePopup.addoption(map, map)
        
    # Reset the player choice dict
    dict_playerChoice.clear()
    dict_playerChoice['votedMaps'] = {}
    dict_playerChoice['totalVotes'] = 0
    dict_playerChoice['winningMap'] = None
    dict_playerChoice['winningMapVotes'] = 0

def startVote():
    # Send the map vote to the players
    gungamelib.msg('gg_map_vote','#all', 'PlaceYourVotes')
    popuplib.send('voteMenu', es.getUseridList())
    
    # Play vote
    es.cexec_all('play admin_plugin/actions/startyourvoting.mp3')
    
    # Start the countdown
    dict_addonVars['voteTimer'] = int(dict_variables['voteTime'])
    repeat.create('voteCounter', VoteCountdown)
    repeat.start('voteCounter', 1, 0)
    
    # Bot vote code
    if int(es.ServerVar('gg_vote_bots_vote')):
        for userid in playerlib.getUseridList('#bot'):
            choice = random.choice(dict_addonVars['voteList'])
            time = random.randint(1, 5)
            gamethread.delayed(time, voteMenuSelect, (userid, choice, 0))
    
    # Set the active vars
    dict_addonVars['voteActive'] = 1
    gungamelib.setGlobal('voteActive', 1)

def VoteCountdown(repeatInfo):
    if dict_addonVars['voteTimer']:
        # Countdown 5 or less?
        if dict_addonVars['voteTimer'] <= 5:
            # Beep :)
            es.cexec_all('playgamesound hl1/fvox/beep.wav')
        
        # Get vote info
        voteInfo = str()
        for map in sorted(dict_playerChoice['votedMaps'].items(), key=itemgetter(1), reverse=True):
            voteInfo += '\n%s (%d votes)' % (map[0], map[1])
        
        # Send the HudHint
        if dict_addonVars['voteTimer'] == 1:
            gungamelib.hudhint('gg_map_vote', '#all', 'Countdown_Singular', {'voteInfo': voteInfo})
        else:
            gungamelib.hudhint('gg_map_vote', '#all', 'Countdown_Plural', {'time': dict_addonVars['voteTimer'], 'voteInfo': voteInfo})
    else:
        # Play beep sound
        es.cexec_all('playgamesound hl1/fvox/beep.wav')
        
        # Delete the repeat
        repeat.delete('voteCounter')
        
        # Get results
        voteResults()
    
    # Decrement timer
    dict_addonVars['voteTimer'] -= 1
    
def voteMenuSelect(userid, mapChoice, popupid):
    # Get index of userid
    index = playerlib.getPlayer(userid).attributes['index']
    
    # Loop through the map choices
    if mapChoice in dict_addonVars['voteList']:
        # Announce players choice if enabled
        if int(dict_variables['showVotes']):
            # Get player name
            name = es.getplayername(userid)
            
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
            
        # Increment total votes
        dict_playerChoice['totalVotes'] += 1

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
def cancelVote():
    if dict_addonVars['voteActive']:
        dict_addonVars['voteActive'] = 0
        repeat.delete('voteCounter')
        popuplib.unsendname('voteMenu', es.getUseridList())
        popuplib.delete('voteMenu')
        
        gungamelib.msg('gg_map_vote','#all', 'VoteCancelled')
    else:
        gungamelib.echo('gg_map_vote', 0, 0, 'NoVoteToCancel')

def getVoteList():
    if dict_addonVars['voteList'] != []:
        gungamelib.echo('gg_map_vote', 0, 0, 'ListOfMaps')
        msgFormat = str()
        
        # Get maps
        for map in dict_addonVars['voteList']:
            msgFormat += '%s ' % map
        
        es.dbgmsg(0, msgFormat)
    else:
        gungamelib.echo('gg_map_vote', 0, 0, 'VoteListEmpty')

def shuffleVoteList():
    if not dict_addonVars['voteActive']:
        setVoteList()
        gungamelib.echo('gg_map_vote', 0, 0, 'NewMapList')
        msgFormat = ''
        for map in dict_addonVars['voteList']:
            msgFormat = '%s%s ' % (msgFormat, map)
        es.dbgmsg(0, msgFormat)
    else:
        gungamelib.echo('gg_map_vote', 0, 0, 'VoteAlreadyInProgress')

def voteStart():
    if not dict_addonVars['voteActive']:
        if not popuplib.exists('voteMenu'):
            setVoteList()
        startVote()
    else:
        gungamelib.echo('gg_map_vote', 0, 0, 'VoteAlreadyInProgress')