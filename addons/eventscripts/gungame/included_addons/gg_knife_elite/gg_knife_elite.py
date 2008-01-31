'''
(c)2007 by the GunGame Coding Team

    Title:      gg_knife_elite
Version #:      1.0.102
Description:    After a player levels up, they only get a knife until the next round.
                THIS WILL OVERRIDE TURBO MODE!!
'''

import es
import playerlib
import gamethread
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_knife_elite Addon for GunGame: Python" 
info.version  = "1.0.102"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_knife_elite" 
info.author   = "GunGame Development Team"

list_allWeapons = ['glock', 'usp', 'p228', 'deagle', 'elite', 'fiveseven', 'awp', 'scout', 'aug', 'mac10', 'tmp', 'mp5navy', 'ump45', 'p90', 'galil', 'famas', 'ak47', 'sg552', 'sg550', 'g3sg1', 'm249', 'm3', 'xm1014', 'm4a1', 'hegrenade', 'flashbang', 'smokegrenade']
dict_playerIsElite = {}

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gg_knife_elite', 'GG Knife Elite')
    
    #Register gg_dead_strip as a dependency
    gungame.registerDependency('gg_dead_strip', 'gg_knife_elite')
    
    # Check if turbo is running
    if gungame.getGunGameVar('gg_turbo') == '1':
        # Check if gg_turbo is a dependency of any other addons
        if not gungame.checkDependency('gg_turbo'):
            # Unload gg_turbo
            gungame.setGunGameVar('gg_turbo', '0')
        else:
            # gg_turbo has depencies, show message and unload gg_knife_pro
            es.dbgmsg(0, '***WARNING***')
            es.dbgmsg(0, '* gg_knife_elite cannot unload gg_turbo')
            es.dbgmsg(0, '* is a dependency of the following addons:')
            for addon in gungame.getAddonDependencyList('gg_turbo'):
                es.dbgmsg(0, '*' + addon)
            es.dbgmsg(0, '* gg_knife_elite will be unloaded')
            es.dbgmsg(0, '*************')
            gungame.setGunGameVar('gg_knife_elite', '0')

    # Check if gg_dead_strip is running
    if gungame.getGunGameVar('gg_dead_strip') == '0':
        gungame.setGunGameVar('gg_dead_strip', '1')
        
    global dict_playerIsElite
    players = playerlib.getUseridList("#all")
    for tempid in players:
        userid = str(tempid)
        dict_playerIsElite[userid] = 0

def unload():
    #Unregister this addon with GunGame
    gungame.unregisterAddon('gg_knife_elite')
    #Register gg_deat_strip as a dependency
    gungame.unregisterDependency('gg_dead_strip', 'gg_knife_elite')

def gg_variable_changed(event_var):
    # Watch for required addon load/unload
    if event_var['cvarname'] == 'gg_turbo' and event_var['newvalue'] == '1':
        # Check if gg_turbo is a dependency of any other addons
        if not gungame.checkDependency('gg_turbo'):
            # Unload gg_turbo
            gungame.setGunGameVar('gg_turbo', '0')
            es.dbgmsg(0, 'WARNING: gg_turbo cannot be loaded while gg_knife_elite is enabled!')
        else:
            # gg_turbo has depencies, show message and unload gg_knife_pro
            es.dbgmsg(0, '***WARNING***')
            es.dbgmsg(0, '* gg_knife_elite cannot stop gg_turbo from loading')
            es.dbgmsg(0, '* gg_turbo is a dependency of the following addons:')
            for addon in gungame.getAddonDependencyList('gg_turbo'):
                es.dbgmsg(0, '* ' + addon)
            es.dbgmsg(0, '* gg_knife_elite will be unloaded')
            es.dbgmsg(0, '*************')
            gungame.setGunGameVar('gg_knife_elite', '0')

def player_spawn(event_var):
    global dict_playerIsElite
    userid = event_var['userid']
    dict_playerIsElite[userid] = 0
    gungamePlayer = gungame.getPlayer(userid)
    es.sexec(userid, 'use weapon_%s' %gungamePlayer.get('weapon'))

def item_pickup(event_var):
    global dict_playerIsElite
    userid = event_var['userid']
    if dict_playerIsElite[userid]:
        global list_allWeapons
        item = event_var['item']
        if item in list_allWeapons:
            playerlibPlayer = playerlib.getPlayer(userid)
            es.server.cmd('es_remove %i' % playerlibPlayer.get('weaponindex', item))

def gg_levelup(event_var):
    userid = event_var['userid']
    gungamePlayer = gungame.getPlayer(userid)
    if gungamePlayer.get('PreventLevel') == 0 and gungamePlayer.get('weapon') != 'knife':
        es.sexec(userid, 'use weapon_knife')
        gungame.stripPlayer(userid)
        
        global dict_playerIsElite
        dict_playerIsElite[userid] = 1