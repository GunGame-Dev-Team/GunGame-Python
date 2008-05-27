''' (c) 2008 by the GunGame Coding Team

    Title: gg_triple_level
    Version: 1.0.324
    Description: When a player makes 3 levels in one round the player will be
                 faster and have an effect for 10 secs.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import playerlib
import gamethread

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_triple_level Addon for GunGame: Python"
info.version  = '1.0.324'
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_triple_level"
info.author   = "GunGame Development Team"

# ==============================================================================
#  GLOBALS
# ==============================================================================
list_currentTripleLevel = []

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_triple_level = gungamelib.registerAddon('gg_triple_level')
    gg_triple_level.setDisplayName('GG Triple Level')
    
def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_triple_level')

def player_death(event_var):
    userid = int(event_var['userid'])
    
    # Reset triple level
    player = gungamelib.getPlayer(userid)
    player['triple'] = 0

def round_start(event_var):
    # Reset the current triple level list
    list_currentTripleLevel = []
    
    # Reset the triple level counter for every player
    for userid in es.getUseridList():
        player = gungamelib.getPlayer(userid)['triple'] = 0

def gg_levelup(event_var):
    attacker = int(event_var['attacker'])
    
    # Add 1 to triple level counter
    gungamePlayer = gungamelib.getPlayer(attacker)
    gungamePlayer['triple'] += 1
    
    # Still not on the 3rd level?
    if gungamePlayer['triple'] != 3:
        return
    
    # Get player level
    name = event_var['es_attackername']
    index = playerlib.getPlayer(attacker).attributes['index']
    
    # Add the player to the triple level list
    list_currentTripleLevel.append(attacker)
    
    # Play sound
    gungamelib.playSound('#all', 'triplelevel')
    
    # Show messages
    gungamelib.saytext2('gg_triple_level', '#all', index, 'TripleLevelled', {'name': name})
    gungamelib.centermsg('gg_triple_level', '#all', 'CenterTripleLevelled', {'name': name})
    
    # Effect to player
    es.server.cmd('es_xgive %s env_spark' % attacker)
    es.server.cmd('es_xfire %s env_spark SetParent !activator' % attacker)
    es.server.cmd('es_xfire %s env_spark AddOutput "spawnflags 896"' % attacker)
    es.server.cmd('es_xfire %s env_spark AddOutput "angles -90 0 0"' % attacker)
    es.server.cmd('es_xfire %s env_spark AddOutput "magnitude 8"' % attacker)
    es.server.cmd('es_xfire %s env_spark AddOutput "traillength 3"' % attacker)
    es.server.cmd('es_xfire %s env_spark StartSpark' % attacker)
    
    # Speed
    player = playerlib.getPlayer(attacker)
    player.set('speed', 1.5)
    
    # Gravity
    es.server.cmd('es_xfire %s !self "gravity 400"' % attacker)
    
    # Reset the level counter to 0 since they just tripled
    gungamePlayer['triple'] = 0
    
    # Stop the triple level after 10 seconds
    gamethread.delayed(10, removeTriple, (attacker))

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def removeTriple(userid):
    # Remove the player from the current triple level list
    list_currentTripleLevel.remove(userid)
    
    # Client in server?
    if not gungamelib.clientInServer(userid):
        return
    
    # Stop effect
    es.server.cmd('es_xfire %s env_spark StopSpark' % userid)
    es.server.cmd('es_xfire %s env_spark Kill' % userid)
    
    # Reset speed
    player = playerlib.getPlayer(userid)
    player.set('speed', 1)
    
    # Reset gravity
    es.server.cmd('es_xfire %s !self "gravity %s"' % (userid, es.ServerVar('sv_gravity')))
    
    # Stop the sound playing for the triple
    if gungamelib.getSound('triplelevel'):
        es.stopsound(userid, gungamelib.getSound('triplelevel'))