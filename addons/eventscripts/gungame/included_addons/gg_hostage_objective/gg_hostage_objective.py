''' (c) 2008 by the GunGame Coding Team

    Title: gg_hostage_objective
    Version: 1.0.340
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
info.version  = '1.0.340'
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
    gg_hostage_objective.setDisplayName('GG Hostage Objective')

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_hostage_objective')


def round_start(event_var):
    dict_hostageTracker.clear()

def hostage_follows(event_var):
    userid = int(event_var['userid'])
    hostage = int(event_var['hostage'])
    
    # Add hostage to player
    if dict_hostageTracker.has_key(userid):
        dict_hostageTracker[userid]['hostages'].append(hostage)
    else:
        dict_hostageTracker[userid] = {'hostages': [hostage], 'rescues': 0}

def hostage_stops_following(event_var):
    userid = int(event_var['userid'])
    hostage = int(event_var['hostage'])
    
    # Remove hostage from player
    if hostage in dict_hostageTracker[userid]['hostages']:
        dict_hostageTracker[userid]['hostages'].remove(hostage)

def hostage_killed(event_var):
    userid = int(event_var['userid'])
    
    # Get player info
    player = gungamelib.getPlayer(userid)
    level = player['level']
    
    # Level them down
    gungamelib.triggerLevelDownEvent(userid, level, level - 1, 0, 'hostage_killed')

def hostage_rescued(event_var):
    userid = int(event_var['userid'])
    
    # Increment rescues
    dict_hostageTracker[userid]['rescues'] += 1
    
    # No more than 2 rescues?
    if dict_hostageTracker[userid]['rescues'] < 2:
        return
    
    # Get player info
    player = gungamelib.getPlayer(userid)
    level = player['level']
    
    # Increment level
    gungamelib.triggerLevelUpEvent(userid, level, level + 1, 0, 'hostage_rescued')
    
    # Reset rescues
    dict_hostageTracker[userid]['rescues'] = 0

def player_death(event_var):
    userid = int(event_var['userid'])
    attacker = int(event_var['attacker'])
    
    # Suicide?
    if userid == attacker or attacker == 0:
        return
    
    # No hostages following?
    if not dict_hostageTracker.has_key(userid):
        return
    
    # No hostages following? (Check 2)
    if not dict_hostageTracker[userid]['hostages']:
        return
    
    # Get victim info
    victimPlayer = gungamelib.getPlayer(userid)
    victimLevel = victimPlayer['level']
    
    # Get attacker info
    attackerPlayer = gungamelib.getPlayer(attacker)
    attackerLevel = attackerPlayer['level']
    
    # Level up the attacker
    gungamelib.triggerLevelUpEvent(attacker, level, level + 1, userid, 'hostage_stop')
    
    # Remove from hostage tracker
    del dict_hostageTracker[userid]