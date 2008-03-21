'''
(c)2007 by the GunGame Coding Team

    Title:      gg_handicap
Version #:      1.0.158
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
info.version  = "1.0.158"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_handicap"
info.author   = "GunGame Development Team"

gg_handicap_update = gungamelib.getVariableValue('gg_handicap_update')

def load():
    # Register addon with gungamelib
    gg_handicap = gungamelib.registerAddon('gg_handicap')
    gg_handicap.setMenuText('GG Handicap')
    
    if gg_handicap_update:
        repeat.create('handicapUpdateLoop', handicapUpdate)
        repeat.start('handicapUpdateLoop', gg_handicap_update, 0)

def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_handicap')
    
    if gg_handicap_update:
        repeat.delete('handicapUpdateLoop')

def server_cvar(event_var):
    # register change in gg_handicap_update
    if event_var['cvarname'] == 'gg_handicap_update':
        gg_handicap_update = gungamelib.getVariableValue('gg_handicap_update')
        if gg_handicap_update:
            repeat.create('handicapUpdateLoop', handicapUpdate)
            repeat.start('handicapUpdateLoop', gg_handicap_update, 0)
        else:
            if repeat.status('handicapUpdateLoop'):
                repeat.delete('handicapUpdateLoop')

def es_map_start(event_var):
    if gg_handicap_update:
        repeat.create('handicapUpdateLoop', handicapUpdate)
        repeat.start('handicapUpdateLoop', gg_handicap_update, 0)

def player_activate(event_var):
    userid = int(event_var['userid'])
    averageLevel = gungamelib.getAverageLevel()
    gungamePlayer = gungamelib.getPlayer(userid)
    if gungamePlayer['level'] < averageLevel:
        gungamePlayer['level'] = averageLevel

def handicapUpdate(repeatInfo):
    averageLevel = gungamelib.getAverageLevel()
    allPlayers = playerlib.getUseridList("#all")
    for userid in allPlayers:
        gungamePlayer = gungamelib.getPlayer(userid)
        if gungamePlayer['level'] < averageLevel:
            gungamePlayer['level'] = averageLevel
            if gungamelib.getSound('handicap'):
                es.playsound(userid, gungamelib.getSound('handicap'), 1.0)
    
    gungamelib.msg('gg_handicap', userid, 'HandicapUpdate', {'level': averageLevel})