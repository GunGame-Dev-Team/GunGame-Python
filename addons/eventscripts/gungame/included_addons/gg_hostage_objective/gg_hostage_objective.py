''' (c) 2008 by the GunGame Coding Team

    Title: gg_hostage_objective
    Version: 1.0.212
    Description: Adds rewards for rescuing or preventing the rescuing of
                 hostages.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import playerlib

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_hostage_objective (for GunGame: Python)'
info.version  = '1.0.212'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_hostage_objective'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
dict_hostageTracker = {}

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_hostage_objective = gungamelib.registerAddon('gg_hostage_objective')
    gg_hostage_objective.setMenuText('GG Hostage Objective')

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_hostage_objective')


def round_start(event_var):
    dict_hostageTracker.clear()

def hostage_follows(event_var):
    userid = event_var['userid']
    if userid not in dict_hostageTracker:
        dict_hostageTracker[userid] = {'hostages':[event_var['hostage']], 'rescues':0}
    else:
        dict_hostageTracker[userid]['hostages'].append(event_var['hostage'])

def hostage_stops_following(event_var):
    userid = event_var['userid']
    hostage = event_var['hostage']
    if hostage in dict_hostageTracker[userid]['hostages']:
        dict_hostageTracker[userid]['hostages'].remove(hostage)

def hostage_killed(event_var):
    userid = event_var['userid']
    if es.exists('userid', userid):
        gungamePlayer = gungamelib.getPlayer(userid)
        gungamePlayerLevel = gungamePlayer['level']
        gungamelib.triggerLevelDownEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_username'], event_var['es_userteam'], gungamePlayerLevel, gungamePlayerLevel - 1, 0, 0)

def hostage_rescued(event_var):
    userid = event_var['userid']
    dict_hostageTracker[userid]['rescues'] += 1
    if dict_hostageTracker[userid]['rescues'] >= 2:
        gungamePlayer = gungamelib.getPlayer(userid)
        gungamePlayerLevel = gungamePlayer['level']
        gungamelib.triggerLevelUpEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_username'], event_var['es_userteam'], gungamePlayerLevel, gungamePlayerLevel + 1, 0, 0)
        dict_hostageTracker[userid]['rescues'] = 0

def player_death(event_var):
    userid = event_var['userid']
    if userid in dict_hostageTracker and len(dict_hostageTracker[userid]['hostages']):
        gungameVictim = gungame.getPlayer(userid)
        gungameVictimLevel = int(gungameVictim.get('level'))
        attacker = event_var['attacker']
        gungameAttacker = gungame.getPlayer(attacker)
        gungameAttackerLevel = int(gungameAttacker.get('level'))
        gungamelib.triggerLevelUpEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], gungameAttackerLevel, gungameAttackerLevel + 1, userid, event_var['es_username'])
        dict_hostageTracker[userid].clear()