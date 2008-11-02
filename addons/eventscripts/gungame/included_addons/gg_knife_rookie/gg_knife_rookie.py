''' (c) 2008 by the GunGame Coding Team

    Title: gg_knife_rookie
    Version: 5.0.489
    Description:    This is the same as gg_knife_pro, but a few small
                    differences. When one player knife kills another player,
                    the attacker will ALWAYS level up, unless on knife level or
                    hegrenade level. The victim will always lose a level, unless
                    the victim was on level 1. Even if the victim is on level 1,
                    the attacker will gain a level.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts imports
import es
import playerlib
import gamethread

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_knife_pro (for GunGame5)'
info.version  = '5.0.489'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_knife_pro'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():    
    # Register addon with gungamelib
    gg_knife_rookie = gungamelib.registerAddon('gg_knife_rookie')
    gg_knife_rookie.setDisplayName('GG Knife Rookie')
    gg_knife_rookie.loadTranslationFile()
    
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
    if gungameAttacker.getPreventLevel() == 1:
        gungamelib.msg('gg_knife_rookie', attacker, 'AttackerPreventLevel')
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
    # Is the attacker on knife or grenade level?
    if gungameAttacker.getWeapon() in ('knife', 'hegrenade'):
        gungamelib.msg('gg_knife_rookie', attacker, 'CannotSkipThisLevel')
    else:
        # Level up
        gungameAttacker.levelup(1, userid, 'steal')
        
        #Prevent player from levelling twice from the same knife kill
        gungameAttacker.setPreventLevel(1, 'gg_knife_rookie')
        gamethread.delayed(0, gungameAttacker.setPreventLevel, (0, 'gg_knife_rookie'))
    
        # ===========
        # PLAY SOUND
        # ===========
        gungamelib.playSound(attacker, 'levelsteal')
        
    # Level changes
    if gungameVictim.level - 1 > 0 and gungameVictim.getPreventLevel() != 1:
        # Level down
        gungameVictim.leveldown(1, attacker, 'steal')
        
        # ===========
        # PLAY SOUND
        # ===========
        gungamelib.playSound(userid, 'leveldown')
        
        # Announce the level stealing
        gungamelib.saytext2('gg_knife_rookie', '#all', gungameAttacker.index, 'StoleLevel', {'attacker': event_var['es_attackername'], 'victim': event_var['es_username']})
        
        # =====
        # EVENT
        # =====
        es.event('initialize', 'gg_knife_steal')
        es.event('setint', 'gg_knife_steal', 'attacker', attacker)
        es.event('setint', 'gg_knife_steal', 'attacker_level', gungameAttacker.level)
        es.event('setint', 'gg_knife_steal', 'userid_level', gungameVictim.level)
        es.event('setint', 'gg_knife_steal', 'userid', userid)
        es.event('fire', 'gg_knife_steal')