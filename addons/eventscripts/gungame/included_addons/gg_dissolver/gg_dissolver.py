''' (c) 2008 by the GunGame Coding Team

    Title: gg_dissolver
    Version: 5.0.558
    Description: When players die, their ragdoll will dissolve.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# Python imports
import random

# Eventscripts imports
import es
import gamethread

# Gungame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_dissolver (for GunGame5)'
info.version  = '5.0.558'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_dissolver'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
# Get the addon cvars
gg_dissolver_effect = gungamelib.getVariable('gg_dissolver_effect')

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_dissolver = gungamelib.registerAddon('gg_dissolver')
    gg_dissolver.setDisplayName('GG Dissolver')
    
def unload():
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_dissolver')


def player_death(event_var):
    # Set vars
    userid = event_var['userid']
    
    # Just remove the ragdoll?
    if int(gg_dissolver_effect) == 0:
        es.delayed('2', 'es_xfire %s cs_ragdoll Kill' % userid)
    else:
        # Give the entity dissolver and set its KeyValues
        cmdFormat = 'es_xgive %s env_entity_dissolver; ' % userid
        cmdFormat += 'es_xfire %s env_entity_dissolver AddOutput "target cs_ragdoll"; ' % userid
        cmdFormat += 'es_xfire %s env_entity_dissolver AddOutput "magnitude 1"; ' % userid
        
        # Check to see what effect to use
        if gg_dissolver_effect == 5:
            cmdFormat += 'es_xfire %s env_entity_dissolver AddOutput "dissolvetype %s"' % (userid, random.randint(0, 3))
        else:
            cmdFormat += 'es_xfire %s env_entity_dissolver AddOutput "dissolvetype %s"' % (userid, int(gg_dissolver_effect) - 1)
        
        es.server.queuecmd(cmdFormat)
        
        # Dissolve the ragdoll then kill the dissolver
        es.delayed('0.01', 'es_xfire %s env_entity_dissolver Dissolve' % userid)
        es.delayed('4', 'es_xfire %s env_entity_dissolver Kill' % userid)
        es.delayed('4', 'es_xfire %s cs_ragdoll Kill' % userid)