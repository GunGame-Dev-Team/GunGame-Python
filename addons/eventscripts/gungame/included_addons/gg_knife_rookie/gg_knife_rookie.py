''' (c) 2008 by the GunGame Coding Team

    Title: gg_knife_rookie
    Version: 1.0.335
    Description:    This is the same as gg_knife_pro, but a few small
                    differences. When one player knife kills another player,
                    the attacker will ALWAYS level up, unless on knife level.
                    The victim will always lose a level, unless the victim was
                    on level 1. Even if the victim is on level 1, the attacker
                    will gain a level.
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
info.version  = '1.0.335'
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_knife_pro"
info.author   = "GunGame Development Team"

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():    
    # Register addon with gungamelib
    gg_knife_rookie = gungamelib.registerAddon('gg_knife_rookie')
    gg_knife_rookie.setDisplayName('GG Knife Rookie')
    gg_knife_rookie.addDependency('gg_knife_pro', 0)

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_knife_rookie')


def player_death(event_var):
    # ============
    # BASIC CHECKS
    # ============
    if event_var['weapon'] != 'knife':
        return
    
    if gungamelib.getGlobal('isWarmup'):
        return
    
    # ===============
    # GET PLAYER INFO
    # ===============
    attacker = int(event_var['attacker'])
    userid = int(event_var['userid'])
    userteam = event_var['es_userteam']
    attackerteam = event_var['es_attackerteam']
    
    # =============
    # SUICIDE CHECK
    # =============
    if (attackerteam == userteam) or (userid == attacker) or (attacker == 0):
        return

    # =================
    # GET ATTACKER INFO
    # =================
    gungameAttacker = gungamelib.getPlayer(attacker)
    gungameAttackerLevel = gungameAttacker['level']
    
    # ===============
    # ATTACKER CHECKS
    # ===============
    # Fix duplicate winning
    if gungameAttackerLevel >= gungamelib.getTotalLevels():
        return
    
    # Can they levelup?
    if gungameAttacker['preventlevel'] == 1:
        gungamelib.msg('gg_knife_rookie', attacker, 'AttackerPreventLevel')
        return
    
    # Is the attacker on knife or grenade level?
    if gungameAttacker.getWeapon() in ('knife', 'hegrenade'):
        gungamelib.msg('gg_knife_rookie', attacker, 'CannotSkipThisLevel')
        return
    
    # ===============
    # GET VICTIM INFO
    # ===============
    gungameVictim = gungamelib.getPlayer(userid)
    gungameVictimLevel = gungameVictim['level']
    
    # =============
    # VICTIM CHECKS
    # =============
    # Is the victim AFK?
    if gungameVictim.isPlayerAFK():
        gungamelib.msg('gg_knife_rookie', attacker, 'VictimAFK')
        return
    
    # =============
    # LEVEL CHANGES
    # =============
    # Get level info
    gungameVictimNewLevel = gungameVictimLevel - 1
    gungameAttackerNewLevel = gungameAttackerLevel + 1
    
    # Level changes
    if gungameVictimNewLevel > 0 and gungameVictim['preventlevel'] != 1:
        gungamelib.triggerLevelDownEvent(userid, gungameVictimLevel, gungameVictimNewLevel, attacker, 'steal')
    
    gungamelib.triggerLevelUpEvent(attacker, gungameAttackerLevel, gungameAttackerNewLevel, userid, 'steal')
    
    # ===========
    # PLAY SOUNDS
    # ===========
    gungamelib.playSound(attacker, 'levelsteal')
    
    if gungameVictimNewLevel > 0 and gungameVictim['preventlevel'] != 1:
        gungamelib.playSound(userid, 'leveldown')
    
    # =====
    # EVENT
    # =====
    es.event('initialize', 'gg_knife_steal')
    es.event('setint', 'gg_knife_steal', 'attacker', attacker)
    es.event('setint', 'gg_knife_steal', 'attacker_level', gungameAttackerNewLevel)
    es.event('setint', 'gg_knife_steal', 'userid_level', gungameVictimNewLevel)
    es.event('setint', 'gg_knife_steal', 'userid', userid)
    es.event('fire', 'gg_knife_steal')
    
    # Announce the level stealing
    index = playerlib.getPlayer(attacker).attributes['index']
    gungamelib.saytext2('gg_knife_rookie', '#all', index, 'StoleLevel', {'attacker': event_var['es_attackername'], 'victim': event_var['es_username']})