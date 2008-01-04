'''
(c)2007 by the GunGame Coding Team

    Title:      gg_knife_pro
Version #:      11.29.2007
Description:    When one player knife kills another player, the attacker steals a level
                from the victim.
'''

import es
import playerlib
import usermsg
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_knife_pro Addon for GunGame: Python" 
info.version  = "11.29.2007"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_knife_pro" 
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007"

def load():
    global gg_knife_pro_limit
    # register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_knife_pro', 'GG Knife Pro')
    # get gg_knife_pro_limit
    gg_knife_pro_limit = gungame.getGunGameVar('gg_knife_pro_limit')
    
def unload():
    # Register this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_knife_pro')

def gg_variable_changed(event_var):
    global gg_knife_pro_limit
    # register change in gg_knife_pro_limit
    cvarName = event_var['cvarname']
    if cvarName == 'gg_knife_pro_limit':
        gg_knife_pro_limit = int(event_var['newvalue'])
    # Unload gungame if they changed "gg_knife_pro" to "0"
    if cvarName == 'gg_knife_pro' and event_var['newvalue'] == '0':
        es.unload('gungame/included_addons/gg_knife_pro')

def player_death(event_var):             #PREVENTLEVEL
    global gg_knife_pro_limit
    # check for knife kill, warmup off, and no team kill
    if event_var['weapon'] == 'knife' and event_var['es_attackerteam'] != event_var['es_userteam']:
        # setup attacker
        attacker = int(event_var['attacker'])
        gungameAttacker = gungame.getPlayer(attacker)
        # check if attacker is on knife level and make sure attacker is not 'world'
        if gungameAttacker.get('weapon') != 'knife' and attacker != 0:
            # setup victim
            userid = event_var['userid']
            gungameVictim = gungame.getPlayer(userid)
            # check if victim is afk
            if not gungameVictim.get('isplayerafk'):
                # get victims level
                gungameVictimLevel = int(gungameVictim.get('level'))
                # check if there is a knife pro limit
                if gg_knife_pro_limit:
                    #  check if victim is above level 1
                    if gungameVictimLevel > 1:
                        # get attacker level
                        gungameAttackerLevel = int(gungameAttacker.get('level'))
                        # check  knife pro limit
                        if gungameAttackerLevel - gungameVictimLevel <= gg_knife_pro_limit:
                            # check if attacker is on nade
                            if gungameAttacker.get('weapon') != 'hegrenade':
                                if gungameVictim.get('PreventLevel') == 0:
                                    # trigger leveldown event
                                    gungame.triggerLevelDownEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_username'], event_var['es_userteam'], gungameVictimLevel, gungameVictimLevel - 1, attacker, event_var['es_attackername'])
                                    if gungameAttacker.get('PreventLevel') == 0:
                                        es.msg('#multi', '\x04%s\x01 stole a level from \x03%s' % (event_var['es_attackername'], event_var['es_username']))
                                else:
                                    es.tell(attacker, '#multi', '\x04%s\x01 stole a level from \x03%s' % (event_var['es_attackername'], event_var['es_username']))
                                if gungameAttacker.get('PreventLevel') == 0:
                                    # trigger levelup event
                                    gungame.triggerLevelUpEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], gungameAttackerLevel, gungameAttackerLevel + 1, userid, event_var['es_username'])
                            else:
                                # Attacker is on nade level
                                if int(gungameAttacker.get('PreventLevel')) == 0:
                                    usermsg.hudhint(attacker, 'You are on \'hegrenade\' level.\n \nYou cannot skip this level by knifing!')
                                if int(gungameVictim.get('PreventLevel')) == 0:
                                    usermsg.hudhint(userid, '%s was on \'hegrenade\' level.\n \nYou did not lose a level!' %event_var['es_attackername'])
                                    
                        else:
                            # Victim level is too low
                            if int(gungameAttacker.get('PreventLevel')) == 0:
                                usermsg.hudhint(attacker, '%s is more than %i level(s) below you.\n \nYou could not steal a level!' % (event_var['es_username'], gg_knife_pro_limit))
                            if int(gungameVictim.get('PreventLevel')) == 0:
                                usermsg.hudhint(userid, '%s is more than %i level(s) above you.\n \nYou did not lose a level!' % (event_var['es_attackername'], gg_knife_pro_limit))
                    else:
                        # Victim is on level 1
                        if gungameAttacker.get('PreventLevel') == 0:
                            usermsg.hudhint(attacker, '%s is on level 1.\n \nYou could not steal a level!' % event_var['es_username'])
                        if gungameVictim.get('PreventLevel') == 0:
                            usermsg.hudhint(userid, 'You are on level 1.\n \n%s could not steal a level!' % event_var['es_attackername'])
                else:
                    # check if victim is above level 1
                    if gungameVictimLevel > 1:
                        # get attacker level
                        gungameAttackerLevel = int(gungameAttacker.get('level'))
                        # check if attacker is on nade
                        if gungameAttacker.get('weapon') != 'hegrenade':
                            if gungameVictim.get('PreventLevel') == 0:
                                # trigger leveldown event
                                gungame.triggerLevelDownEvent(userid, playerlib.uniqueid(userid, 1), event_var['es_username'], event_var['es_userteam'], gungameVictimLevel, gungameVictimLevel - 1, attacker, event_var['es_attackername'])
                                if gungameAttacker.get('PreventLevel') == 0:
                                    es.msg('#multi', '\x04%s\x01 stole a level from \x03%s' % (event_var['es_attackername'], event_var['es_username']))
                            else:
                                es.tell(attacker, '#multi', '\x04%s\x01 stole a level from \x03%s' % (event_var['es_attackername'], event_var['es_username']))
                            if gungameAttacker.get('PreventLevel') == 0:
                                # trigger levelup event
                                gungame.triggerLevelUpEvent(attacker, playerlib.uniqueid(attacker, 1), event_var['es_attackername'], event_var['es_attackerteam'], gungameAttackerLevel, gungameAttackerLevel + 1, userid, event_var['es_username'])
                        else:
                            # Attacker is on nade level
                            if gungameAttacker.get('PreventLevel') == 0:
                                usermsg.hudhint(attacker, 'You are on \'hegrenade\' level.\n \nYou cannot skip this level by knifing!')
                            if gungameVictim.get('PreventLevel') == 0:
                                usermsg.hudhint(userid, '%s was on \'hegrenade\' level.\n \nYou did not lose a level!' %event_var['es_attackername'])
                    else:
                        # Victim is on level 1
                        if gungameAttacker.get('PreventLevel') == 0:
                            usermsg.hudhint(attacker, '%s is on level 1.\n \nYou could not steal a level!' % event_var['es_username'])
                        if gungameVictim.get('PreventLevel') == 0:
                            usermsg.hudhint(userid, 'You are on level 1.\n \n%s could not steal a level!' % event_var['es_attackername'])