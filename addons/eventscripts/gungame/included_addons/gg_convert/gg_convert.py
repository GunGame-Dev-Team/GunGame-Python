''' (c) 2008 by the GunGame Coding Team

    Title: gg_convert
    Version: 1.0.340
    Description: Provides a console interface which allows convertions from
                 GunGame 3 and 4 are available for usage in GunGame:Python.
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

# EventScripts imports
import es
import usermsg

# GunGame imports
import gungamelib

# ==============================================================================
#   ADDON REGISTRATION
# ==============================================================================
# Register with EventScripts
info = es.AddonInfo()
info.name     = 'gg_convert (for GunGame: Python)'
info.version  = '1.0.340'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_console'
info.author   = 'GunGame Development Team'

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    gg_convert = gungamelib.registerAddon('gg_convert')
    gg_convert.setDisplayName('GG Converter')
    
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
    for f in os.listdir(gungamelib.getGameDir('cfg/gungame/spawnpoints/legacy')):
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
            points = parseLegacySpawnpoint(gungamelib.getGameDir('cfg/gungame/spawnpoints/legacy/%s' % f), userid)
        except:
            gungamelib.echo('gg_convert', userid, 0, 'dm3:ConvertionFailed')
            continue
        
        # Are there any points?
        if not points:
            continue
        
        # Now write it to a file
        newFileName = name[3:-3]
        newFile = open(gungamelib.getGameDir('cfg/gungame/spawnpoints/%s.txt' % newFileName), 'w')
        
        # Loop through the points
        for point in points:
            newFile.write('%s %s %s 0.000000 0.000000 0.000000\n' % (points[point][0], points[point][1], points[point][2]))
        
        # Close the file
        newFile.close()
    
    # Announce that all files have been converted
    gungamelib.echo('gg_deathmatch', userid, 0, 'dm3:ConvertingCompleted')

def parseLegacySpawnpoint(file, userid=0):
    # Create vars
    points = {}
    
    # Load the keygroup file
    kv = keyvalues.KeyValues(name=file[3:-6])
    kv.load(file)
    
    # Get the total points
    totalVals = int(kv['total']['total'])+1
    
    # Loop through the values
    for x in [str(x) for x in range(0, totalVals)]:
        # Try to get this value
        try:
            split = kv['points'][x]
        except KeyError:
            gungamelib.echo('gg_convert', userid, 0, 'dm3:InvalidTotal')
            return points
        
        # Split it
        points[i] = split.split(',')
    
    return points

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
