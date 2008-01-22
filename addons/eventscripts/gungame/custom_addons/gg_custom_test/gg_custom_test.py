# dummy file just so something shows up in the custom addons folder

import es
from gungame import gungame

def load():
    # Register this addon with GunGame
    gungame.registerAddon("gungame/custom_addons/gg_custom_test", "GG Custom Test")
    
def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon("gungame/custom_addons/gg_custom_test")