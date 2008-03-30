''' (c) 2008 by the GunGame Coding Team

    Title: gg_knife_pro
    Version: 1.0.218
    Description: When one player knife kills another player, the attacker steals
                 a level from the victim.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import playerlib
import usermsg

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_knife_pro Addon for GunGame: Python"
info.version  = '1.0.218'
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_knife_pro"
info.author   = "GunGame Development Team"

# ==============================================================================
#  GLOBALS
# ==============================================================================
proLimit = gungamelib.getVariable('gg_knife_pro_limit')

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():    
    # Register addon with gungamelib
    gg_knife_pro = gungamelib.registerAddon('gg_knife_pro')
    gg_knife_pro.setMenuText('GG Knife Pro')

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_knife_pro')


def player_death(event_var):
    # Check for knife kill, and not a team kill, and not a suicide by world
    userteam = event_var['es_userteam']
    attackerteam = event_var['es_attackerteam']
    
    # Skip if was a team kill, suicide or a not a knife kill
    if event_var['weapon'] != 'knife' or attackerteam == userteam or event_var['attacker'] == '0':
        return

    # Is warmup round?
    if gungamelib.getGlobal('isWarmup') == 1:
        return
        
    # Check to make sure it wasn't a suicide
    if event_var['attacker'] == '0':
        return
    
    # Get attacker info
    attacker = int(event_var['attacker'])
    gungameAttacker = gungamelib.getPlayer(attacker)
    gungameAttackerLevel = gungameAttacker['level']
    
    # Fix duplicate winning
    if gungameAttackerLevel == gungamelib.getTotalLevels():
        return
    
    # Get victim info
    userid = event_var['userid']
    gungameVictim = gungamelib.getPlayer(userid)
    gungameVictimLevel = gungameVictim['level']
    
    # Can they levelup anyway?
    if gungameAttacker['preventlevel'] == 1:
        gungamelib.msg('gg_knife_pro', attacker, 'AttackerPreventLevel')
        return
    
    # Is the attacker on the grenade level?
    if gungameAttacker.getWeapon() == 'hegrenade':
        gungamelib.msg('gg_knife_pro', attacker, 'AttackerNadeLevel')
        return
    
    # Is the victim on level 1?
    if gungameVictim['level'] == 1:
        gungamelib.msg('gg_knife_pro', attacker, 'VictimLevel1')
        return
    
    # Is the victim AFK?
    if gungameVictim.isPlayerAFK():
        gungamelib.msg('gg_knife_pro', attacker, 'VictimAFK')
        return
    
    # Is the level difference higher than the limit?
    if ((gungameAttackerLevel - gungameVictimLevel) >= int(proLimit)) and int(proLimit) != 0:
        gungamelib.msg('gg_knife_pro', attacker, 'LevelDifferenceLimit')
        return
        
    steamid = gungameVictim['steamid']
    username = event_var['es_username']
    gungameVictimNewLevel = gungameVictimLevel - 1
    attackersteamid = gungameAttacker['steamid']
    attackername = event_var['es_attackername']
    gungameAttackerNewLevel = gungameAttackerLevel + 1
    
    # Trigger level down for the victim
    gungamelib.triggerLevelDownEvent(userid, steamid, username, userteam, gungameVictimLevel, gungameVictimNewLevel, attacker, attackername)
    
    # Play the leveldown sound
    if gungamelib.getSound('leveldown'):
        es.playsound(userid, gungamelib.getSound('leveldown'), 1.0)
    
    # Trigger level up for the attacker
    gungamelib.triggerLevelUpEvent(attacker, attackersteamid, attackername, event_var['es_attackerteam'], gungameAttackerLevel, gungameAttackerNewLevel, userid, username, 'knife')
    
    # Play the leveldown sound
    if gungamelib.getSound('levelsteal'):
        es.playsound(attacker, gungamelib.getSound('levelsteal'), 1.0)
    
    # Event code
    es.event('initialize', 'gg_knife_steal')
    es.event('setint', 'gg_knife_steal', 'userid', attacker)
    es.event('setstring', 'gg_knife_steal', 'steamid', attackersteamid)
    es.event('setstring', 'gg_knife_steal', 'name', attackername)
    es.event('setstring', 'gg_knife_steal', 'team', attackerteam)
    es.event('setint', 'gg_knife_steal', 'attacker_level', gungameAttackerNewLevel)
    es.event('setint', 'gg_knife_steal', 'victim_level', gungameVictimNewLevel)
    es.event('setint', 'gg_knife_steal', 'victim', userid)
    es.event('setstring', 'gg_knife_steal', 'victimname', username)
    es.event('fire', 'gg_knife_steal')
    
    # Announce the level stealing
    index = playerlib.getPlayer(attacker).attributes['index']
    gungamelib.saytext2('gg_knife_pro', '#all', index, 'StoleLevel', {'attacker': attackername, 'victim': username})
    