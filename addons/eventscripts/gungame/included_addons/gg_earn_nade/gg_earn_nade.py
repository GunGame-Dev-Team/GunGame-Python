''' (c) 2008 by the GunGame Coding Team

    Title: gg_earn_nade
    Version: 1.0.220
    Description: When a player is on "hegrenade" level and they get a kill with
                 a weapon other than an "hegrenade", they are given an
                 additional hegrenade if they do not have one.
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
info.name     = "gg_earn_nade (for GunGame: Python)"
info.version  = "1.0.210"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_earn_nade"
info.author   = "GunGame Development Team"

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register this addon with GunGamelib
    gg_earn_nade = gungamelib.registerAddon('gg_earn_nade')
    gg_earn_nade.setDisplayName('GG Earn Grenade')

def unload():
    # Unregister the addon with GunGamelib
    gungamelib.unregisterAddon('gg_earn_nade')


def player_death(event_var):
    # Get variables
    attacker = int(event_var['attacker'])
    userid = int(event_var['userid'])
    
    # Make sure that the attacker is not "world"
    if attacker == 0:
        return
    
    # Is a team-kill?
    if event_var['es_attackerteam'] == event_var['es_userteam']:
        return
    
    # Get attacker object
    gungameAttacker = gungamelib.getPlayer(attacker)
    
    # Make sure attacker's weapon is hegrenade
    if gungameAttacker.getWeapon() != 'hegrenade':
        return
    
    # Attacker can't level up?
    if gungameAttacker['preventlevel'] == 0:
        return
    
    # Make sure the attacking weapon was not hegrenade
    if event_var['weapon'] == 'hegrenade':
        return
    
    # Get victim object
    gungameVictim = gungamelib.getPlayer(userid)
    
    # Victim is AFK?
    if gungameVictim.isPlayerAFK():
        return
    
    # Get playerlib player object
    playerlibPlayer = playerlib.getPlayer(attacker)
    
    # Only give them a hegrenade if they don't already have one
    if int(playerlibPlayer.get('he')) == 0:
        # Give them an additional hegrenade
        es.server.cmd('es_xgive %s weapon_hegrenade' % attacker)