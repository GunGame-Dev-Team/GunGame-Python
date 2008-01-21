#!/usr/bin/env python
'''
================================================================================
    All content copyright (c) 2008, GunGame Coding Team
================================================================================
    Name: gg_dissolver
    Main Author: Saul Rennison
    Version: 1.0.58 (21.01.2008)
================================================================================
    When players die, their ragdoll will dissolve. With the added option to
    disable this addon.
================================================================================
'''

# System imports

# Eventscripts imports
import es
import gamethread

# Gungame import
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_dissolver (for GunGame: Python)"
info.version  = "1.0.58 (21.01.2008)"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_dissolver"
info.author   = "Saul (cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2008)"

# Get the addon cvars
addonCVars = {}
addonCVars['ragdoll_effect'] = int(gungame.getGunGameVar('gg_dissolver_effect'))

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gungame/included_addons/gg_dissolver', 'GG Dissolver')
    
def unload():
    # UnRegister this addon with GunGame
    gungame.unregisterAddon('gungame/included_addons/gg_dissolver')

def player_death(event_var):
    # Set vars
    userid = int(event_var['userid'])
    
    # Just remove the ragdoll?
    if addonCVars['ragdoll_effect'] == 0:
        gamethread.delayed(2, es.server.cmd, 'es_xfire %s cs_ragdoll Kill' % userid)
    else:
        # Give the entity dissolver and set its KeyValues
        es.server.cmd('es_xgive %s env_entity_dissolver' % userid)
        es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "target cs_ragdoll"' % userid)
        es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "magnitude 1"' % userid)
        es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "dissolvetype %s"' % (userid, addonCVars['ragdoll_effect'] - 1))
        
        # Dissolve the ragdoll then kill the dissolver
        gamethread.delayedname(1, userid, es.server.cmd, 'es_xfire %s env_entity_dissolver Dissolve' % userid)
        gamethread.delayedname(6, userid, es.server.cmd, 'es_xfire %s env_entity_dissolver Kill' % userid)