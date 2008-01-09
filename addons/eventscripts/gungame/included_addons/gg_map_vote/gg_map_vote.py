'''
(c)2007 by the GunGame Coding Team

    Title:      gg_map_vote
Version #:      09.01.08
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
info.version  = "09.01.08"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_map_vote" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2008, Saul"

# custom map list for the end map vote
gg_map_list_file = gungame.getGunGameVar('gg_map_list_file')

# file to use for the map vote
gg_map_list_source = int(gungame.getGunGameVar('gg_map_list_source'))

# number of maps in the end of map vote
gg_map_vote_size = int(gungame.getGunGameVar('gg_map_vote_size'))

# number of recently played maps excluded from vote
gg_dont_show_last_maps = int(gungame.getGunGameVar('gg_dont_show_last_maps'))

# the amount of time in seconds aloud for the vote
gg_vote_time = int(gungame.getGunGameVar('gg_vote_time'))

# shows player name and vote selection in the player chat
gg_show_player_vote = int(gungame.getGunGameVar('gg_show_player_vote'))

# dictionary for gg_map_list_source settings
# 1 = mapcycle.txt
# 2 = maplist.txt
# 3 = specified file
# 4 = cstrike/maps folder
dict_MapListFile = {}
dict_MapListFile[1] = '/cstrike/mapcycle.txt'
dict_MapListFile[2] = '/cstrike/maplist.txt'
dict_MapListFile[3] = gg_map_list_file

# list of recent maps - maps here are for testing only
list_RecentMaps = []
# dictionary of Player Vote Choices
dict_PlayerChoice = {}
# list of potential vote maps
list_MapList = []
# list of Maps being voted for
list_VoteList = []
# check to see if vote is active
VoteActive = 0

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
        
    InitiateVote()

def unload():
    # unregister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_map_vote')
    
    # delete popup
    if popuplib.exists('VoteMenu'):
        popuplib.unsendname('VoteMenu', es.getUseridList())
        popuplib.delete('VoteMenu')
        
    #delete repeat
    if repeat.status('VoteCounter'):
        repeat.delete('VoteCounter')

def gg_variable_changed(event_var):
    # register change in gg_map_list_file
    if event_var['cvarname'] == 'gg_map_list_file':
        global gg_map_list_file
        gg_map_list_file = int(gungame.getGunGameVar('gg_map_list_file'))
    # register change in gg_map_list_source
    if event_var['cvarname'] == 'gg_map_list_source':
        global gg_map_list_source
        gg_map_list_source = int(gungame.getGunGameVar('gg_map_list_source'))
    # register change in gg_map_vote_size
    if event_var['cvarname'] == 'gg_map_vote_size':
        global gg_map_vote_size
        gg_map_vote_size = int(gungame.getGunGameVar('gg_map_vote_size'))
    # register change in gg_dont_show_last_maps
    if event_var['cvarname'] == 'gg_dont_show_last_maps':
        global gg_dont_show_last_maps
        gg_dont_show_last_maps = int(gungame.getGunGameVar('gg_dont_show_last_maps'))
    # register change in gg_vote_time
    if event_var['cvarname'] == 'gg_vote_time':
        global gg_vote_time
        gg_vote_time = int(gungame.getGunGameVar('gg_vote_time'))
    # register change in gg_show_player_vote
    if event_var['cvarname'] == 'gg_show_player_vote':
        global gg_show_player_vote
        gg_show_player_vote = int(gungame.getGunGameVar('gg_show_player_vote'))

def es_map_start(event_var):
    global gg_dont_show_last_maps
    global list_RecentMaps
    
    # add current map to list of recent maps
    if gg_dont_show_last_maps:
        list_RecentMaps.append(event_var['mapname'])
        # check size of recent map list
        if len(list_RecentMaps) > gg_dont_show_last_maps:
            del list_RecentMaps[0]

    # get vote ready
    if popuplib.exists('VoteMenu'):
        repeat.delete('VoteCounter')
        popuplib.unsendname('VoteMenu', es.getUseridList())
        popuplib.delete('VoteMenu')
    InitiateVote()

# fires with event gg_vote
def gg_vote(event_var):
    global VoteActive
    if not VoteActive and popuplib.exists('VoteMenu'):
        StartVote()

# fires with event gg_win
def gg_win(event_var):
    global dict_PlayerChoice
    global VoteActive
    if VoteActive:
        repeat.delete('VoteCounter')
        VoteResults()
    winningMap = dict_PlayerChoice['WinningMap']
    if winningMap != None:
        es.set('nextlevel', winningMap)
        es.msg('#multi', '\4GG Map Vote\1: Next map is \4%s\1' % winningMap)

def InitiateVote():
    global gg_map_list_source
    global gg_map_vote_size
    global list_VoteList
    global list_MapList
    
    # get list of maps from cstrike/maps
    list_MapDir = []
    MapsDir = os.listdir(os.getcwd() + '/cstrike/maps/')
    for map in MapsDir:
        (MapName, Extension) = os.path.splitext(map)
        if Extension == '.bsp':
            list_MapDir.append(MapName)

    # create a of maps for voting
    if gg_map_list_source == 4:
        # get list of maps from /cstrike/maps
        list_MapList = list_MapDir
    else:
        # get list of maps from mapcycle.txt, maplist.txt or gg_maplist.txt
        list_MapList = []
        list_MapListFile = open(os.getcwd() + dict_MapListFile[gg_map_list_source], 'r')
        for line in list_MapListFile:
            line = line.strip()
            if not line.startswith('//') and line != '' and line in list_MapDir:
                list_MapList.append(line)
    
    # remove maps in the RecentMaps list
    for map in list_RecentMaps:
        if map in list_MapList and len(list_MapList) > gg_map_vote_size:
            list_MapList.remove(map)
    SetVoteList()

def SetVoteList():
    global gg_map_vote_size
    global list_MapList
    global list_VoteList
    # set the size of the vote list
    MapsQty = len(list_MapList)
    if gg_map_vote_size and MapsQty > gg_map_vote_size:
        list_VoteList = random.sample(list_MapList, gg_map_vote_size)
    else:
        list_VoteList = list_MapList
    
    # create the menu popup
    VotePopup = popuplib.easymenu('VoteMenu', '_popup_choice', VoteMenuSelect)
    # set title for the menu
    VotePopup.settitle('Next Map?')
    # loop threw maps to build list
    for map in list_VoteList:
        VotePopup.addoption(map, map)
        
    #reset Winning Map
    dict_PlayerChoice.clear()
    dict_PlayerChoice['VotedMaps'] = {}
    dict_PlayerChoice['TotalVotes'] = 0
    dict_PlayerChoice['WinningMap'] = None
    dict_PlayerChoice['WinningMapVotes'] = 0

def StartVote():
    global gg_vote_time
    global VoteActive
    global VoteTimer
    
    # send the map vote to the players
    es.msg('#multi', '\4GG Map Vote\1: Place your votes for the nextmap.')
    popuplib.send('VoteMenu', es.getUseridList())
    es.cexec_all('play admin_plugin/actions/startyourvoting.mp3')
    
    VoteTimer = gg_vote_time
    repeat.create('VoteCounter', VoteCountdown)
    repeat.start('VoteCounter', 1, 0)
    VoteActive = 1

def VoteCountdown(repeatInfo):
    global dict_PlayerChoice
    global VoteTimer
    
    if VoteTimer:
        HudhintText = 'Time Remaining: %d' % VoteTimer
        for map in dict_PlayerChoice['VotedMaps']:
            HudhintText += '\n%s (%d votes)' % (HudhintText, map, dict_PlayerChoice['VotedMaps'][map])
        for userid in es.getUseridList():
            usermsg.hudhint(userid, HudhintText)
    else:
        VoteResults()
        repeat.delete('VoteCounter')
        
    # Decrement timer
    VoteTimer -= 1
    
    
def VoteMenuSelect(userid, MapChoice, popupid):
    global dict_PlayerChoice
    global list_VoteList
    global gg_show_player_vote
    if MapChoice in list_VoteList:
        # announce players choice if enabled
        if gg_show_player_vote:
            Name = es.getplayername(userid)
            es.msg('\3', '%s voted %s' % (Name, MapChoice))
        # register votes
        if MapChoice not in dict_PlayerChoice['VotedMaps']:
            dict_PlayerChoice['VotedMaps'][MapChoice] = 1
        else:
            dict_PlayerChoice['VotedMaps'][MapChoice] += 1
        if dict_PlayerChoice['VotedMaps'][MapChoice] > dict_PlayerChoice['WinningMapVotes']:
            dict_PlayerChoice['WinningMap'] = MapChoice
            dict_PlayerChoice['WinningMapVotes'] = dict_PlayerChoice['VotedMaps'][MapChoice]
        dict_PlayerChoice['TotalVotes'] += 1

def VoteResults():
    global dict_PlayerChoice
    global list_VoteList
    global VoteActive
    VoteActive = 0
    list_VoteList = []
    
    # Close and delete popup
    popuplib.unsendname('VoteMenu', es.getUseridList())
    popuplib.delete('VoteMenu')
    
    # Announce winning map
    if dict_PlayerChoice['TotalVotes']:
        es.msg('#multi', '\4GG Map Vote\1: \4%s\1 won with \4%d\1 votes. \4%d\1 votes were cast.' % (dict_PlayerChoice['WinningMap'], dict_PlayerChoice['WinningMapVotes'], dict_PlayerChoice['TotalVotes']))
        
        for userid in es.getUseridList():
            usermsg.hudhint(userid, 'Nextmap:\n%s' %dict_PlayerChoice['WinningMap'])
    else:
        es.msg('#multi', '\4GG Map Vote\1: The vote was cancelled. No votes were cast.')
        for userid in es.getUseridList():
            usermsg.hudhint(userid, 'Not enough votes')

    es.cexec_all('play admin_plugin/actions/endofvote.mp3')

# console command gg_vote_cancel
def CancelVote():
    global VoteActive
    if VoteActive:
        VoteActive = 0
        repeat.delete('VoteCounter')
        popuplib.unsendname('VoteMenu', es.getUseridList())
        popuplib.delete('VoteMenu')
        es.msg('#multi', '\4GG Map Vote\1: Vote has been cancelled.')
    else:
        es.msg('#multi', '\4GG Map Vote\1: No active vote to cancel.')

# console command gg_vote_list
def GetVoteList():
    global list_VoteList
    if list_VoteList != []:
        es.msg('#multi', '\4GG Map Vote\1: List of maps in the next vote...')
        msgFormat = ''
        for map in list_VoteList:
            msgFormat = '%s%s ' % (msgFormat, map)
        es.msg('\3', msgFormat)
    else:
        es.msg('#multi', '\4GG Map Vote\1: The vote list is empty.')

# console command gg_vote_shuffle
def ShuffleVoteList():
    global list_VoteList
    global VoteActive
    if not VoteActive:
        SetVoteList()
        es.msg('#multi', '\4GG Map Vote\1: New shuffled map list!')
        msgFormat = ''
        for map in list_VoteList:
            msgFormat = '%s%s ' % (msgFormat, map)
        es.msg('\3', msgFormat)
    else:
        es.msg('#multi', '\4GG Map Vote\1: Vote already in progress!')

# console command gg_vote_start
def VoteStart():
    global VoteActive
    if not VoteActive:
        if not popuplib.exists('VoteMenu'):
            SetVoteList()
        StartVote()
    else:
        es.msg('#multi', '\4GG Map Vote\1: Vote already in progress!')