''' (c) 2008 by the GunGame Coding Team

    Title: gg_deathmatch
    Version: 1.0.484
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
reload(spawnpointlib)
import testrepeat as repeat

# GunGame Imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_deathmatch (for GunGame: Python)'
info.version  = '1.0.484'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_deathmatch'
info.author   = 'GunGame Development Team'
    
# ==============================================================================
#  GLOBALS
# ==============================================================================

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    global mp_freezetimeBackUp
    global mp_roundtimeBackUp
    
    # Register addon with gungamelib
    gg_deathmatch = gungamelib.registerAddon('gg_deathmatch')
    gg_deathmatch.setDisplayName('GG Deathmatch')
    gg_deathmatch.loadTranslationFile()

    # Add dependencies
    gg_deathmatch.addDependency('gg_turbo', 1)
    gg_deathmatch.addDependency('gg_dead_strip', 1)
    gg_deathmatch.addDependency('gg_dissolver', 1)
    gg_deathmatch.addDependency('gg_map_obj', 0)
    gg_deathmatch.addDependency('gg_knife_elite', 0)
    gg_deathmatch.addDependency('gg_elimination', 0)
    
    # Create repeats for all players on the server
    for userid in es.getUseridList():
        respawnPlayer = repeat.find('gungameRespawnPlayer%s' % userid)
        
        if not respawnPlayer:
            repeat.create('gungameRespawnPlayer%s' % userid, respawnCountDown, (userid))
    
    # Respawn all dead players
    for userid in playerlib.getUseridList('#dead'):
        repeat.start('gungameRespawnPlayer%s' % userid, 1, gungamelib.getVariable('gg_dm_respawn_delay'))

    mp_freezetimeBackUp = int(es.ServerVar('mp_freezetime'))
    mp_roundtimeBackUp = int(es.ServerVar('mp_roundtime'))
    
    es.forcevalue('mp_freezetime', 0)
    es.forcevalue('mp_roundtime', 9)

def unload():
    global spawnPoints
    global mp_freezetimeBackUp
    global mp_roundtimeBackUp
    
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_deathmatch')
    
    # Reset freezetime and rountime to their original values
    es.forcevalue('mp_freezetime', mp_freezetimeBackUp)
    es.forcevalue('mp_roundtime', mp_roundtimeBackUp)
    
    # Delete all player respawns
    for userid in es.getUseridList():
        if repeat.find('gungameRespawnPlayer%s' % userid):
            repeat.delete('gungameRespawnPlayer%s' % userid)

def es_map_start(event_var):
    # Don't allow respawn
    gungamelib.setGlobal('respawn_allowed', 0)

def gg_win(event_var):
    for userid in es.getUseridList():
        if repeat.find('gungameRespawnPlayer%s' % userid):
            repeat.delete('gungameRespawnPlayer%s' % userid)
    
def player_team(event_var):
    if event_var['disconnect'] != '0':
        return
    
    # Get the userid
    userid = event_var['userid']
    
    # If the player does not have a respawn repeat, create one
    respawnPlayer = repeat.find('gungameRespawnPlayer%s' % userid)
    if not respawnPlayer:
        repeat.create('gungameRespawnPlayer%s' % userid, respawnCountDown, (userid))
    
    # Don't allow spectators or players that are unassigned to respawn
    if int(event_var['team']) < 2:
        if repeat.status('gungameRespawnPlayer%s' % userid) != 1:
            repeat.stop('gungameRespawnPlayer%s' % userid)
            
            if gungamelib.canShowHints():
                gungamelib.hudhint('gg_deathmatch', userid, 'RespawnCountdown_CancelTeam')
        
        return
    
    # Respawn the player
    repeat.start('gungameRespawnPlayer%s' % userid, 1, gungamelib.getVariable('gg_dm_respawn_delay'))

def player_spawn(event_var):
    global spawnPoints
    
    # Get the userid
    userid = int(event_var['userid'])
    
    # Is a spectator?
    if gungamelib.isSpectator(userid) or gungamelib.isDead(userid):
        return
    
    if int(gungamelib.getVariable('gg_noblock')):
        return
    
    # Prevent players from sticking together
    es.setplayerprop(userid, 'CBaseEntity.m_CollisionGroup', 17)
    physexplodeFormat = 'es_xgive %s env_physexplosion;' % userid
    physexplodeFormat += 'es_xfire %s env_physexplosion addoutput "magnitude 100";' % userid
    physexplodeFormat += 'es_xfire %s env_physexplosion addoutput "radius 50";' % userid
    physexplodeFormat += 'es_xfire %s env_physexplosion addoutput "inner_radius 0";' % userid
    physexplodeFormat += 'es_xfire %s env_physexplosion addoutput "spawnflags 15";' % userid
    physexplodeFormat += 'es_xfire %s env_physexplosion addoutput "targetentityname player";' % userid
    physexplodeFormat += 'es_xfire %s env_physexplosion explode;' % userid
    physexplodeFormat += 'es_xdelayed 0 es_xfire %s env_physexplosion kill' % userid
    es.delayed(1, physexplodeFormat)
    gamethread.delayed(1.5, es.setplayerprop, (userid, 'CBaseEntity.m_CollisionGroup', 5))

def player_death(event_var):
    # Get the userid
    userid = event_var['userid']
    
    # Remove defuser
    try:
        if playerlib.getPlayer(userid).get('defuser'):
            gamethread.delayed(0.5, es.remove, ('item_defuser'))
    except playerlib.UseridError:
        pass
    
    # Respawn the player if the round hasn't ended
    if gungamelib.getGlobal('respawn_allowed'):
        repeat.start('gungameRespawnPlayer%s' % userid, 1, gungamelib.getVariable('gg_dm_respawn_delay'))

def player_disconnect(event_var):
    # Get userid
    userid = event_var['userid']
    
    # Delete the player-specific repeat
    if repeat.find('gungameRespawnPlayer%s' % userid):
        repeat.delete('gungameRespawnPlayer%s' % userid)

def round_start(event_var):
    # Allow respawn
    gungamelib.setGlobal('respawn_allowed', 1)

def round_end(event_var):
    # Don't allow respawn
    gungamelib.setGlobal('respawn_allowed', 0)

def respawnCountDown(userid):
    # Make sure that the repeat exists
    respawnRepeat = repeat.find('gungameRespawnPlayer%s' %userid)
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
        gungamelib.respawn(userid)