''' (c) 2008 by the GunGame Coding Team

    Title: gg_handicap
    Version: 1.0.293
    Description:
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# Python imports
import os

# EventScripts imports
import es
import repeat
import playerlib
import gamethread

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_handicap (for GunGame: Python)'
info.version  = '1.0.293'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_handicap'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
updateType = gungamelib.getVariable('gg_handicap_update')

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_handicap = gungamelib.registerAddon('gg_handicap')
    gg_handicap.setDisplayName('GG Handicap')
    
    # Start loop
    repeat.create('HandicapLoop', handicapUpdate)
    repeat.start('HandicapLoop', 120, 0)

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_handicap')
    
    # Stop loop
    if repeat.status('HandicapLoop'):
        repeat.delete('HandicapLoop')

def es_map_start(event_var):
    # Start loop
    repeat.create('HandicapLoop', handicapUpdate)
    repeat.start('HandicapLoop', 120, 0)

def player_activate(event_var):
    # Get vars
    userid = int(event_var['userid'])
    averageLevel = gungamelib.getAverageLevel()
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Level below average?
    if gungamePlayer['level'] < averageLevel:
        gungamePlayer['level'] = averageLevel
        gungamelib.msg('gg_handicap', userid, 'LevelAveraged', {'level': averageLevel})

def handicapUpdate(repeatInfo):
    if not int(updateType):
        return
    
    # Get average level
    averageLevel = gungamelib.getAverageLevel()
    
    # Loop throughp players
    for userid in playerlib.getUseridList('#all'):
        # Get player object
        gungamePlayer = gungamelib.getPlayer(userid)
        
        # Is level below average?
        if gungamePlayer['level'] < averageLevel:
            # Set their level
            gungamePlayer['level'] = averageLevel
            
            # Give new weapon if turbo mode is on
            if gungamelib.getVariableValue('gg_turbo'):
                if gungamePlayer.getWeapon() == 'knife':
                    es.sexec(userid, 'use weapon_knife')
                if not gungamelib.isDead(userid):
                    gungamePlayer.stripPlayer()
                    
                    # Only delay if we are on linux
                    if os.name == 'posix':
                        gamethread.delayed(0.01, gungamePlayer.giveWeapon, ())
                    else:
                        gungamePlayer.giveWeapon()
            
            # Play sound
            if gungamelib.getSound('handicap'):
                es.playsound(userid, gungamelib.getSound('handicap'), 1.0)
            
            # Tell them
            gungamelib.msg('gg_handicap', userid, 'LevelAveraged', {'level': averageLevel})