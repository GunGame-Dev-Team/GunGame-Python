''' (c) 2008 by the GunGame Coding Team

    Title: gg_multi_level
    Version: 5.0.374
    Description: When a player makes a certain number of levels
                 in one round the player will be faster and have
                 an effect for 10 secs.
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
info.name     = 'gg_multi_level (for GunGame5)'
info.version  = '5.0.374'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_multi_level'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
list_currentMultiLevel = []
roundCounter = 0

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_multi_level = gungamelib.registerAddon('gg_multi_level')
    gg_multi_level.setDisplayName('GG Multi Level')
    gg_multi_level.loadTranslationFile()
    
def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_multi_level')

def player_death(event_var):
    userid = int(event_var['userid'])
    
    # Reset multi-level
    player = gungamelib.getPlayer(userid)
    player['multilevel'] = 0

def round_start(event_var):
    global list_currentMultiLevel
    global roundCounter
    # Reset the current multi level list
    list_currentMultiLevel = []
    
    # Reset the multi level counter for every player
    for userid in es.getUseridList():
        gungamelib.getPlayer(userid)['multilevel'] = 0
    
    roundCounter += 1

def gg_levelup(event_var):
    attacker = int(event_var['attacker'])
    
    # Add 1 to multi level counter
    gungamePlayer = gungamelib.getPlayer(attacker)
    gungamePlayer['multilevel'] += 1
    
    # Still not on the 3rd level?
    if gungamePlayer['multilevel'] != int(gungamelib.getVariableValue('gg_multi_level')):
        return
    
    # Get player level
    name = event_var['es_attackername']
    index = gungamePlayer['index']
    
    # Add the player to the multi level list
    list_currentMultiLevel.append(attacker)
    
    # Emit sound
    gungamelib.emitSound(attacker, 'multilevel')
    
    # Show messages
    gungamelib.saytext2('gg_multi_level', '#all', index, 'MultiLevelled', {'name': name})
    gungamelib.centermsg('gg_multi_level', '#all', 'CenterMultiLevelled', {'name': name})
    
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
    
    # Reset the level counter to 0 since they just multi-levelled
    gungamePlayer['multilevel'] = 0
    
    # Stop the multi level after 10 seconds
    gamethread.delayed(10, removeMulti, (attacker, roundCounter))
    
    # Fire gg_multi_level
    es.event('initialize', 'gg_multi_level')
    es.event('setint', 'gg_multi_level', 'userid', attacker)
    es.event('setint', 'gg_multi_level', 'leveler', attacker)
    es.event('fire', 'gg_multi_level')

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def removeMulti(userid, roundMultiStart):
    #Check if multikill was started in the current round
    if roundMultiStart != roundCounter:
        return
    
    # Remove the player from the current multi level list
    list_currentMultiLevel.remove(userid)
    
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
    
    # Stop the sound playing for the multi-level
    if gungamelib.getSound('multilevel'):
        es.stopsound(userid, gungamelib.getSound('multilevel'))
        
'''
[DONE] Change Sound Packs
[DONE] Change Player Class in gungamelib
[DONE] Change gg_default_addons.cfg
[DONE] Change gungame.py to load gg_multi_level
Remove Triple Level
'''