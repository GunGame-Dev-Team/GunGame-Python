'''
(c)2007 by the GunGame Coding Team

    Title:      gg_handicap
Version #:      1.0.175
Description:    When a player joins they are given the average level.
'''

# EventScripts imports
import es
import repeat
import playerlib

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_handicap Addon for GunGame: Python"
info.version  = "1.0.175"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_handicap"
info.author   = "GunGame Development Team"

gg_handicap_update = gungamelib.getVariableValue('gg_handicap_update')

def load():
    # Register addon with gungamelib
    gg_handicap = gungamelib.registerAddon('gg_handicap')
    gg_handicap.setMenuText('GG Handicap')
    
    # Start loop
    repeat.create('HandicapLoop', handicapUpdate)
    repeat.start('HandicapLoop', 120, 0)

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_handicap')
    
    # Stop loop
    if repeat.status('HandicapLoop'):
        repeat.delete('HandicapLoop')

def server_cvar(event_var):
    # New value must be numeric
    if not gungamelib.isNumeric(event_var['cvarValue']):
        return
    
    # Get vars
    newValue = int(event_var['cvarvalue'])
    var = event_var['cvarname']
    
    if var == 'gg_handicap_update':
        if newValue == 1:
            gg_handicap_update = 1
        else:
            gg_handicap_update = 0

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
    if not gg_handicap_update:
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
            
            # Play sound
            if gungamelib.getSound('handicap'):
                es.playsound(userid, gungamelib.getSound('handicap'), 1.0)
            
            # Tell them
            gungamelib.msg('gg_handicap', userid, 'LevelAveraged', {'level': averageLevel})