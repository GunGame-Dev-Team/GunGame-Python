'''
(c)2008 by the GunGame Coding Team

    Title:      gg_triple_level
Version #:      1.0.117
Description:    When a player makes 3 levels in one round he get faster and have an effect for 10 secs
'''

# EventScripts imports
import es
import playerlib
import gamethread

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_triple_level Addon for GunGame: Python"
info.version  = "1.0.117"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_triple_level"
info.author   = "GunGame Development Team"

# Create a list to store those that are currently triple levelled
list_currentTripleLevel = []

def load():
    # Register addon with gungamelib
    gg_triple_level = gungamelib.registerAddon('gg_triple_level')
    gg_triple_level.setMenuText('GG Triple Level')
    
def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_triple_level')

def gg_levelup(event_var):
    userid = event_var['userid']
    # Add 1 to triple level counter
    gungamePlayer = gungamelib.getPlayer(userid)
    gungamePlayer['triple'] += 1
    
    # If is it a Triple Level
    if gungamePlayer['triple'] == 3:
        # Add the player to the triple level list
        list_currentTripleLevel.append(userid)
        # Sound and Messages
        if gungamelib.getSound('triplelevel') != '0':
            es.emitsound('player', userid, gungamelib.getSound('triplelevel'), 1.0, 1.0)
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
        gungamePlayer['triple'] = 0
		
        # Stop Triple Level Bonus after 10 secs
        gamethread.delayed(10, removeTriple, (userid))

def player_death(event_var):
    userid = event_var['userid']
    # Get deaths player
    gungamePlayer = gungamelib.getPlayer(userid)
    
    # Reset the triple level counter on player death
    gungamePlayer['triple'] = 0

def round_start(event_var):
    # Get all players
    players = playerlib.getUseridList("#all")
    
    # Reset the current triple level list
    list_currentTripleLevel = []
    
    # Reset the triple level counter at the beginning of each round for every player
    for userid in players:
        gungamePlayer = gungamelib.getPlayer(userid)
        gungamePlayer['triple'] = 0

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
        if gungamelib.getSound('triplelevel') != '0':
            es.stopsound(userid, gungamelib.getSound('triplelevel'))
        
def announce(message):
    es.msg("#multi", "\4[GG:Triple Level]\1 %s" % message)
   
def tell(userid, message):
    es.tell(userid, "#multi", "\4[GG:Triple Level]\1 %s" % message)

def echo(message):
    es.dbgmsg(0, "[GG:Triple Level] %s" % message)