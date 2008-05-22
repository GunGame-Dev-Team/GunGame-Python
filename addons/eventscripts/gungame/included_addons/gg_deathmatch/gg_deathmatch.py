''' (c) 2008 by the GunGame Coding Team

    Title: gg_deathmatch
    Version: 1.0.324
    Description: Team-deathmatch mod for GunGame.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts Imports
import es
import gamethread
import playerlib
import popuplib
import spawnpointlib
import testrepeat as repeat

# GunGame Imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_deathmatch (for GunGame: Python)'
info.version  = '1.0.324'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_deathmatch'
info.author   = 'GunGame Development Team'
    
# ==============================================================================
#  GLOBALS
# ==============================================================================
spawnPoints = None

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    global spawnPoints
    
    # Register addon with gungamelib
    gg_deathmatch = gungamelib.registerAddon('gg_deathmatch')
    gg_deathmatch.addDependency('gg_turbo', 1)
    gg_deathmatch.addDependency('gg_dead_strip', 1)
    gg_deathmatch.addDependency('gg_dissolver', 1)
    gg_deathmatch.addDependency('gg_map_obj', 0)
    gg_deathmatch.addDependency('gg_knife_elite', 0)
    gg_deathmatch.addDependency('gg_elimination', 0)
    
    # Get the spawn points for the map
    if gungamelib.inMap():
        spawnPoints = spawnpointlib.SpawnPointManager('cfg/gungame/spawnpoints')
    
    # Respawn all dead players
    for userid in playerlib.getUseridList('#dead'):
        repeat.start('respawnPlayer%s' % userid, 1, gungamelib.getVariable('gg_dm_respawn_delay'))
    
    # Set freezetime and roundtime
    es.server.cmd('mp_freezetime 0')
    es.server.cmd('mp_roundtime 900')

def unload():
    global spawnPoints
    
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_deathmatch')
    
    # Delete all player respawns
    for userid in es.getUseridList():
        repeat.delete('respawnPlayer%s' % userid)


def es_map_start(event_var):
    global spawnPoints
    
    # Don't allow respawn
    gungamelib.setGlobal('respawn_allowed', 0)
    
    # Reset spawnpoints
    spawnPoints = spawnpointlib.SpawnPointManager('cfg/gungame/spawnpoints')
    
def player_team(event_var):
    if event_var['disconnect'] != '0':
        return
    
    # Get the userid
    userid = event_var['userid']
    
    # If the player does not have a respawn repeat, create one
    respawnPlayer = repeat.find('respawnPlayer%s' % userid)
    if not respawnPlayer:
        repeat.create('respawnPlayer%s' % userid, respawnCountDown, (userid))
    
    # Don't allow spectators or players that are unassigned to respawn
    if int(event_var['team']) < 2:
        if repeat.status('respawnPlayer%s' % userid) != 1:
            repeat.stop('respawnPlayer%s' % userid)
            
            if gungamelib.canShowHints():
                gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_CancelTeam')
        
        return
    
    # Respawn the player
    repeat.start('respawnPlayer%s' % userid, 1, gungamelib.getVariable('gg_dm_respawn_delay'))

def player_spawn(event_var):
    global spawnPoints
    
    # Get the userid
    userid = int(event_var['userid'])
    
    # Is a spectator?
    if gungamelib.isSpectator(userid) or gungamelib.isDead(userid):
        return
    
    # No-block for a second, to stop sticking inside other players
    collisionBefore = es.getplayerprop(userid, 'CBaseEntity.m_CollisionGroup')
    es.setplayerprop(userid, 'CBaseEntity.m_CollisionGroup', 17)
    gamethread.delayed(1.5, es.setplayerprop, (userid, 'CBaseEntity.m_CollisionGroup', collisionBefore))
    
    # Do not continue if we have no spawn points
    if not spawnPoints.hasPoints():
        return
    
    # Teleport the player
    s = spawnPoints.getRandomPoint()
    gungamelib.getPlayer(userid).teleportPlayer(s[0], s[1], s[2], 0, s[4])

def player_death(event_var):
    # Get the userid
    userid = event_var['userid']
    
    # Remove defuser
    if playerlib.getPlayer(userid).get('defuser'):
        gamethread.delayed(0.5, es.remove, ('item_defuser'))
    
    # Respawn the player if the round hasn't ended
    if gungamelib.getGlobal('respawn_allowed'):
        repeat.start('respawnPlayer%s' % userid, 1, gungamelib.getVariable('gg_dm_respawn_delay'))

def player_disconnect(event_var):
    # Get userid
    userid = event_var['userid']
    
    # Delete the player-specific repeat
    if repeat.find('respawnPlayer%s' % userid):
        repeat.delete('respawnPlayer%s' % userid)

def round_start(event_var):
    # Allow respawn
    gungamelib.setGlobal('respawn_allowed', 1)

def round_end(event_var):
    # Don't allow respawn
    gungamelib.setGlobal('respawn_allowed', 0)

def respawnCountDown(userid):
    # Make sure that the repeat exists
    respawnRepeat = repeat.find('respawnPlayer%s' %userid)
    if not respawnRepeat:
        return
    
    # Not dead?
    if not gungamelib.isDead(userid):
        respawnRepeat.stop()
        return
    
    # Round finished?
    if gungamelib.getGlobal('respawn_allowed') == 0:
        # Tell them the round has ended
        if gungamelib.canShowHints():
            gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_RoundEnded')
        
        respawnRepeat.stop()
        return
    
    # Allow to show HUDHints?
    if gungamelib.canShowHints():
        # More than 1 remaining?
        if respawnRepeat['remaining'] > 1:
            gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_Plural', {'time': respawnRepeat['remaining']})
        
        # Is the counter 1?
        elif respawnRepeat['remaining'] == 1:
            gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_Singular')
    
    # Respawn the player
    if respawnRepeat['remaining'] == 0:
        es.server.cmd('%s %s' % (gungamelib.getVariable('gg_dm_respawn_cmd'), userid))
