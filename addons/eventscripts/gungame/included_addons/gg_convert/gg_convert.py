''' (c) 2008 by the GunGame Coding Team

    Title: gg_convert
    Version: 5.0.568
    Description: Provides a console interface which allows convertions for
                 GunGame 3 and 4 winner database and spawnpoint files to
                 GunGame 5 formats.
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python imports
import os
import time

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
info.name     = 'gg_convert (for GunGame5)'
info.version  = '5.0.568'
info.url      = 'http://gungame5.com/'
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

def unload():
    gungamelib.unregisterAddon('gg_convert')

# ==============================================================================
#   HELP
# ==============================================================================
def convert_help(userid):
    # Tell them to check their console
    gungamelib.msg('gungame', userid, 'CheckYourConsole')
    gungamelib.echo('gg_convert', userid, 0, 'HelpCommands')
    
    # Echo the lists to them
    for x in gConverts:
        if userid == 0:
            es.dbgmsg(0, '[gg_convert]  * gg_convert_%s' % x)
        else:
            usermsg.echo(userid, '[gg_convert]  * gg_convert_%s' % x)

# ==============================================================================
#   DEATHMATCH -- GUNGAME 3
# ==============================================================================
def convert_dm3(userid):
    # Tell them to check their console
    gungamelib.msg('gungame', userid, 'CheckYourConsole')
    
    # Loop through the files in the legacy folder
    for f in os.listdir(gungamelib.getGameDir('cfg/gungame5/converter/gg3 spawnpoints')):
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
            points = parseLegacySpawnpoint(gungamelib.getGameDir('cfg/gungame5/converter/gg3 spawnpoints/%s' % f), userid)
        except:
            gungamelib.echo('gg_convert', userid, 0, 'dm3:ConvertionFailed')
            #es.excepter(*sys.exc_info())
            gungamelib.logException()
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
#   DEATHMATCH -- GUNGAME 4
# ==============================================================================
def convert_dm4(userid):
    # Tell them to check their console
    gungamelib.msg('gungame', userid, 'CheckYourConsole')
    
    # Loop through the files in the legacy folder
    for f in os.listdir(gungamelib.getGameDir('cfg/gungame5/converter/gg4 spawnpoints')):
        name, ext = os.path.splitext(f)
        
        # Isn't an ES sqldb file?
        if not name.startswith('es_') or ext != '.sqldb':
            continue
        
        # Remove the es_
        name = name[3:]
        
        # Announce we are converting it
        gungamelib.echo('gg_convert', userid, 0, 'dm4:ConvertingFile', {'file': f})
        
        # Load the database into a keygroup
        es.sql('open', name, 'gungame5/converter/gg4 spawnpoints')
        es.sql('query', name, 'gg4_sp', 'SELECT * FROM spawnpoints')
        es.sql('close', name)
        
        # Open the keygroup with keyvalues
        gg4_sp = keyvalues.getKeyGroup('gg4_sp')
        
        # Create a list to store the spawnpoints
        points = []
        
        # Get spawnpoint info
        for x in gg4_sp:
            # Get info
            x = str(x)
            info = gg4_sp[x]
            
            # Prepare the spawnpoint to be added
            point = '%s %s %s %s %s 0.000000\n' % (float(info['loc_x']), float(info['loc_y']), float(info['loc_z']), float(info['eye0']), float(info['eye1']))
            
            # If the point already exists, skip it
            if point in points:
                continue
            
            # Add the point to the list
            points.append(point)
        
        # Are there any points?
        if not len(points):
            continue
        
        # Write to the file, then close it
        newFile = open(gungamelib.getGameDir('cfg/gungame5/spawnpoints/%s.txt' % name), 'w')
        newFile.writelines(points)
        newFile.close()
    
    # Announce that all files have been converted
    gungamelib.echo('gg_convert', userid, 0, 'dm4:ConvertionCompleted')

# ==============================================================================
#   WINNERS -- GUNGAME 3
# ==============================================================================
def convert_winners3(userid):
    # Tell them to check their console
    gungamelib.msg('gungame', userid, 'CheckYourConsole')
    
    # Get the file
    file = gungamelib.getGameDir('cfg/gungame5/converter/gg3 winners/es_gg_winners_db.txt')
    
    # Load the KeyValues file
    kv = keyvalues.KeyValues(name=file[3:-6])
    kv.load(file)
    
    # Loop through the winners
    for x in kv:
        x = str(x)
        
        # Check its a unique id
        if not x.startswith('STEAM_'):
            gungamelib.echo('gg_convert', userid, 0, 'winners3:SkippingNonUnique', {'name': x})
            continue
        
        # Get data
        data = kv[x]
        
        # Set winner info
        gungameWinner = gungamelib.getWinner(x)
        gungameWinner['wins'] = int(data['wins'])
        gungameWinner['name'] = data['name']
        gungameWinner['timestamp'] = time.time()
        
        # Print to console
        gungamelib.echo('gg_convert', userid, 0, 'winners3:Converted', {'name': data['name'], 'wins': data['wins'], 'uniqueid': x})
    
    completeConvert()
    
    # Completed
    gungamelib.echo('gg_convert', userid, 0, 'winners3:ConvertionCompleted')

# ==============================================================================
#   WINNERS -- GUNGAME 4
# ==============================================================================
def convert_winners4(userid):
    # Tell them to check their console
    gungamelib.msg('gungame', userid, 'CheckYourConsole')
    
    # Load the database into a keygroup
    es.sql('open', 'gg_database', 'gungame5/converter/gg4 winners')
    es.sql('query', 'gg_database', 'gg4c_db', 'SELECT * FROM gg_players')
    es.sql('close', 'gg_database')
    
    # Open the keygroup with keyvalues
    gg4db = keyvalues.getKeyGroup('gg4c_db')
    
    # Loop through the winners
    for player in gg4db:
        # Get winner info
        player = str(player)
        wins = int(gg4db[player]['wins'])
        
        # Do they have any wins? / Are they a fake player?
        if not wins:
            continue
        
        steamid = gg4db[player]['steamid']
        name = gg4db[player]['name']
        
        # Set winner info
        gungameWinner = gungamelib.getWinner(steamid)
        gungameWinner['wins'] = wins
        gungameWinner['name'] = name
        gungameWinner['timestamp'] = time.time()
        
        # Print to console
        gungamelib.echo('gg_convert', userid, 0, 'winners4:Converted', {'name': name, 'wins': wins, 'uniqueid': steamid})
    
    # Finalize convertion
    completeConvert()
    gungamelib.echo('gg_convert', userid, 0, 'winners4:ConvertionCompleted')

def completeConvert():
    # Reload the database
    gungamelib.saveWinnerDatabase()
    gungamelib.loadWinnerDatabase()
    
    # Reload gg_info_menus
    es.reload('gungame/included_addons/gg_info_menus')

# ==============================================================================
#   GLOBALS
# ==============================================================================
gConverts = {
    'help': convert_help,
    'dm3': convert_dm3,
    'dm4': convert_dm4,
    'winners3': convert_winners3,
    'winners4': convert_winners4
}