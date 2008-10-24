''' (c) 2008 by the GunGame Coding Team

    Title: gg_convert
    Version: 1.0.493
    Description: Provides a console interface which allows convertions from
                 GunGame 3 and 4 are available for usage in GunGame 5.
'''

'''XXX Todo:
 - gg3: deathmatch [DONE]
 - gg4: deathmatch [TODO]
 - gg3: winners    [TODO]
 - gg4: winners    [TODO]
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python imports
import os
import sys

# EventScripts imports
import es
import usermsg
import keyvalues

# GunGame imports
import gungamelib

# ==============================================================================
#   ADDON REGISTRATION
# ==============================================================================
# Register with EventScripts
info = es.AddonInfo()
info.name     = 'gg_convert (for GunGame: Python)'
info.version  = '1.0.493'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_console'
info.author   = 'GunGame Development Team'

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    gg_convert = gungamelib.registerAddon('gg_convert')
    gg_convert.setDisplayName('GG Converter')
    gg_convert.loadTranslationFile()
    
    for name in gConverts:
        gg_convert.registerAdminCommand('convert_' + name, gConverts[name])

# ==============================================================================
#   HELP
# ==============================================================================
def convert_help(userid):
    # Tell them to check their console
    gungamelib.msg('gungame', userid, 'CheckYourConsole')
    gungamelib.echo('gg_convert', userid, 0, 'HelpCommands')
    
    # Echo the lists to them
    for x in gConverts:
        usermsg.echo(userid, '[gg_convert]  * gg_convert_%s' % x)

# ==============================================================================
#   DEATHMATCH -- GUNGAME 3
# ==============================================================================
def convert_dm3(userid):
    # Tell them to check their console
    gungamelib.msg('gungame', userid, 'CheckYourConsole')
    
    # Loop through the files in the legacy folder
    for f in os.listdir(gungamelib.getGameDir('cfg/gungame5/spawnpoints/legacy')):
        name, ext = os.path.splitext(f)
        
        # Isn't a text file?
        if ext != '.txt':
            continue
        
        # Is not a KeyValues file?
        if not name.startswith('es_') or not name.endswith('_db'):
            continue
        
        # Announce we are parsing it
        gungamelib.echo('gg_convert', userid, 0, 'dm3:ConvertingFile', {'file': f})
        
        # Parse it
        try:
            points = parseLegacySpawnpoint(gungamelib.getGameDir('cfg/gungame5/spawnpoints/legacy/%s' % f), userid)
        except:
            gungamelib.echo('gg_convert', userid, 0, 'dm3:ConvertionFailed')
            es.excepter(*sys.exc_info())
            continue
        
        # Are there any points?
        if not points:
            continue
        
        # Now write it to a file
        newFileName = name[3:-3]
        newFile = open(gungamelib.getGameDir('cfg/gungame5/spawnpoints/%s.txt' % newFileName), 'w')
        
        # Loop through the points
        for point in points:
            newFile.write('%s %s %s 0.000000 0.000000 0.000000\n' % (point[0], point[1], point[2]))
        
        # Close the file
        newFile.close()
    
    # Announce that all files have been converted
    gungamelib.echo('gg_convert', userid, 0, 'dm3:ConvertionCompleted')

def parseLegacySpawnpoint(file, userid=0):
    # Initialise variables
    smallFile = file.split('/')[-1]
    
    # Load the KeyValues file
    kv = keyvalues.KeyValues(name=file[3:-6])
    kv.load(file)
    
    # Get the total points
    totalVals = int(kv['total']['total'])+1
    
    # Loop through the values
    for i in [str(x) for x in xrange(1, totalVals)]:
        # Try to get this value
        try:
            point = kv['points'][i]
        except KeyError:
            gungamelib.echo('gg_convert', userid, 0, 'dm3:InvalidTotal', {'file': smallFile})
            return
        
        # Split it
        yield point.split(',')

# ==============================================================================
#   GLOBALS
# ==============================================================================
gConverts = {
    'help': convert_help,
    'dm3': convert_dm3,
    #'dm4': convert_dm4,
    #'winners3': convert_winners3,
    #'winners4': convert_winners4
}
