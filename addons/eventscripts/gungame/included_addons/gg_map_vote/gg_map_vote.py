'''
(c)2007 by the GunGame Coding Team

    Title:      gg_map_vote
Version #:      1.0.27
Description:    Adds map voting capabilities to gungame.
'''

import es
import os
import random
import popuplib
import usermsg
import repeat
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_map_vote Addon for GunGame: Python" 
info.version  = "1.0.27"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_map_vote" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2008, Saul"


# Dictionary of MapVote variables
dict_mapVoteVars = {}

# custom map list for the end map vote
dict_mapVoteVars['gg_map_list_file'] = gungame.getGunGameVar('gg_map_list_file')

# file to use for the map vote
dict_mapVoteVars['gg_map_list_source'] = int(gungame.getGunGameVar('gg_map_list_source'))

# number of maps in the end of map vote
dict_mapVoteVars['gg_map_vote_size'] = int(gungame.getGunGameVar('gg_map_vote_size'))

# number of recently played maps excluded from vote
dict_mapVoteVars['gg_dont_show_last_maps'] = int(gungame.getGunGameVar('gg_dont_show_last_maps'))

# the amount of time in seconds aloud for the vote
dict_mapVoteVars['gg_vote_time'] = int(gungame.getGunGameVar('gg_vote_time'))

# shows player name and vote selection in the player chat
dict_mapVoteVars['gg_show_player_vote'] = int(gungame.getGunGameVar('gg_show_player_vote'))

# dictionary for gg_map_list_source settings
# 1 = mapcycle.txt
# 2 = maplist.txt
# 3 = specified file
# 4 = cstrike/maps folder
dict_mapListFile = {}
dict_mapListFile[1] = '/cstrike/mapcycle.txt'
dict_mapListFile[2] = '/cstrike/maplist.txt'
dict_mapListFile[3] = dict_mapVoteVars['gg_map_list_file']

# list of recent maps - maps here are for testing only
list_recentMaps = []
# dictionary of Player Vote Choices
dict_playerChoice = {}
# list of potential vote maps
list_mapList = []
# list of Maps being voted for
list_voteList = []
# check to see if vote is active
voteActive = 0

def load():
    # register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_map_vote', 'gg_map_vote')

    # create commands
    if not es.exists('command','gg_vote_cancel'):
        es.regcmd('gg_vote_cancel','gungame/included_addons/gg_map_vote/CancelVote','Cancels an active map vote.')
    if not es.exists('command','gg_vote_list'):
        es.regcmd('gg_vote_list','gungame/included_addons/gg_map_vote/GetVoteList','Gets a list of maps in the upcoming vote.')
    if not es.exists('command','gg_vote_shuffle'):
        es.regcmd('gg_vote_shuffle','gungame/included_addons/gg_map_vote/ShuffleVoteList','Gets a new random set of maps for the upcoming vote.')
    if not es.exists('command','gg_vote_start'):
        es.regcmd('gg_vote_start','gungame/included_addons/gg_map_vote/VoteStart','Start a random map vote.')
        
    initiateVote()

def unload():
    # unregister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_map_vote')
    
    # delete popup
    if popuplib.exists('voteMenu'):
        popuplib.unsendname('voteMenu', es.getUseridList())
        popuplib.delete('voteMenu')
        
    #delete repeat
    if repeat.status('voteCounter'):
        repeat.delete('voteCounter')

def gg_variable_changed(event_var):
    global dict_mapVoteVars
    
    # watch for changes in map vote variables
    if dict_mapVoteVars.has_key(event_var['cvarname']):
        dict_mapVoteVars[event_var['cvarname']] = int(event_var['newvalue'])

def es_map_start(event_var):
    global dict_mapVoteVars
    global list_recentMaps
    
    # add current map to list of recent maps
    if dict_mapVoteVars['gg_dont_show_last_maps']:
        list_recentMaps.append(event_var['mapName'])
        # check size of recent map list
        if len(list_recentMaps) > dict_mapVoteVars['gg_dont_show_last_maps']:
            del list_recentMaps[0]

    # get vote ready
    if popuplib.exists('voteMenu'):
        repeat.delete('voteCounter')
        popuplib.unsendname('voteMenu', es.getUseridList())
        popuplib.delete('voteMenu')
    initiateVote()

# fires with event gg_vote
def gg_vote(event_var):
    global voteActive
    if not voteActive and popuplib.exists('voteMenu'):
        startVote()

# fires with event gg_win
def gg_win(event_var):
    global dict_playerChoice
    global voteActive
    if voteActive:
        repeat.delete('voteCounter')
        voteResults()
    winningMap = dict_playerChoice['winningMap']
    if winningMap != None:
        es.set('nextlevel', winningMap)
        es.msg('#multi', '\4GG Map Vote\1: Next map is \4%s\1' % winningMap)

def initiateVote():
    global dict_mapVoteVars
    global list_voteList
    global list_mapList
    
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
        list_mapList = list_mapDir
    else:
        # get list of maps from mapcycle.txt, maplist.txt or gg_maplist.txt
        list_mapList = []
        list_mapListFile = open(os.getcwd() + dict_mapListFile[dict_mapVoteVars['gg_map_list_source']], 'r')
        for line in list_mapListFile:
            line = line.strip()
            if not line.startswith('//') and line != '' and line in list_mapDir:
                list_mapList.append(line)
    
    # remove maps in the RecentMaps list
    for map in list_recentMaps:
        if map in list_mapList and len(list_mapList) > dict_mapVoteVars['gg_map_vote_size']:
            list_mapList.remove(map)
    setVoteList()

