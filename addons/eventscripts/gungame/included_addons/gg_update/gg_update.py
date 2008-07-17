''' (c) 2008 by the GunGame Coding Team

    Title: gg_update
    Version: 1.0.402
    Description: This addon automatically updates GunGame:Python from the
                 latest SVN revision.
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# Python Imports
import sys
import os
import urllib2
from BeautifulSoup import BeautifulSoup

# EventScripts Imports
import es
import gamethread

# GunGame Imports
import gungamelib

# ==============================================================================
#   ADDON REGISTRATION
# ==============================================================================
# Register with EventScripts
info = es.AddonInfo()
info.name     = 'gg_update (for GunGame: Python)'
info.version  = '1.0.400'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_update'
info.author   = 'GunGame Development Team'

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    # Register addon
    gg_update = gungamelib.registerAddon('gg_update')
    gg_update.setDisplayName('GG Updater')
    
    # Update
    update()

def unload():
    gungamelib.unregisterAddon('gg_update')


def es_map_start(event_var):
    # Check that we update on map start
    if gungamelib.getVariableValue('gg_update') != 1:
        gungamelib.echo('gg_update', 0, 0, 'MapStartDisabled')
    
    # Commence update
    update()

# ==============================================================================
#   HELPER FUNCTIONS
# ==============================================================================
def getLatestVersion():
    # Open the page
    page = urllib2.urlopen('http://code.google.com/p/gungame-python/source/list').read()
    soup = BeautifulSoup(page)
    
    return int(soup.find('td', {'class': 'id'}).a['href'][9:])

def checkVersion(latestRevision=False):
    currentRevision = int(str(es.ServerVar('eventscripts_ggp')).split('.')[2])
    
    if not latestRevision:
        latestRevision = getLatestVersion()
    
    if latestRevision > currentRevision:
        return 1
    elif latestRevision < currentRevision:
        return -1
    else:
        return 0

def update():
    # Get variables
    latestRevision = getLatestVersion()
    thisRevision = int(str(es.ServerVar('eventscripts_ggp')).split('.')[2])
    remainingRevisions = latestRevision-thisRevision
    updateRan = False
    
    # Get last updated revision
    dataFile = open(gungamelib.getGameDir('addons/eventscripts/gungame/data/updatedata.txt'), 'r')
    savedRevision = int(dataFile.read())
    dataFile.close()
    
    gungamelib.echo('gg_update', 0, 0, 'Started')
    
    # Any need to update?
    if remainingRevisions <= 0:
        gungamelib.echo('gg_update', 0, 0, 'LatestVersion')
        return
    else:
        gungamelib.echo('gg_update', 0, 0, 'UpdateAvailable', {'remaining': remainingRevisions})
    
    # Keep updating the files until we get the the latest revision
    for x in range(1, remainingRevisions+1):
        y = thisRevision+x
        
        # Have we already updated to this revision before?
        if y <= savedRevision:
            gungamelib.echo('gg_update', 0, 0, 'ExistingRevision')
            continue
        
        try:
            forceUpdateToRevision(y)
        except Exception, e:
            gungamelib.echo('gg_update', 0, 0, 'UpdateError', {'rev': y})
            
            # Print the error out
            es.dbgmsg(0, ' ')
            es.excepter(*sys.exc_info())
            es.dbgmsg(0, ' ')
            
            gungamelib.echo('gg_update', 0, 0, 'RecommendManualUpdate')
            return
        
        updateRan = True
    
    # Restart GunGame
    if updateRan:
        gungamelib.echo('gg_update', 0, 0, 'Restarting')
        es.delayed(1, 'es_reload gungame')

def forceUpdateToRevision(rev):
    gungamelib.echo('gg_update', 0, 0, 'Downloading', {'rev': rev})
    
    # Open the page
    try:
        page = urllib2.urlopen('http://code.google.com/p/gungame-python/source/detail?r=%s' % rev).read()
    except Exception, e:
        gungamelib.echo('gg_update', 0, 0, 'ReadError', {'rev': rev})
        
        # Print the error out
        es.dbgmsg(0, ' ')
        es.excepter(*sys.exc_info())
        es.dbgmsg(0, ' ')
        
        gungamelib.echo('gg_update', 0, 0, 'RecommendManualUpdate')
        return
    
    # Get the soup of it
    soup = BeautifulSoup(page, convertEntities='html')
    
    # Get the log message
    logMessageLines = soup.find('pre', {'style': 'margin-left:1em'}).renderContents().split('\n')
    
    # Print the log message
    es.dbgmsg(0, '[GG Updater] ------------------------------')
    gungamelib.echo('gg_update', 0, 0, 'StartLogMessage')
    es.dbgmsg(0, '[GG Updater]')
    [es.dbgmsg(0, '[GG Updater] \t' + x) for x in logMessageLines]
    es.dbgmsg(0, '[GG Updater]')
    gungamelib.echo('gg_update', 0, 0, 'EndLogMessage')
    es.dbgmsg(0, '[GG Updater] ------------------------------')
    
    # Initialize variables
    modified = []
    added    = []
    removed  = []
    
    # Loop through the modified files
    for x in soup.findAll('td', text='Modified'):
        # Get the file name
        x = x.findNext('a').renderContents()
        
        # Skip wiki files
        if x.startswith('/wiki/'):
            gungamelib.echo('gg_update', 0, 0, 'SkippingWiki')
            continue
        
        # Add to modified list
        modified.append(x[7:])
    
    # Loop through the added files
    for x in soup.findAll('td', text='Added'):
        # Get the file name
        x = x.findNext('a').renderContents()
        
        # Skip wiki files
        if x.startswith('/wiki/'):
            gungamelib.echo('gg_update', 0, 0, 'SkippingWiki')
            continue
        
        # Add to modified list
        added.append(x[7:])
    
    # Loop through the deleted files
    for x in soup.findAll('td', text='Deleted'):
        # Get the file name
        x = x.findNext('a').renderContents()
        
        # Skip wiki files
        if x.startswith('/wiki/'):
            gungamelib.echo('gg_update', 0, 0, 'SkippingWiki')
            continue
        
        # Add to modified list
        removed.append(x[7:])
    
    # Remove removed files
    for x in removed:
        y = gungamelib.getGameDir(x)
        
        # Does the file exist?
        if not os.path.exists(y):
            continue
        
        # Is a directory
        if os.path.isdir(y):
            # Remove all the files in the directory
            for f in os.listdir(y):
                os.remove(os.path.join(y, f))
                gungamelib.echo('gg_update', 0, 0, 'RemovedFile', {'x': '%s/%s' % (x, f)})
            
            os.rmdir(y)
            gungamelib.echo('gg_update', 0, 0, 'RemovedDirectory', {'x': x})
        
        # Is a file
        else:
            os.remove(y)
            gungamelib.echo('gg_update', 0, 0, 'RemovedFile', {'x': x})
    
    # Add added files
    for x in added:
        y = gungamelib.getGameDir(x)
        
        # Skip adding of file / directory if it already exists
        if os.path.exists(y):
            continue
        
        # Is a file
        if '.' in y:
            open(y, 'w')
            gungamelib.echo('gg_update', 0, 0, 'AddedFile', {'x': x})
        
        # Is a directory
        else:
            os.mkdir(y)
            gungamelib.echo('gg_update', 0, 0, 'AddedDirectory', {'x': x})
    
    # Modify modified files
    for x in modified:
        y = gungamelib.getGameDir(x)
       
        # Skip config files
        if x.endswith('.cfg'):
            gungamelib.echo('gg_update', 0, 0, 'SkippedFile', {'x': x})
            continue
        
        # Get the extension
        ext = os.path.splitext(x)[1][1:]
        
        # Is a Python file?
        if ext == 'py' and os.path.isfile(y+'c'):
            # Remove the .pyc file
            os.remove(y+'c')
        
        # Get file lines from the SVN
        newFile = urllib2.urlopen('http://gungame-python.googlecode.com/svn/trunk/%s' % x).read()
        
        # Write new lines to file
        file = open(gungamelib.getGameDir(x), 'wb')
        file.write(newFile)
        file.close()
        
        gungamelib.echo('gg_update', 0, 0, 'ModifiedFile', {'x': x})
    
    # Add new revision to the data file
    dataFile = open(gungamelib.getGameDir('addons/eventscripts/gungame/data/updatedata.txt'), 'w')
    dataFile.write(str(rev))
    dataFile.close()