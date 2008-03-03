'''
(c)2007 by the GunGame Coding Team

    Title:      gg_handicap
Version #:      1.0.111
Description:    When a player joins they are given the average level.
'''

import es
import gungamelib
import repeat
import playerlib

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_handicap Addon for GunGame: Python" 
info.version  = "1.0.111"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_handicap" 
info.author   = "GunGame Development Team"

gg_handicap_update = int(gungamelib.getVariableValue('gg_handicap_update'))

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
        gg_handicap_update = int(gungamelib.getVariableValue('gg_handicap_update'))
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
        if int(es.getplayerteam(userid)) > 1:
            gungamePlayer.stripPlayer()
            gungamePlayer.giveWeapon()

def handicapUpdate(repeatInfo):
    averageLevel = gungamelib.getAverageLevel()
    allPlayers = playerlib.getUseridList("#all")
    for userid in allPlayers:
        gungamePlayer = gungamelib.getPlayer(userid)
        if gungamePlayer['level'] < averageLevel:
            gungamePlayer['level'] = averageLevel
            es.playsound(userid, gungamelib.getSound('handicap'), 1.0)
    
    announce('All players are now level \4%d\1 or higher.' % averageLevel)
    
def announce(message):
    es.msg('#multi', '\4[GG:Handicap]\1 %s' % message)
   
def tell(userid, message):
    es.tell(userid, '#multi', '\4[GG:Handicap]\1 %s' % message)

def echo(message):
    es.dbgmsg(0, '[GG:Handicap] %s' % message)