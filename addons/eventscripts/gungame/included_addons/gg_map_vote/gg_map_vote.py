'''
(c)2007 by the GunGame Coding Team

    Title:      gg_map_vote
Version #:      1.0.203
Description:    Adds map voting capabilities to gungame.
'''

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

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_map_vote Addon for GunGame: Python"
info.version  = "1.0.203"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_map_vote"
info.author   = "GunGame Development Team"

# Dictionary of MapVote variables
dict_mapVoteVars = {}

# custom map list for the end map vote
dict_mapVoteVars['gg_map_list_file'] = gungamelib.getVariableValue('gg_map_list_file')
# file to use for the map vote
dict_mapVoteVars['gg_map_list_source'] = gungamelib.getVariableValue('gg_map_list_source')
# number of maps in the end of map vote
dict_mapVoteVars['gg_map_vote_size'] = gungamelib.getVariableValue('gg_map_vote_size')
# number of recently played maps excluded from vote
dict_mapVoteVars['gg_dont_show_last_maps'] = gungamelib.getVariableValue('gg_dont_show_last_maps')
# the amount of time in seconds aloud for the vote
dict_mapVoteVars['gg_vote_time'] = gungamelib.getVariableValue('gg_vote_time')
# shows player name and vote selection in the player chat
dict_mapVoteVars['gg_show_player_vote'] = gungamelib.getVariableValue('gg_show_player_vote')

# dictionary for gg_map_list_source settings
# 1 = mapcycle.txt
# 2 = maplist.txt
# 3 = specified file
# 4 = cstrike/maps folder
dict_mapListFile = {}
dict_mapListFile[1] = '/cstrike/mapcycle.txt'
dict_mapListFile[2] = '/cstrike/maplist.txt'
dict_mapListFile[3] = dict_mapVoteVars['gg_map_list_file']

# dictionary of Player Vote Choices
dict_playerChoice = {}

dict_addonVars = {}
# list of recent maps - maps here are for testing only
dict_addonVars['recentMaps'] = []
# list of potential vote maps
dict_addonVars['mapList'] = []
# list of Maps being voted for
dict_addonVars['voteList'] = []
# check to see if vote is active
dict_addonVars['voteActive'] = 0
# stores the value of the vote timer
dict_addonVars['voteTimer'] = 0


# get old eventscripts_maphandler value
oldEventscriptsMaphandler = es.ServerVar('eventscripts_maphandler')
es.ServerVar('eventscripts_maphandler').set(1)

def load():
    # Register addon with gungamelib
    gg_map_vote = gungamelib.registerAddon('gg_map_vote')
    gg_map_vote.setMenuText('GG Map Vote')

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
    # add current map to list of recent maps
    if dict_mapVoteVars['gg_dont_show_last_maps']:
        dict_addonVars['recentMaps'].append(event_var['mapName'])
        # check size of recent map list
        if len(dict_addonVars['recentMaps']) > dict_mapVoteVars['gg_dont_show_last_maps']:
            del dict_addonVars['recentMaps'][0]
            
    # delete popup
    if popuplib.exists('voteMenu'):
        popuplib.unsendname('voteMenu', es.getUseridList())
        popuplib.delete('voteMenu')
        
    #delete repeat
    if repeat.status('voteCounter'):
        repeat.delete('voteCounter')
        
    # get vote ready
    initiateVote()

# fires with event gg_vote
def gg_vote(event_var):
    if not dict_addonVars['voteActive'] and popuplib.exists('voteMenu'):
        startVote()

# fires with event gg_win
def gg_win(event_var):
    if dict_addonVars['voteActive']:
        repeat.delete('voteCounter')
        voteResults()
    winningMap = dict_playerChoice['winningMap']
    if winningMap != None:
        es.set('nextlevel', winningMap)
        gungamelib.msg('gg_map_vote','#all', 'Nextmap', {'map': winningMap})

def initiateVote():
    # get list of maps from cstrike/maps
    list_mapDir = []
    mapsDir = os.listdir(os.getcwd() + '/cstrike/maps/')
    for map in mapsDir:
        (mapName, extension) = os.path.splitext(map)
        if extension == '.bsp':
            list_mapDir.append(mapName)

    # create a of maps for voting
    if dict_mapVoteVars['gg_map_list_source'] == 4:
        # get list of maps from /cstrike/maps
        dict_addonVars['mapList'] = list_mapDir
    else:
        # get list of maps from mapcycle.txt, maplist.txt or gg_maplist.txt
        dict_addonVars['mapList'] = []
        list_mapListFile = open(os.getcwd() + dict_mapListFile[dict_mapVoteVars['gg_map_list_source']], 'r')
        for line in list_mapListFile:
            line = line.strip()
            if not line.startswith('//') and line != '' and line in list_mapDir:
                dict_addonVars['mapList'].append(line)
    
    # remove maps in the RecentMaps list
    for map in dict_addonVars['recentMaps']:
        if map in dict_addonVars['mapList'] and len(dict_addonVars['mapList']) > dict_mapVoteVars['gg_map_vote_size']:
            dict_addonVars['mapList'].remove(map)
    setVoteList()

def setVoteList():
    # Set the size of the vote list
    mapsQuantity = len(dict_addonVars['mapList'])
    if dict_mapVoteVars['gg_map_vote_size'] and mapsQuantity > dict_mapVoteVars['gg_map_vote_size']:
        dict_addonVars['voteList'] = random.sample(dict_addonVars['mapList'], dict_mapVoteVars['gg_map_vote_size'])
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
    dict_addonVars['voteTimer'] = dict_mapVoteVars['gg_vote_time']
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
        if dict_mapVoteVars['gg_show_player_vote']:
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

# console command gg_vote_cancel
def cancelVote():
    if dict_addonVars['voteActive']:
        dict_addonVars['voteActive'] = 0
        repeat.delete('voteCounter')
        popuplib.unsendname('voteMenu', es.getUseridList())
        popuplib.delete('voteMenu')
        
        gungamelib.msg('gg_map_vote','#all', 'VoteCancelled')
    else:
        gungamelib.echo('gg_map_vote', 0, 0, 'NoVoteToCancel')

# console command gg_vote_list
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

# console command gg_vote_shuffle
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

# console command gg_vote_start
def voteStart():
    if not dict_addonVars['voteActive']:
        if not popuplib.exists('voteMenu'):
            setVoteList()
        startVote()
    else:
        gungamelib.echo('gg_map_vote', 0, 0, 'VoteAlreadyInProgress')