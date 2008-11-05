''' (c) 2008 by the GunGame Coding Team

    Title: gg_thanks
    Version: 5.0.522
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
info.name     = 'gg_thanks (for GunGame5)'
info.version  = '5.0.522'
info.url      = 'http://gungame5.com/'
info.basename = 'gungame/included_addons/gg_thanks'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
credits = {
    'Project Leaders':
        ['XE_ManUp',
        'RideGuy'],
    
    'Developers':
        ['Saul',
        'HitThePipe',
        'Artsemis',
        'Don',
        'Sc0pE',
        'Goodfelladeal',
        'cagemonkey'],
    
    'Beta Testers':
        ['-=CsFF=- Eagle',
        'Ace Rimmer',
        'aLpO',
        'bonbon',
        'cagemonkey',
        'Chrisber',
        'Cisco',
        'CmG Knight',
        'dajayguy',
        'danzig',
        'DerekRDenholm',
        'disconnect81',
        'DontWannaName',
        'emc0002',
        'Errant',
        'GoodfellaDeal',
        'Hacker Killer'
        'moethelawn',
        'monday',
        'Q2',
        'SIL3NT-DE4TH',
        'sp90378',
        'SquirrelEater',
        'StealthAssassin',
        'Tempe Terror1',
        'tnb=[porsche]911',
        'Predator',
        'Wallslide',
        'Warbucks',
        'waspy',
        'Wire Wolf',
        'your-name-here',
        '{cDS} Blue Ape'],
        
    'Special Thanks':
        ['Predator',
        'tnb=[porsche]911',
        'your-name-here',
        'RG3 Community',
        'counter-strike.com',
        'quantum-servers.com',
        'Steven Crothers',
        'The Cheebs'],
}

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    # Register addon with gungamelib
    gg_thanks = gungamelib.registerAddon('gg_thanks')
    gg_thanks.setDisplayName('GG Thanks')
    gg_thanks.loadTranslationFile()
    
    gg_thanks.registerPublicCommand('thanks', thanks)

def unload():
    # Unregister this addon with gungamelib
    gungamelib.unregisterAddon('gg_thanks')


def thanks(userid):
    gungamelib.msg('gg_thanks', userid, 'CheckConsole')
    
    # Get the categories
    categories = credits.keys()
    
    es.cexec(userid, 'echo [GG Thanks] ')
    # Loop through the credits
    for x in ('Project Leaders', 'Developers', 'Beta Testers', 'Special Thanks'):
        # Print category
        es.cexec(userid, 'echo [GG Thanks] %s:' % (x))
        
        # Show all in this category
        for y in credits[x]:
            es.cexec(userid, 'echo [GG Thanks]    %s' % y)
        
        es.cexec(userid, 'echo [GG Thanks] ')