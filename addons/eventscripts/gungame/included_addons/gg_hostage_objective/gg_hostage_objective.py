'''
(c)2007 by the GunGame Coding Team

    Title:      gg_hostage_objective
Version #:      1.0.102
Description:    Adds rewards for rescueing or preventing the rescuing of hostages.
'''

import es
import playerlib
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_hostage_objective Addon for GunGame: Python" 
info.version  = "1.0.102"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_hostage_objective" 
info.author   = "GunGame Development Team"


# Tracks who has a following hostage
dict_hostageTracker = {}


def load():
    # Register this addon with GunGame
    gungame.registerAddon('gg_hostage_objective', 'GG Hostage Objective')
        
        
def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gg_hostage_objective')
    
    
def round_start(event_var):
    global dict_hostageTracker
    dict_hostageTracker.clear()
    
    
def hostage_follows(event_var):
    print 'HOSTAGE FOLLOWS'
    global dict_hostageTracker
    userid = event_var['userid']
    if userid not in dict_hostageTracker:
        dict_hostageTracker[userid] = {'hostages':[event_var['hostage']], 'rescues':0}
    else:
        dict_hostageTracker[userid]['hostages'].append(event_var['hostage'])
        
        
def hostage_stops_following(event_var):
    print 'HOSTAGE STOPS FOLLOWING'
    global dict_hostageTracker
    userid = event_var['userid']
    hostage = event_var['hostage']
    if hostage in dict_hostageTracker[userid]['hostages']:
        dict_hostageTracker[userid]['hostages'].remove(hostage)
        
        
def hostage_killed(event_var):
    print 'HOSTAGE KILLED'
    userid = event_var['userid']
    if es.exists('userid', userid):
        gungamePlayer = gungame.getPlayer(userid)
        gungamePlayerLevel = int(gungamePlayer.get('level'))
        gungame.triggerLevelDownEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_username'], event_var['es_userteam'], gungamePlayerLevel, gungamePlayerLevel - 1, 0, 0)
        
        
def hostage_rescued(event_var):
    print 'HOSTAGE RESCUED'
    userid = event_var['userid']
    dict_hostageTracker[userid]['rescues'] += 1
    if dict_hostageTracker[userid]['rescues'] >= 2:
        gungamePlayer = gungame.getPlayer(userid)
        gungamePlayerLevel = int(gungamePlayer.get('level')) 
        gungame.triggerLevelUpEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_username'], event_var['es_userteam'], gungamePlayerLevel, gungamePlayerLevel + 1, 0, 0)
        dict_hostageTracker[userid]['rescues'] = 0
        
        
def player_death(event_var):
    global dict_hostageTracker
    userid = event_var['userid']
    if userid in dict_hostageTracker and len(dict_hostageTracker[userid]['hostages']):
        gungameVictim = gungame.getPlayer(userid)
        gungameVictimLevel = int(gungameVictim.get('level'))
        attacker = event_var['attacker']
        gungameAttacker = gungame.getPlayer(attacker)
        gungameAttackerLevel = int(gungameAttacker.get('level'))
        gungame.triggerLevelUpEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], gungameAttackerLevel, gungameAttackerLevel + 1, userid, event_var['es_username'])
        dict_hostageTracker[userid].clear()