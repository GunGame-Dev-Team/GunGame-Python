''' (c) 2008 by the GunGame Coding Team

    Title: gg_handicap
    Version: 5.0.541
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
info.version  = '5.0.541'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_handicap'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
updateType = gungamelib.getVariable('gg_handicap_update')
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
    repeat.start('gungameHandicapLoop', 120, 0)

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_handicap')
    
    # Stop loop
    if repeat.status('gungameHandicapLoop'):
        repeat.delete('gungameHandicapLoop')


def es_map_start(event_var):
    # Start loop
    repeat.create('gungameHandicapLoop', handicapUpdate)
    repeat.start('gungameHandicapLoop', 120, 0)

def player_activate(event_var):
    # Get vars
    userid = int(event_var['userid'])
    averageLevel = gungamelib.getAverageLevel(userid)
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Level below average?
    if gungamePlayer['level'] < averageLevel:
        gungamePlayer['level'] = averageLevel
        gungamelib.msg('gg_handicap', userid, 'LevelAveraged', {'level': averageLevel})

def handicapUpdate():
    if not int(updateType):
        return
    
    # Get average level
    averageLevel = gungamelib.getAverageLevel()
    
    # Loop throughp players
    for userid in playerlib.getUseridList('#all'):
        # Get player object
        gungamePlayer = gungamelib.getPlayer(userid)
        
        # Is level below average?
        if gungamePlayer['level'] >= averageLevel:
            continue
        
        # Level them up
        gungamePlayer['level'] = averageLevel
        if gg_turbo:
            giveNewWeapon(userid)
        
        # Play sound and tell them
        gungamelib.playSound(userid, 'handicap')
        gungamelib.msg('gg_handicap', userid, 'LevelAveraged', {'level': averageLevel})

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