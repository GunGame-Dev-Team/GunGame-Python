'''
(c)2007 by the GunGame Coding Team

    Title:      gg_earn_nade
Version #:      1.0.102
Description:    When a player is on "hegrenade" level and they get a kill with a weapon other than
                an "hegrenade", they are given an additional hegrenade if they do not have one.
'''

import es
from gungame import gungame
import playerlib

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_earn_nade Addon for GunGame: Python" 
info.version  = "1.0.102"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_earn_nade" 
info.author   = "GunGame Development Team"

def load():
    # Register the addon with GunGame so that it will be automatically unloaded if GunGame is unloaded
    gungame.registerAddon('gg_earn_nade', 'GG Earn Nade')

def unload():
    # Unregister the addon with GunGame so that it will be automatically unloaded if GunGame is unloaded
    gungame.unregisterAddon('gg_earn_nade')

def gg_variable_changed(event_var):
    if event_var['cvarname'] == 'gg_earn_grenades' and event_var['newvalue'] == '0':
        es.unload('gg_earn_nade')

def player_death(event_var):
    attacker = int(event_var['attacker'])
    # Make sure that the attacker is not "world"
    if attacker != 0:
        gungameAttacker = gungame.getPlayer(attacker)
        # Check to see if the player is on grenade level
        if gungameAttacker.get('weapon') == 'hegrenade':
            # Make sure that PreventLevel is not set
            if int(gungameAttacker.get('PreventLevel')) == 0:
                # Make sure this was not a TK
                if event_var['es_attackerteam'] != event_var['es_userteam']:
                    # Make sure the victim was not AFK
                    userid = int(event_var['userid'])
                    gungameVictim = gungame.getPlayer(userid)
                    if not gungameVictim.get('isplayerafk'):
                        # Make sure the weapon they killed with was not an hegrenade
                        if event_var['weapon'] != 'hegrenade':
                            # Check to make sure they don't already have an hegrenade
                            playerlibPlayer = playerlib.getPlayer(attacker)
                            if int(playerlibPlayer.get('he')) == 0:
                                # Give them an additional hegrenade
                                es.server.cmd('es_xgive %d weapon_hegrenade' %attacker)