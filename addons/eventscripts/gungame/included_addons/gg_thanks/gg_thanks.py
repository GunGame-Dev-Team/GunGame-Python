''' (c) 2008 by the GunGame Coding Team

    Title: gg_thanks
    Version: 1.0.485
    Description: An addon dedicated to... everyone?!
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# Python imports
import time

# EventScripts imports
import es

# GunGame imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_thanks Addon for GunGame: Python'
info.version  = '1.0.485'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_thanks'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
credits = {
    'Lead Developer / Project Lead':
        ['XE_ManUp'],
    
    'Developers':
        ['RideGuy', 'Saul', 'HitThePipe', 'Artsemis', 'Don'],
    
    'Special Thanks':
        ['Don', 'Artsemis', 'Predator (x2!)', 'tnb=[porsche]911'],
    
    'Beta Testers':
        ['-=CsFF=- Eagle',
        '7355608',
        'Ace Rimmer',
        'aLpO',
        'Artsemis',
        'BbluE',
        'bonbon',
        'cagemonkey',
        'Chrisber',
        'Cisco',
        'CmG Knight',
        'cmoore420',
        'dajayguy',
        'danzig',
        'Defcon',
        'DerekRDenholm',
        'disconnect81',
        'Don',
        'DontWannaName',
        'emc0002',
        'Errant',
        'GoodfellaDeal',
        'HitThePipe',
        'kkrazyykkidd',
        'MDK',
        'Mjtact',
        'moethelawn',
        'monday',
        'Parah',
        'Q2',
        'RideGuy',
        'Saul',
        'Sc0pE',
        'SIL3NT-DE4TH',
        'sp90378',
        'SquirrelEater',
        'StealthAssassin',
        'Tempe Terror1',
        'The-Killer',
        'tnb=[porsche]911',
        'Predator',
        'trcjm',
        'ultima1221',
        'Wallslide',
        'Warbucks',
        'waspy',
        'Wire Wolf',
        'your-name-here',
        '{cDS} Blue Ape']
}

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_thanks = gungamelib.registerAddon('gg_thanks')
    gg_thanks.setDisplayName('GG Thanks')
    
    gg_thanks.registerAdminCommand('thanks', thanks)

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_thanks')


def thanks(userid):
    # Server console only (for overflow protection)
    if userid != 0:
        es.tell(userid, '#multi', '\4[GG Thanks] This command is for the server console only.')
        return
    
    # Loop through the credits
    for x in credits:
        # Print category
        es.dbgmsg(0, '[GG Thanks] %s:' % (x))
        
        # Show all in this category
        for y in credits[x]:
            es.dbgmsg(0, '[GG Thanks]    %s' % y)
        
        es.dbgmsg(0, '[GG Thanks] ')
        
        # Overflow protection
        time.sleep(0.1)