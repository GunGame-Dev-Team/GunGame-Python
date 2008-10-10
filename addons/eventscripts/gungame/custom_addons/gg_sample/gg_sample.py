''' (c) 2008 by the GunGame Coding Team

    Title: gg_sample
    Version: 1.0.480
    Description: Custom addon test.
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python imports


# EventScripts imports
import es

# GunGame imports
import gungamelib

# ==============================================================================
#   ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'sample Addon for GunGame: Python'
info.version  = '1.0.480'
info.url      = ''
info.basename = 'gungame/custom_addons/gg_sample'
info.author   = 'GunGame Development Team'

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    addon = gungamelib.registerAddon('gg_sample')
    addon.setDisplayName('gg_sample')
    
def unload():
    gungamelib.unregisterAddon('gg_sample')