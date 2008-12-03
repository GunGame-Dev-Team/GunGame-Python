''' (c) 2008 by the GunGame Coding Team

    Title: gg_handicap
    Version: 5.0.561
    Description:
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# Python imports
import os

# EventScripts imports
import es
import testrepeat as repeat
import playerlib
import gamethread

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_handicap (for GunGame5)'
info.version  = '5.0.561'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_handicap'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
handicapType = gungamelib.getVariable('gg_handicap')
updateTime = gungamelib.getVariable('gg_handicap_update')
gg_turbo = gungamelib.getVariable('gg_turbo')

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_handicap = gungamelib.registerAddon('gg_handicap')
    gg_handicap.setDisplayName('GG Handicap')
    gg_handicap.loadTranslationFile()
    
    # Start loop
    repeat.create('gungameHandicapLoop', handicapUpdate)
    repeat.start('gungameHandicapLoop', updateTime, 0)

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_handicap')
    
    # Stop loop
    if repeat.status('gungameHandicapLoop'):
        repeat.delete('gungameHandicapLoop')


def es_map_start(event_var):
    # Start loop
    repeat.create('gungameHandicapLoop', handicapUpdate)
    repeat.start('gungameHandicapLoop', updateTime, 0)

def player_activate(event_var):
    # Get vars
    userid = int(event_var['userid'])
    # Set handicap type
    if handicapType == 1:
        handicapLevel = gungamelib.getLowestLevel(userid)
        handicapMethod = 'LevelLowest'
    elif handicapType == 2:
        handicapLevel = gungamelib.getMedianLevel(userid)
        handicapMethod = 'LevelMedian'
    elif handicapType == 3:
        handicapLevel = gungamelib.getAverageLevel(userid)
        handicapMethod = 'LevelAveraged'
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Level below handicap?
    if gungamePlayer['level'] < handicapLevel:
        gungamePlayer['level'] = handicapLevel
        gungamelib.msg('gg_handicap', userid, handicapMethod, {'level': handicapLevel})

def handicapUpdate():
    if not int(updateTime):
        return
    
    # Set handicap type
    if handicapType == 1:
        handicapLevel = gungamelib.getAboveLowestLevel()
        handicapMethod = 'LevelLowest'
    elif handicapType == 2:
        handicapLevel = gungamelib.getMedianLevel()
        handicapMethod = 'LevelMedian'
    elif handicapType == 3:
        handicapLevel = gungamelib.getAverageLevel()
        handicapMethod = 'LevelAveraged'
    
    if handicapType == 1:
        # Loop through players
        for userid in gungamelib.getLevelUseridList(gungamelib.getLowestLevel()):
            # Get gungame player object
            gungamePlayer = gungamelib.getPlayer(userid)
            
            # Level them up
            gungamePlayer['level'] = handicapLevel
            if gg_turbo:
                giveNewWeapon(userid)
            
            # Play sound and tell them
            gungamelib.playSound(userid, 'handicap')
            gungamelib.msg('gg_handicap', userid, handicapMethod, {'level': handicapLevel})
        return
    
    # Loop through players
    for gungamePlayer in gungamelib.getPlayerList():
        userid = gungamePlayer['userid']
        
        # Is level below average?
        if gungamePlayer['level'] >= handicapLevel:
            continue
        
        # Level them up
        gungamePlayer['level'] = handicapLevel
        if gg_turbo:
            giveNewWeapon(userid)
        
        # Play sound and tell them
        gungamelib.playSound(userid, 'handicap')
        gungamelib.msg('gg_handicap', userid, handicapMethod, {'level': handicapLevel})

def giveNewWeapon(userid):
    userid = int(userid)
    gungamePlayer = gungamelib.getPlayer(userid)
    
    if gungamelib.isDead(userid):
        return
        
    if gungamelib.isSpectator(userid):
        return
    
    gungamePlayer.stripPlayer()
    
    # Only delay if we are on linux
    if gungamelib.getOS() == 'posix':
        gamethread.delayed(0, delayedGiveNewWeapon, (userid))
    else:
        gungamePlayer.giveWeapon()

def delayedGiveNewWeapon(userid):
    if gungamelib.isDead(userid):
        return
    
    if gungamelib.isSpectator(userid):
        return
    
    gungamePlayer = gungamelib.getPlayer(userid)
    gungamePlayer.giveWeapon()