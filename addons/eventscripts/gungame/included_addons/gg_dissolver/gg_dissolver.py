'''
(c)2007 by the GunGame Coding Team

    Title:      gg_dissolver
Version #:      1.0.203
Description:    When players die, their ragdoll will dissolve. With the added option to
                disable this addon.
'''

# Python imports
import random

# Eventscripts imports
import es
import gamethread

# Gungame import
import gungamelib

# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = "gg_dissolver (for GunGame: Python)"
info.version  = "1.0.203"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45"
info.basename = "gungame/included_addons/gg_dissolver"
info.author   = "GunGame Development Team"

# Get the addon cvars
gg_dissolver_effect = gungamelib.getVariableValue('gg_dissolver_effect')

def load():
    # Register addon with gungamelib
    gg_dissolver = gungamelib.registerAddon('gg_dissolver')
    gg_dissolver.setMenuText('GG Dissolver')
    
def unload():
    # UnRegister this addon with GunGame
    gungamelib.unregisterAddon('gg_dissolver')
    
def server_cvar(event_var):
    # Register change for gg_dissolver_effect
    if event_var['cvarname'] == 'gg_dissolver_effect':
        gg_dissolver_effect = gungamelib.getVariableValue('gg_dissolver_effect')

def player_death(event_var):
    # Set vars
    userid = int(event_var['userid'])
    
    # Just remove the ragdoll?
    if gg_dissolver_effect == 0:
        es.delayed('2', 'es_xfire %s cs_ragdoll Kill' % userid)
    else:
        # Give the entity dissolver and set its KeyValues
        es.server.cmd('es_xgive %s env_entity_dissolver' % userid)
        es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "target cs_ragdoll"' % userid)
        es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "magnitude 1"' % userid)
        # Check to see what effect to use
        if gg_dissolver_effect == 5:
            es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "dissolvetype %s"' % (userid, random.randint(0, 3)))
        else:
            es.server.cmd('es_xfire %s env_entity_dissolver AddOutput "dissolvetype %s"' % (userid, gg_dissolver_effect - 1))
        
        # Dissolve the ragdoll then kill the dissolver
        es.delayed('0.01', 'es_xfire %s env_entity_dissolver Dissolve' % userid)
        es.delayed('4', 'es_xfire %s env_entity_dissolver Kill' % userid)
        es.delayed('4', 'es_xfire %s cs_ragdoll Kill' % userid)