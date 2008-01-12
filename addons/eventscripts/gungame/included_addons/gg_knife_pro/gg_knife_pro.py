'''
(c)2008 by the GunGame Coding Team

    Title:      gg_knife_pro
Version #:      12.01.08
Description:    When one player knife kills another player, the attacker steals
                a level from the victim.
'''

# Imports
import es
import playerlib
import usermsg

from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_knife_pro Addon for GunGame: Python" 
info.version  = "12.01.08"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_knife_pro" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2008, Saul"

# Globals
gg_knife_pro_limit = 0

def load():    
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_knife_pro', 'GG Knife Pro')
    
    # Get gg_knife_pro_limit
    gg_knife_pro_limit = int(gungame.getGunGameVar('gg_knife_pro_limit'))
    
def unload():
    # Register this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_knife_pro')

def gg_variable_changed(event_var):
    # Get the cvar name
    cvar = event_var['cvarname']
    
    # Register change in gg_knife_pro_limit
    if cvar == 'gg_knife_pro_limit':
        gg_knife_pro_limit = int(event_var['newvalue'])
    
    # Unload the addon if they changed "gg_knife_pro" to "0"
    if cvar == 'gg_knife_pro' and event_var['newvalue'] == '0':
        es.unload('gungame/included_addons/gg_knife_pro')

def player_death(event_var):
    # Check for knife kill, and not a team kill
    if event_var['weapon'] != 'knife' or event_var['es_attackerteam'] == event_var['es_userteam']:
        return

    # Is warmup round?
    if gungame.getRegisteredAddons().has_key('gungame\\included_addons\\gg_warmup_round'):
        return
    
    # Get attacker info
    attacker = int(event_var['attacker'])
    gungameAttacker = gungame.getPlayer(attacker)
    gungameAttackerLevel = int(gungameAttacker.get('level'))
    
    # Get victim info
    userid = event_var['userid']
    gungameVictim = gungame.getPlayer(userid)
    gungameVictimLevel = int(gungameVictim.get('level'))
    
    # Can they levelup anyway?
    if int(gungameAttacker.get('PreventLevel')) == 1:
        tell(attacker, 'You cannot steal a level. You cannot levelup at the moment.')
        return
    
    # Is the attacker on the grenade level?
    if gungameAttacker.get('weapon') == 'hegrenade':
        tell(attacker, 'You cannot skip the grenade level!')
        return
    
    # Is the victim on level 1?
    if int(gungameVictim.get('level')) == 1:
        tell(attacker, 'You cannot steal a level from the victim, they are on level 1.')
        return
    
    # Is the victim AFK?
    if gungameVictim.get('isplayerafk'):
        tell(attacker, 'You cannot steal a level, the victim is AFK.')
        return
    
    # Is the level difference higher than the limit?
    if gungameAttackerLevel - gungameVictimLevel >= gg_knife_pro_limit:
        tell(attacker, 'The level difference between you and the victim is higher than the set limit.')
        return
    
    # Trigger level down for the victim
    gungame.triggerLevelDownEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_username'], event_var['es_userteam'], gungameVictimLevel, gungameVictimLevel - 1, attacker, event_var['es_attackername'])
    
    # Trigger level up for the attacker
    gungame.triggerLevelUpEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], gungameAttackerLevel, gungameAttackerLevel + 1, userid, event_var['es_username'])
    
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