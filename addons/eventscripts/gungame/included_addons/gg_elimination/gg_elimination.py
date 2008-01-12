'''
(c)2007 by the GunGame Coding Team

    Title:      gg_elimination
Version #:      1.0.40
Description:    Players respawn after their killer is killed.
                Originally for ES1.3 created by ichthy.
                http://addons.eventscripts.com/addons/view/3972
'''

import es
from gungame import gungame
import gamethread

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_elimination Addon for GunGame: Python" 
info.version  = "1.0.40"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_elimination"
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007"

# Set up variables for use throughout gg_elimination
roundActive = 0
currentRound = 0
dict_playersEliminated = {}
gg_dm_ragdoll_effect = int(gungame.getGunGameVar('gg_dm_ragdoll_effect'))

def load():
    # Get userids of all connected players
    global dict_playersEliminated
    for userid in es.getUseridList():
        dict_playersEliminated[str(userid)] = []
        
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_elimination', 'GG Elimination')
    
    # Unload Elimination if gg_deathmatch is set to 1
    if gungame.getGunGameVar('gg_deathmatch') == '1':
        gungame.setGunGameVar('gg_elimination', 0)

def unload():
    # Prevent players from spawning after gg_elimination is disabled
    global roundActive
    roundActive = 0
    
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_elimination')

def gg_variable_changed(event_var):
    # Register change for gg_dm_ragdoll_effect
    if event_var['cvarname'] == 'gg_dm_ragdoll_effect':
        gg_dm_ragdoll_effect = int(gungame.getGunGameVar('gg_dm_ragdoll_effect'))
    # Turn off Elimination if DeathMatch is enabled
    if event_var['cvarname'] == 'gg_deathmatch' and event_var['newlevel'] == '1':
        gungame.setGunGameVar('gg_elimination', 0)

def es_map_start(event_var):
    global roundActive
    global currentRound
    
    # reset round tracking
    roundActive = 0
    currentRound = 0

def round_start(event_var):
    global roundActive
    global currentRound
    global dict_playersEliminated
    
    # Round tracking
    roundActive = 1
    currentRound += 1
    
    # Message telling players how elimination works
    for player in dict_playersEliminated:
        dict_playersEliminated[player] = []
    es.msg('#multi', '#green[Elimination] #lightgreenPlayers respawn when their killer is killed')
        
def round_end(event_var):
    global roundActive
    
    # More round tracking
    roundActive = 0
    
def player_activate(event_var):
    global dict_playersEliminated
    
    # Add new player to player dict
    userid = event_var['userid']
    if not dict_playersEliminated.has_key(userid):
        dict_playersEliminated[userid] = []

def player_disconnect(event_var):
    global currentRound
    global dict_playersEliminated
    
    # Respawn disconnecting users eliminated players
    userid = event_var['userid']
    respawnEliminated(userid, currentRound)
    # Remove diconnecting player from player dict
    if dict_playersEliminated.has_key(userid):
        del dict_playersEliminated[userid]

def player_death(event_var):
    global roundActive
    global dict_playersEliminated
    global gg_dm_ragdoll_effect
    
    userid = event_var['userid']
    # Check to see if the round has ended
    if roundActive:
        attacker = event_var['attacker']
        # Set up victim message
        respawnMsgFormat = ''
        # Check if death was a suicide and respawn player
        if userid == attacker or attacker == '0':
            gamethread.delayed(5, respawnPlayer, (userid, currentRound))
            es.tell(userid, '#multi', '#green[Elimination] #lightgreenSuicide auto respawn: 5 seconds')
        # Check if death was a teamkill and respawn victim
        elif event_var['es_userteam'] == event_var['es_attackerteam']:
            gamethread.delayed(5, respawnPlayer, (userid, currentRound))
            es.tell(userid, '#multi', '#green[Elimination] #lightgreenTeamkill auto respawn: 5 seconds')
        # Add victim to the Attackers Eliminated players
        else:
            dict_playersEliminated[attacker].append(userid)
            es.tell(userid, '#multi', '#green[Elimination] #lightgreenYou will respawn when #default%s #lightgreendies.' %event_var['es_attackername'])
        # Check if victim had any Eliminated players
        gamethread.delayed(1, respawnEliminated, (userid, currentRound))
        
    # Give the entity dissolver and set its KeyValues
    es.server.cmd('es_xgive %s env_entity_dissolver' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "target cs_ragdoll"' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "magnitude 1"' % userid)
    es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "dissolvetype %s"' % (userid, gg_dm_ragdoll_effect))
    
    # Dissolve the ragdoll then kill the dissolver
    gamethread.delayed(0.01, es.server.cmd, 'es_xfire %s env_entity_dissolver Dissolve' % userid)
    gamethread.delayed(0.06, es.server.cmd, 'es_xremove env_entity_dissolver')

def respawnPlayer(userid, respawnRound):
    global roundActive
    global currentRound
    
    # Check if the round is over and respawn player
    if roundActive and currentRound == respawnRound:
        es.server.cmd('est_spawn %s' %userid)
        es.msg('#multi', '#green[Elimination] #lightgreenRespawning: #default%s' %es.getplayername(userid))

def respawnEliminated(userid, respawnRound):
    global roundActive
    global currentRound
    global dict_playersEliminated
    
    # Format respawning message
    msgFormat = ''
    # Check if round is over
    if roundActive and currentRound == respawnRound:
        # Respawn all victims eliminated players
        for player in dict_playersEliminated[userid]:
            if es.exists('userid', player):
                es.server.cmd('est_spawn %s' %player)
                msgFormat = '%s%s, ' %(msgFormat, es.getplayername(player))
        # Show respawning players
        if msgFormat != '':
            es.msg('#multi', '#green[Elimination] #lightgreenRespawning: #default%s' %msgFormat[0:-2])
        # Clear victims eliminated player list
        dict_playersEliminated[userid] = []