def setVoteList():
    global dict_mapVoteVars
    global list_mapList
    global list_voteList
    # set the size of the vote list
    mapsQuantity = len(list_mapList)
    if dict_mapVoteVars['gg_map_vote_size'] and mapsQuantity > dict_mapVoteVars['gg_map_vote_size']:
        list_voteList = random.sample(list_mapList, dict_mapVoteVars['gg_map_vote_size'])
    else:
        list_voteList = list_mapList
    
    # create the menu popup
    votePopup = popuplib.easymenu('voteMenu', '_popup_choice', voteMenuSelect)
    # set title for the menu
    votePopup.settitle('Next Map?')
    # loop threw maps to build list
    for map in list_voteList:
        votePopup.addoption(map, map)
        
    #reset Winning Map
    dict_playerChoice.clear()
    dict_playerChoice['votedMaps'] = {}
    dict_playerChoice['totalVotes'] = 0
    dict_playerChoice['winningMap'] = None
    dict_playerChoice['winningMapVotes'] = 0

def startVote():
    global dict_mapVoteVars
    global voteActive
    global voteTimer
    
    # send the map vote to the players
    es.msg('#multi', '\4GG Map Vote\1: Place your votes for the nextmap.')
    popuplib.send('voteMenu', es.getUseridList())
    es.cexec_all('play admin_plugin/actions/startyourvoting.mp3')
    
    voteTimer = dict_mapVoteVars['gg_vote_time']
    repeat.create('voteCounter', VoteCountdown)
    repeat.start('voteCounter', 1, 0)
    voteActive = 1

def VoteCountdown(repeatInfo):
    global dict_playerChoice
    global voteTimer
    
    if voteTimer:
        hudhintText = 'Time Remaining: %d' % voteTimer
        for map in dict_playerChoice['votedMaps']:
            hudhintText += '\n%s (%d votes)' % (hudhintText, map, dict_playerChoice['votedMaps'][map])
        for userid in es.getUseridList():
            usermsg.hudhint(userid, hudhintText)
    else:
        voteResults()
        repeat.delete('voteCounter')
        
    # Decrement timer
    voteTimer -= 1
    
    
def voteMenuSelect(userid, mapChoice, popupid):
    global dict_playerChoice
    global list_voteList
    global dict_mapVoteVars
    if mapChoice in list_voteList:
        # announce players choice if enabled
        if dict_mapVoteVars['gg_show_player_vote']:
            name = es.getplayername(userid)
            es.msg('\3', '%s voted %s' % (name, mapChoice))
        # register votes
        if mapChoice not in dict_playerChoice['votedMaps']:
            dict_playerChoice['votedMaps'][mapChoice] = 1
        else:
            dict_playerChoice['votedMaps'][mapChoice] += 1
        if dict_playerChoice['votedMaps'][mapChoice] > dict_playerChoice['winningMapVotes']:
            dict_playerChoice['winningMap'] = mapChoice
            dict_playerChoice['winningMapVotes'] = dict_playerChoice['votedMaps'][mapChoice]
        dict_playerChoice['totalVotes'] += 1

def voteResults():
    global dict_playerChoice
    global list_voteList
    global voteActive
    voteActive = 0
    list_voteList = []
    
    # Close and delete popup
    popuplib.unsendname('voteMenu', es.getUseridList())
    popuplib.delete('voteMenu')
    
    # Announce winning map
    if dict_playerChoice['totalVotes']:
        es.msg('#multi', '\4GG Map Vote\1: \4%s\1 won with \4%d\1 votes. \4%d\1 votes were cast.' % (dict_playerChoice['winningMap'], dict_playerChoice['winningMapVotes'], dict_playerChoice['totalVotes']))
        
        for userid in es.getUseridList():
            usermsg.hudhint(userid, 'Nextmap:\n%s' %dict_playerChoice['winningMap'])
    else:
        es.msg('#multi', '\4GG Map Vote\1: The vote was cancelled. No votes were cast.')
        for userid in es.getUseridList():
            usermsg.hudhint(userid, 'Not enough votes')

    es.cexec_all('play admin_plugin/actions/endofvote.mp3')

# console command gg_vote_cancel
def CancelVote():
    global voteActive
    if voteActive:
        voteActive = 0
        repeat.delete('voteCounter')
        popuplib.unsendname('voteMenu', es.getUseridList())
        popuplib.delete('voteMenu')
        es.msg('#multi', '\4GG Map Vote\1: Vote has been cancelled.')
    else:
        es.msg('#multi', '\4GG Map Vote\1: No active vote to cancel.')

# console command gg_vote_list
def GetVoteList():
    global list_voteList
    if list_voteList != []:
        es.msg('#multi', '\4GG Map Vote\1: List of maps in the next vote...')
        msgFormat = ''
        for map in list_voteList:
            msgFormat = '%s%s ' % (msgFormat, map)
        es.msg('\3', msgFormat)
    else:
        es.msg('#multi', '\4GG Map Vote\1: The vote list is empty.')

# console command gg_vote_shuffle
def ShuffleVoteList():
    global list_voteList
    global voteActive
    if not voteActive:
        setVoteList()
        es.msg('#multi', '\4GG Map Vote\1: New shuffled map list!')
        msgFormat = ''
        for map in list_voteList:
            msgFormat = '%s%s ' % (msgFormat, map)
        es.msg('\3', msgFormat)
    else:
        es.msg('#multi', '\4GG Map Vote\1: Vote already in progress!')

# console command gg_vote_start
def VoteStart():
    global voteActive
    if not voteActive:
        if not popuplib.exists('voteMenu'):
            setVoteList()
        startVote()
    else:
        es.msg('#multi', '\4GG Map Vote\1: Vote already in progress!')