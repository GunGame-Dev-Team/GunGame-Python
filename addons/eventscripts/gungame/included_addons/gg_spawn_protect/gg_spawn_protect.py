'''
(c)2007 by the GunGame Coding Team

    Title:      gg_spawn_protection
Version #:      12.31.2007
Description:    This will make players invincable and marked with color when
                ever a player spawns.  Protected players cannot level up during
                spawn protection.
'''

import es
import playerlib
import gamethread
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_spawn_protection Addon for GunGame: Python" 
info.version  = "08.01.2007"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_spawn_protect"
info.author   = "cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007"

# Addon settings
addonOpts = {}
addonOpts['red'] = int(gungame.getGunGameVar('gg_spawn_protect_red'))
addonOpts['green'] = int(gungame.getGunGameVar('gg_spawn_protect_green'))
addonOpts['blue'] = int(gungame.getGunGameVar('gg_spawn_protect_blue'))
addonOpts['alpha'] = int(gungame.getGunGameVar('gg_spawn_protect_alpha'))
addonOpts['delay'] = int(gungame.getGunGameVar('gg_spawn_protect'))

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_spawn_protect', 'GG Spawn Protection')

def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_spawn_protect')

def gg_variable_changed(event_var):
    # Register change in gg_map_list_file
    if event_var['cvarname'] == 'gg_spawn_protect':
        addonOpts['delay'] = int(gungame.getGunGameVar('gg_spawn_protect'))

def player_spawn(event_var):
    # If not warmup round...
    if not gungame.getRegisteredAddons().has_key('gungame\\included_addons\\gg_warmup_round'):
        # Get userid and player objects
        userid = int(event_var['userid'])
        gungamePlayer = gungame.getPlayer(userid)
        playerlibPlayer = playerlib.getPlayer(userid)
        
        # Debug
        #print 'Spawn Protect: R: %s, G: %s, B: %s, A: %s' % (addonOpts['red'], addonOpts['green'], addonOpts['blue'], addonOpts['alpha'])
        
        # Set protected settings
        gungamePlayer.set('PreventLevel', 1)
        playerlibPlayer.set('health', 999)
        playerlibPlayer.set('color', (addonOpts['red'], addonOpts['green'], addonOpts['blue'], addonOpts['alpha']))
        
        # Set un-protected settings
        gamethread.delayed(addonOpts['delay'], gungamePlayer.set, ('preventlevel', 0))
        gamethread.delayed(addonOpts['delay'], playerlibPlayer.set, ('health', 100))
        gamethread.delayed(addonOpts['delay'], playerlibPlayer.set, ('color', (255, 255, 255, 255)))
