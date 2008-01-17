'''
(c)2008 by the GunGame Coding Team

    Title:      gg_triple_level
Version #:      1.12.2008
Description:    When a player makes 3 levels in one round he get faster and have an effect for 10 secs
'''

import es, playerlib, gamethread
from gungame import gungame
from gungame.included_addons.gg_sounds import gg_sounds as gg_sound

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_triple_level Addon for GunGame: Python" 
info.version  = "1.15.2008"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_triple_level" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007, Chrisber"


global list_currentTripleLevel
# Create a list to store those that are currently triple levelled
list_currentTripleLevel = []

def load():
    # Register this addon with GunGame
    gungame.registerAddon("gungame/included_addons/gg_triple_level", "GG Triple Level")
    
def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon("gungame/included_addons/gg_triple_level")

def gg_levelup(event_var):
    userid = event_var['userid']
    # Add 1 to triple level counter
    tripler = gungame.getPlayer(userid)
    tripler.set("triple", int(tripler.get("triple")) + 1)
    
    # If is it a Triple Level
    if tripler.get("triple") == 3:
        # Add the player to the triple level list
        list_currentTripleLevel.append(userid)
        # Sound and Messages
        es.emitsound('player', userid, gg_sound.gg_sounds['triplelevel'], 1.0, 1.0)
        announce("\4%s\1 triple levelled!" % event_var["name"])
        es.centermsg("%s triple levelled!" % event_var["name"])
        
        # Effect to player
        es.server.cmd("es_xgive %s env_spark" %userid)
        es.server.cmd("es_xfire %s env_spark setparent !activator" %userid)
        es.server.cmd("es_xfire %s env_spark addoutput \"spawnflags 896\"" %userid)
        es.server.cmd("es_xfire %s env_spark addoutput \"angles -90 0 0\"" %userid)
        es.server.cmd("es_xfire %s env_spark addoutput \"magnitude 8\"" %userid)
        es.server.cmd("es_xfire %s env_spark addoutput \"traillength 3\"" %userid)
        es.server.cmd("es_xfire %s env_spark startspark" %userid)
        
        # Speed
        player = playerlib.getPlayer(userid)
        player.set("speed", 1.5)
        
        # Gravity
        es.server.cmd("es_xfire %s !self \"gravity 400\"" %userid)

        # Reset the level counter to 0 since they just tripled
        tripler.set("triple", 0)
		
        # Stop Triple Level Bonus after 10 secs
        gamethread.delayed(10, removeTriple, (userid))

def player_death(event_var):
    # Get deaths player
    tripler = gungame.getPlayer(event_var["userid"])
    
    # Reset the triple level counter on player death
    tripler.set("triple", 0)
    
    # Check to see if this player is currently triple-levelled
    if userid in list_currentTripleLevel:
        # Since they are triple-levelled, we need to remove the triple
        removeTriple(userid)

def round_start(event_var):
    # Get all players
    players = playerlib.getUseridList("#all")
    
    # Reset the current triple level list
    list_currentTripleLevel = []
    
    # Reset the triple level counter at the beginning of each round for every player
    for userid in players:
        tripler = gungame.getPlayer(userid)
        tripler.set("triple", 0)

def removeTriple(userid):
    # Remove the player from the current triple level list
    list_currentTripleLevel.remove(userid)
    # Check if UserID exists
    # In the 10 secs the user maybe left
    if es.exists("userid", userid):
        # Stop Effect
        es.server.cmd("es_xfire %s env_spark stopspark" %userid)
        
        # Stop Speed
        player = playerlib.getPlayer(userid)
        player.set("speed", 1)
        
        # Stop Gravity (experimental)
        es.server.cmd("es_xfire %s !self \"gravity 800\"" %userid)
        
        # Stop the sound playing for the triple
        es.stopsound(userid, gg_sound.gg_sounds['triplelevel'])
        
def announce(message):
    es.msg("#multi", "\4[GG:Triple Level]\1 %s" % message)
   
def tell(userid, message):
    es.tell(userid, "#multi", "\4[GG:Triple Level]\1 %s" % message)

def echo(message):
    es.dbgmsg(0, "[GG:Triple Level] %s" % message)