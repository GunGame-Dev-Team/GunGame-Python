''' (c) 2008 by the GunGame Coding Team

    Title: gg_elimination
    Version: 1.0.302
    Description: Players respawn after their killer is killed.
    
    Originally for ES1.3 created by ichthys:
        http://addons.eventscripts.com/addons/view/3972
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import gamethread
import usermsg

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_elimination Addon for GunGame: Python'
info.version  = '1.0.302'
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
dict_addonVars['respawnCmd'] = gungamelib.getVariable('gg_dm_respawn_cmd')

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

    # Get userids of all connected players
    for userid in es.getUseridList():
        dict_playersEliminated[str(userid)] = []

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_elimination')
    
    # Prevent players from spawning after gg_elimination is disabled
    dict_addonVars['roundActive'] = 0


def es_map_start(event_var):
    # Reset round tracking
    dict_addonVars['roundActive'] = 0
    dict_addonVars['currentRound'] = 0

def round_start(event_var):
    # Round tracking
    dict_addonVars['roundActive'] = 1
    dict_addonVars['currentRound'] += 1
    
    # Reset all eliminated player counters
    for player in dict_playersEliminated:
        dict_playersEliminated[player] = []
    
    gungamelib.msg('gg_elimination', '#all', 'RoundInfo')

def round_end(event_var):
    # Set round inactive
    dict_addonVars['roundActive'] = 0
    
def player_activate(event_var):
    userid = event_var['userid']
    
    # Create player dictionary
    dict_playersEliminated[userid] = []

def player_disconnect(event_var):
    userid = event_var['userid']
    
    # Remove diconnecting player from player dict
    if dict_playersEliminated.has_key(userid):
        respawnEliminated(userid, dict_addonVars['currentRound'])
        del dict_playersEliminated[userid]

def player_death(event_var):
    # Check to see if the round is active
    if not dict_addonVars['roundActive']:
        return
    
    # Get userid and attacker userids
    userid = event_var['userid']    
    attacker = event_var['attacker']
    
    # Was suicide?
    if userid == attacker or attacker == '0':
        gamethread.delayed(5, respawnPlayer, (userid, dict_addonVars['currentRound']))
        gungamelib.msg('gg_elimination', userid, 'SuicideAutoRespawn')
    
    # Was a teamkill?
    elif event_var['es_userteam'] == event_var['es_attackerteam']:
        gamethread.delayed(5, respawnPlayer, (userid, dict_addonVars['currentRound']))
        gungamelib.msg('gg_elimination', userid, 'TeamKillAutoRespawn')
    
    # Was a normal death
    else:
        # Add victim to the attackers eliminated players
        dict_playersEliminated[attacker].append(userid)
        
        # Tell them they will respawn when their attacker dies
        index = gungamelib.getPlayer(attacker)['index']
        gungamelib.saytext2('gg_elimination', userid, index, 'RespawnWhenAttackerDies', {'attacker': event_var['es_attackername']})
    
    # Check if victim had any Eliminated players
    gamethread.delayed(1, respawnEliminated, (userid, dict_addonVars['currentRound']))

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def respawnPlayer(userid, respawnRound):
    # Make sure the round is active
    if not dict_addonVars['roundActive']:
        return
    
    # Check if respawn was issued in the current round
    if dict_addonVars['currentRound'] != respawnRound:
        return
    
    index = gungamelib.getPlayer(userid)['index']
    
    # Tell everyone that they are respawning
    gungamelib.saytext2('gg_elimination', '#all', index, 'RespawningPlayer', {'player': es.getplayername(userid)})
    
    # Respawn player
    es.server.cmd('%s %s' % (dict_addonVars['respawnCmd'], userid))

def respawnEliminated(userid, respawnRound):    
    # Check if round is over
    if not dict_addonVars['roundActive']:
        return
    
    # Check if respawn was issued in the current round
    if dict_addonVars['currentRound'] != respawnRound:
        return
    
    # Check the player has any eliminated players
    if not dict_playersEliminated[userid]:
        return
    
    # Set variables
    players = []
    index = 0
    
    # Respawn all victims eliminated players
    for playerid in dict_playersEliminated[userid]:
        # Make sure the player exists
        if not respawnable(playerid):
            continue
        
        # Respawn player
        es.server.cmd('%s %s' % (dict_addonVars['respawnCmd'], playerid))
        
        # Add to message format
        players.append('\3%s\1' % es.getplayername(playerid))
        
        # Get index
        if not index:
            index = gungamelib.getPlayer(playerid)['index']
    
    # Tell everyone that they are respawning
    gungamelib.saytext2('gg_elimination', '#all', index, 'RespawningPlayer', {'player': ', '.join(players)})
    
    # Clear victims eliminated player list
    dict_playersEliminated[userid] = []

def respawnable(userid):
    # Check if player is on a team (checks for existancy also)
    if gungamelib.isSpectator(userid):
        return False
    
    # Make sure the player is alive
    if not gungamelib.isDead(userid):
        return False
    
    return True