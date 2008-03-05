'''
(c)2008 by the GunGame Coding Team

    Title:      gg_knife_pro
Version #:      1.0.119
Description:    When one player knife kills another player, the attacker steals
                a level from the victim.
'''

# EventScripts imports
import es
import playerlib
import usermsg

# GunGame imports
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_knife_pro Addon for GunGame: Python"
info.version  = "1.0.119"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_knife_pro"
info.author   = "GunGame Development Team"

# Globals
gg_knife_pro_limit = 0

def load():    
    # Register addon with gungamelib
    gg_knife_pro = gungamelib.registerAddon('gg_knife_pro')
    gg_knife_pro.setMenuText('GG Knife Pro')
    
    # Get gg_knife_pro_limit
    gg_knife_pro_limit = gungamelib.getVariableValue('gg_knife_pro_limit')
    
def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_knife_pro')

def server_cvar(event_var):
    # Get the cvar name
    cvar = event_var['cvarname']
    
    # Register change in gg_knife_pro_limit
    if cvar == 'gg_knife_pro_limit':
        gg_knife_pro_limit = int(event_var['cvarvalue'])
    
def player_death(event_var):
    # Check for knife kill, and not a team kill
    userteam = event_var['es_userteam']
    attackerteam = event_var['es_attackerteam']
    if event_var['weapon'] != 'knife' or attackerteam == userteam:
        return

    # Is warmup round?
    if gungamelib.getGlobal('isWarmup') == '1':
        return
    
    # Get attacker info
    attacker = int(event_var['attacker'])
    gungameAttacker = gungamelib.getPlayer(attacker)
    gungameAttackerLevel = gungameAttacker['level']
    
    # Get victim info
    userid = event_var['userid']
    gungameVictim = gungamelib.getPlayer(userid)
    gungameVictimLevel = gungameVictim['level']
    
    # Can they levelup anyway?
    if gungameAttacker['preventlevel'] == 1:
        tell(attacker, 'You cannot steal a level. You cannot levelup at the moment.')
        return
    
    # Is the attacker on the grenade level?
    if gungameAttacker.getWeapon() == 'hegrenade':
        tell(attacker, 'You cannot skip the grenade level!')
        return
    
    # Is the victim on level 1?
    if gungameVictim['level'] == 1:
        tell(attacker, 'You cannot steal a level from the victim, they are on level 1.')
        return
    
    # Is the victim AFK?
    if gungameVictim.isPlayerAFK():
        tell(attacker, 'You cannot steal a level, the victim is AFK.')
        return
    
    # Is the level difference higher than the limit?
    if ((gungameAttackerLevel - gungameVictimLevel) >= gg_knife_pro_limit) and gg_knife_pro_limit != 0:
        tell(attacker, 'The level difference between you and the victim is higher than the set limit.')
        return
        
    steamid = gungameVictim['steamid']
    username = event_var['es_username']
    gungameVictimNewLevel = gungameVictimLevel - 1
    attackersteamid = gungameAttacker['steamid']
    attackername = event_var['es_attackername']
    gungameAttackerNewLevel = gungameAttackerLevel + 1
    
    # Trigger level down for the victim
    gungamelib.triggerLevelDownEvent(userid, steamid, username, userteam, gungameVictimLevel, gungameVictimNewLevel, attacker, attackername)
    
    # Trigger level up for the attacker
    gungamelib.triggerLevelUpEvent(attacker, attackersteamid, attackername, event_var['es_attackerteam'], gungameAttackerLevel, gungameAttackerNewLevel, userid, username, 'knife')
    
    # BEGIN THE EVENT CODE FOR INITIALIZING & FIRING EVENT "GG_KNIFE_STEAL"
    # -----------------------------------------------------------------------------------------------------------
    es.event('initialize', 'gg_knife_steal')
    # The userid of the player that stole the level
    es.event('setint', 'gg_knife_steal', 'userid', attacker)
    # The steamid of player that stole the level (provided by uniqueid)
    es.event('setstring', 'gg_knife_steal', 'steamid', attackersteamid)
    # The name of the player that stole the level
    es.event('setstring', 'gg_knife_steal', 'name', attackername)
    # The team # of the player that stole the level up: team 2= Terrorists, 3= CT
    es.event('setstring', 'gg_knife_steal', 'team', attackerteam)                                
    # The new level of the player that stole the level
    es.event('setint', 'gg_knife_steal', 'attacker_level', gungameAttackerNewLevel)
    # The new level of the victim
    es.event('setint', 'gg_knife_steal', 'victim_level', gungameVictimNewLevel)
    # The userid of victim
    es.event('setint', 'gg_knife_steal', 'victim', userid)
    # The victim's name
    es.event('setstring', 'gg_knife_steal', 'victimname', username)
    # Fire the "gg_knife_steal" event
    es.event('fire', 'gg_knife_steal')
    # -----------------------------------------------------------------------------------------------------------
    # END THE EVENT CODE FOR INITIALIZING & FIRING EVENT "GG_KNIFE_STEAL"
    
    # Announce the level stealing
    levelStole(attacker, userid)
    
def announce(message):
    es.msg('#multi', '\4[GG:Knife Pro]\1 %s' % message)
    
def tell(userid, message):
    es.tell(userid, '#multi', '\4[GG:Knife Pro]\1 %s' % message)

def levelStole(attackerUserid, victimUserid):
    # Get attacker index
    index = playerlib.getPlayer(attackerUserid).attributes['index']
    
    # Get attacker username and victim username
    attacker = es.getplayername(attackerUserid)
    victim = es.getplayername(victimUserid)
    
    # Loop through the players
    for userid in es.getUseridList():
        usermsg.saytext2(userid, index, '\3%s\1 stole a level from \4%s' % (attacker, victim))