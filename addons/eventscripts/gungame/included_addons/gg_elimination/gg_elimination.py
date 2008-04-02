''' (c) 2008 by the GunGame Coding Team

    Title: gg_elimination
    Version: 1.0.236
    Description: Players respawn after their killer is killed.
    
    Originally for ES1.3 created by ichthys.
    (http://addons.eventscripts.com/addons/view/3972)
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import gamethread
import playerlib
import usermsg

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_elimination Addon for GunGame: Python'
info.version  = '1.0.236'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_elimination'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
# Set up variables for use throughout gg_elimination
dict_addonVars = {}
dict_addonVars['roundActive'] = 0
dict_addonVars['currentRound'] = 0

# Player Database
dict_playersEliminated = {}

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_elimination = gungamelib.registerAddon('gg_elimination')
    gg_elimination.setDisplayName('GG Elimination')
    gg_elimination.addDependency('gg_turbo', 1)
    gg_elimination.addDependency('gg_dead_strip', 1)
    gg_elimination.addDependency('gg_dissolver', 1)
    gg_elimination.addDependency('gg_knife_elite', 0)
    gg_elimination.addDependency('gg_deathmatch', 0)

    # Get userids of all connected players
    for userid in es.getUseridList():
        dict_playersEliminated[str(userid)] = []

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_elimination')
    
    # Prevent players from spawning after gg_elimination is disabled
    dict_addonVars['roundActive'] = 0


def es_map_start(event_var):
    # reset round tracking
    dict_addonVars['roundActive'] = 0
    dict_addonVars['currentRound'] = 0

def round_start(event_var):
    # Round tracking
    dict_addonVars['roundActive'] = 1
    dict_addonVars['currentRound'] += 1
    
    # Message telling players how elimination works
    for player in dict_playersEliminated:
        dict_playersEliminated[player] = []
    es.msg('#multi', '#green[Elimination] #lightgreenPlayers respawn when their killer is killed')
        
def round_end(event_var):
    # More round tracking
    dict_addonVars['roundActive'] = 0
    
def player_activate(event_var):
    # Add new player to player dict
    userid = event_var['userid']
    if not dict_playersEliminated.has_key(userid):
        dict_playersEliminated[userid] = []

def player_disconnect(event_var):
    # Respawn disconnecting users eliminated players
    userid = event_var['userid']
    respawnEliminated(userid, dict_addonVars['currentRound'])
    # Remove diconnecting player from player dict
    if dict_playersEliminated.has_key(userid):
        del dict_playersEliminated[userid]

def player_death(event_var):
    userid = event_var['userid']
    # Check to see if the round has ended
    if dict_addonVars['roundActive']:
        attacker = event_var['attacker']
        
        # Set up victim message
        respawnMsgFormat = ''
        
        # Check if death was a suicide and respawn player
        if userid == attacker or attacker == '0':
            gamethread.delayed(5, respawnPlayer, (userid, dict_addonVars['currentRound']))
            es.tell(userid, '#multi', '#green[Elimination] #lightgreenSuicide auto respawn: 5 seconds')
            
        # Check if death was a teamkill and respawn victim
        elif event_var['es_userteam'] == event_var['es_attackerteam']:
            gamethread.delayed(5, respawnPlayer, (userid, dict_addonVars['currentRound']))
            es.tell(userid, '#multi', '#green[Elimination] #lightgreenTeamkill auto respawn: 5 seconds')
        else:
            # Add victim to the Attackers Eliminated players
            dict_playersEliminated[attacker].append(userid)
            
            index = playerlib.getPlayer(attacker).attributes['index']
            usermsg.saytext2(userid, index, '\4[Elimination]\1 You will respawn when \3%s\1 dies' %event_var['es_attackername'])
            
        # Check if victim had any Eliminated players
        gamethread.delayed(1, respawnEliminated, (userid, dict_addonVars['currentRound']))

# ==============================================================================
#  RESPAWN CODE
# ==============================================================================
def respawnPlayer(userid, respawnRound):
    # Check if the round is over and respawn player
    if dict_addonVars['roundActive'] and dict_addonVars['currentRound'] == respawnRound:
        index = playerlib.getPlayer(userid).attributes['index']
        for sendid in es.getUseridList():
            usermsg.saytext2(sendid, index, '\4[Elimination]\1 Respawning: \3%s\1' %es.getplayername(userid))
        es.server.cmd('est_spawn %s' %userid)

def respawnEliminated(userid, respawnRound):
    # Format respawning message
    msgFormat = None
    
    # Check if round is over
    if dict_addonVars['roundActive'] and dict_addonVars['currentRound'] == respawnRound:
        index = 0
        
        # Respawn all victims eliminated players
        for player in dict_playersEliminated[userid]:
            if es.exists('userid', player):
                es.server.cmd('est_spawn %s' %player)
                msgFormat = '%s\3%s\1, ' %(msgFormat, es.getplayername(player))
                if not index:
                    index = playerlib.getPlayer(player).attributes['index']
        # Show respawning players
        if msgFormat:
            # es.msg('#multi', '#green[Elimination] #lightgreenRespawning: #default%s' %msgFormat[0:-2])
            for sendid in es.getUseridList():
                usermsg.saytext2(sendid, index, '\4[Elimination]\1 Respawning: %s' %msgFormat[0:-2])
        # Clear victims eliminated player list
        dict_playersEliminated[userid] = []
