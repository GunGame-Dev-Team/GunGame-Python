'''
(c)2007 by the GunGame Coding Team

    Title:      gg_handicap
Version #:      12.16.2007
Description:    When a player joins they are given the average level.
'''

import es
from gungame import gungame
import repeat
import playerlib

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_handicap Addon for GunGame: Python" 
info.version  = "12.16.2007"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_handicap" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007"

gg_handicap_update = int(gungame.getGunGameVar('gg_handicap_update'))

def load():
    global gg_handicap_update
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_handicap', 'GG Handicap')
    if gg_handicap_update:
        repeat.create('handicapUpdateLoop', handicapUpdate)
        repeat.start('handicapUpdateLoop', gg_handicap_update, 0)

def unload():
    global gg_handicap_update
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_handicap')
    if gg_handicap_update:
        repeat.delete('handicapUpdateLoop')

def gg_variable_changed(event_var):
    # register change in gg_handicap_update
    if event_var['cvarname'] == 'gg_handicap_update':
        global gg_handicap_update
        gg_handicap_update = int(gungame.getGunGameVar('gg_handicap_update'))
        if gg_handicap_update:
            repeat.create('handicapUpdateLoop', handicapUpdate)
            repeat.start('handicapUpdateLoop', gg_handicap_update, 0)
        else:
            if repeat.status('handicapUpdateLoop'):
                repeat.delete('handicapUpdateLoop')

def es_map_start(event_var):
    global gg_handicap_update
    if gg_handicap_update:
        repeat.create('handicapUpdateLoop', handicapUpdate)
        repeat.start('handicapUpdateLoop', gg_handicap_update, 0)

def player_activate(event_var):
    userid = int(event_var['userid'])
    averageLevel = gungame.getAverageLevel()
    gungamePlayer = gungame.getPlayer(userid)
    if gungamePlayer.get('level') < averageLevel:
        gungamePlayer.set('level', averageLevel)
        if int(es.getplayerteam(userid)) > 1:
            gungame.stripPlayer(userid)
            gungame.giveWeapon(userid)

def handicapUpdate(repeatInfo):
    averageLevel = gungame.getAverageLevel()
    allPlayers = playerlib.getUseridList("#all")
    for userid in allPlayers:
        gungamePlayer = gungame.getPlayer(str(userid))
        if gungamePlayer.get('level') < averageLevel:
            gungamePlayer.set('level', averageLevel)
    
    announce('All players are now level \4%d\1 or higher.' % averageLevel)
    
def announce(message):
    es.msg('#multi', '\4[GG:Handicap]\1 %s' % message)
   
def tell(userid, message):
    es.tell(userid, '#multi', '\4[GG:Handicap]\1 %s' % message)

def echo(message):
    es.dbgmsg(0, '[GG:Handicap] %s' % message)