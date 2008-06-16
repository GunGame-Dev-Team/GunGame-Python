''' (c) 2008 by the GunGame Coding Team

    Title: gg_spawnpoints
    Version: 1.0.340
    Description: Spawnpoints manager for GunGame:Python.
'''

# ==============================================================================
#  IMPORTS
# ==============================================================================
# EventScripts Imports
import es
import playerlib
import popuplib
import spawnpointlib

# GunGame Imports
import gungamelib

# ==============================================================================
#  ADDON REGISTRATION
# ==============================================================================
# Register this addon with EventScripts
info = es.AddonInfo()
info.name     = 'gg_spawnpoints (for GunGame: Python)'
info.version  = '1.0.340'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_spawnpoints'
info.author   = 'GunGame Development Team'

# ==============================================================================
#  GLOBALS
# ==============================================================================
spawnPoints = None

# ==============================================================================
#  GAME EVENTS
# ==============================================================================
def load():
    global spawnPoints
    
    # Register addon with gungamelib
    gg_spawnpoints = gungamelib.registerAddon('gg_spawnpoints')
    
    # Menu settings
    gg_spawnpoints.createMenu(menuCallback)
    gg_spawnpoints.setDisplayName('GG Spawnpoints')
    gg_spawnpoints.setDescription('Manage this maps spawnpoints')
    gg_spawnpoints.menu.addoption('add', 'Add spawnpoint')
    gg_spawnpoints.menu.addoption('remove', 'Remove spawnpoint')
    gg_spawnpoints.menu.addoption('remove_all', 'Remove all spawnpoints')
    gg_spawnpoints.menu.addoption('show', 'Show spawnpoints')
    
    # Commands
    gg_spawnpoints.registerAdminCommand('spawn_add', cmd_spawn_add, '<userid to create at>')
    gg_spawnpoints.registerAdminCommand('spawn_remove', cmd_spawn_remove, '<index>')
    gg_spawnpoints.registerAdminCommand('spawn_remove_all', cmd_spawn_remove_all)
    gg_spawnpoints.registerAdminCommand('spawn_show', cmd_spawn_show)
    gg_spawnpoints.registerAdminCommand('spawn_print', cmd_spawn_print)
    
    # Get the spawn points for the map
    if gungamelib.inMap():
        spawnPoints = spawnpointlib.SpawnPointManager('cfg/gungame/spawnpoints')

def unload():
    global spawnPoints
    
    # Unregister this addon with GunGame
    gungamelib.unregisterAddon('gg_spawnpoints')
    
    # Un-show the spawnpoints
    if spawnPoints.getShow():
        spawnPoints.show(0)


def es_map_start(event_var):
    global spawnPoints
    
    # Reset spawnpoints
    spawnPoints = spawnpointlib.SpawnPointManager('cfg/gungame/spawnpoints')

def round_start(event_var):
    global spawnPoints
    
    # Reset spawnpoints
    if spawnPoints:
        if spawnPoints.getShow():
            spawnPoints.__resetProps()

# ==============================================================================
#   COMMANDS
# ==============================================================================
def cmd_spawn_add(userid, location):
    global spawnPoints
    
    # In map?
    if not gungamelib.inMap():
        return
    
    # Does the userid exist?
    if not gungamelib.clientInServer(location):
        gungamelib.echo('gg_spawnpoints', userid, 0, 'OperationFailed:InvalidUserid', {'userid': location})
        return
    
    # Get player info
    playerlibPlayer = playerlib.getPlayer(location)
    playerLoc = es.getplayerlocation(location)
    playerViewAngle = playerlibPlayer.get('viewangle')
    
    # Create spawnpoint
    spawnPoints.add(playerLoc[0], playerLoc[1], playerLoc[2], playerViewAngle[1])
    
    gungamelib.msg('gg_spawnpoints', userid, 'AddedSpawnpoint', {'index': spawnPoints.getTotalPoints()-1})

def cmd_spawn_remove_all(userid):
    global spawnPoints
    
    # In map?
    if not gungamelib.inMap():
        return
    
    # Do we have spawnpoints?
    if not spawnPoints.hasPoints():
        gungamelib.msg('gg_spawnpoints', userid, 'OperationFailed:NoSpawnpoints')
        return
    
    # Remove spawnpoints
    spawnPoints.deleteAll()
    
    gungamelib.msg('gg_spawnpoints', userid, 'RemovedAllSpawnpoints')

def cmd_spawn_print(userid):
    global spawnPoints
    
    # In map?
    if not gungamelib.inMap():
        return
    
    # Do we have spawnpoints?
    if not spawnPoints.hasPoints():
        gungamelib.msg('gg_spawnpoints', userid, 'OperationFailed:NoSpawnpoints')
        return
    
    # Send message
    gungamelib.echo('gg_spawnpoints', userid, 0, 'SpawnpointsFor', {'map': gungamelib.getMapName()})
    
    # Loop through the spawnpoints
    for index in spawnPoints.getIndexIter():
        # Get list
        s = spawnPoints[index]
        
        # Print to console
        gungamelib.echo('gg_spawnpoints', userid, 0, 'SpawnpointInfo', {'index': index, 'x': s[0], 'y': s[1], 'z': s[2]})
    
    # Send end message
    gungamelib.echo('gg_spawnpoints', userid, 0, 'SpawnpointsEnd')

def cmd_spawn_remove(userid, index):
    global spawnPoints
    
    # Make index an integer
    index = int(index)
    
    # In map?
    if not gungamelib.inMap():
        return
    
    # Do we have spawnpoints?
    if not spawnPoints.hasPoints():
        gungamelib.msg('gg_spawnpoints', userid, 'OperationFailed:NoSpawnpoints')
        return
    
    # Invalid index?
    if not spawnPoints.validIndex(index):
        gungamelib.msg('gg_spawnpoints', userid, 'OperationFailed:InvalidIndex')
        return
    
    spawnPoints.delete(index)
    
    # Print to console
    gungamelib.msg('gg_spawnpoints', userid, 'RemovedSpawnpoint', {'index': index})

def cmd_spawn_show(userid, toggle=None):
    global spawnPoints
    
    # In map?
    if not gungamelib.inMap():
        return
    
    # Do we have spawnpoints?
    if not spawnPoints.hasPoints():
        gungamelib.msg('gg_spawnpoints', userid, 'OperationFailed:NoSpawnpoints')
        return
    
    spawnPoints.show(toggle)

# ==============================================================================
#   MENU COMMANDS
# ==============================================================================
def menuCallback(userid, choice, popupid):
    if choice == 'add':
        sendAddMenu(userid)
    elif choice == 'remove':
        sendRemoveMenu(userid)
    elif choice == 'remove_all':
        sendRemoveAllMenu(userid)
    elif choice == 'show':
        sendShowMenu(userid)

def sendAddMenu(userid):
    # Create menu
    menu = popuplib.easymenu('gg_spawnpoints_add', None, selectAddMenu)
    menu.settitle('GG Spawnpoints: Add a spawnpoint')
    menu.setdescription('%s\n * Add a spawnpoint at which location' % menu.c_beginsep)
    
    # Add them to the menu
    menu.addoption(userid, '<Current Location>')
    
    # All all players to the menu
    for _userid in filter(lambda x: x != userid, playerlib.getUseridList('#all')):
        menu.addoption(_userid, '%s - %s' % (_userid, es.getplayername(_userid)))
    
    # Send menu
    menu.send(userid)

def selectAddMenu(userid, choice, popupid):
    # Add spawnpoint
    es.sexec(userid, 'gg_spawn_add %s' % choice)
    
    # Return to main menu
    popuplib.send('gg_spawnpoints', userid)


def sendRemoveMenu(userid):
    global spawnPoints
    
    # Create menu
    menu = popuplib.easymenu('gg_spawnpoints_remove', None, selectRemoveMenu)
    menu.settitle('GG Spawnpoints: Remove a spawnpoint')
    menu.setdescription('%s\n * Remove a spawnpoint by index' % menu.c_beginsep)
    
    # All all players to the menu
    for index in spawnPoints.getIndexIter():
        # Get location
        x, y, z, unused, roll, yaw = spawnPoints[index]
        
        # Add option
        menu.addoption(index, '%s - X: %s Y: %s Z: %s' % (index, round(float(x)), round(float(y)), round(float(z))))
    
    # Send menu
    menu.send(userid)

def selectRemoveMenu(userid, choice, popupid):
    # Get their position
    position = es.getplayerlocation(userid)
    
    # Teleport them
    gungamelib.getPlayer(userid).teleportPlayer(spawnPoints[choice][0],
                                                spawnPoints[choice][1],
                                                spawnPoints[choice][2],
                                                0,
                                                spawnPoints[choice][4])
    
    # Create menu
    menu = popuplib.easymenu('gg_spawnpoints_remove_confirm', None, selectRemoveConfirmMenu)
    menu.settitle('GG Spawnpoints: Remove this spawnpoint?')
    menu.setdescription('%s\n * Do you want to remove this spawnpoint?' % menu.c_beginsep)
    
    # Add options
    menu.addoption((choice, position), 'Yes, delete spawnpoint "%s".' % choice)
    menu.addoption((-1, position), 'No, return me to the previous menu.')
    
    # Send menu
    menu.send(userid)

def selectRemoveConfirmMenu(userid, choice, popupid):
    # Get player location
    x, y, z = choice[1]
    
    # Teleport them back
    gungamelib.getPlayer(userid).teleportPlayer(x, y, z, 0, 0)
    
    if choice[0] == -1:
        # Send them the previous menu
        sendRemoveMenu(userid)
    else:
        # Remove spawnpoint
        es.sexec(userid, 'gg_spawn_remove %s' % choice[0])
        
        # Send menu
        popuplib.send('gg_spawnpoints', userid)


def sendRemoveAllMenu(userid):
    # Create menu
    menu = popuplib.easymenu('gg_spawnpoints_remove_all_confirm', None, selectRemoveAllMenu)
    menu.settitle('GG Spawnpoints: Remove all spawnpoints?')
    menu.setdescription('%s\n * Confirmation menu' % menu.c_beginsep)
    
    # Add options
    menu.addoption(1, 'Yes, remove all spawnpoints.')
    menu.addoption(0, 'No, return me to the main menu.')
    
    # Send
    menu.send(userid)

def selectRemoveAllMenu(userid, choice, popupid):
    if choice == 1:
        # Delete spawnpoint
        es.sexec(userid, 'gg_spawn_remove_all')
        
        # Send them the main menu
        popuplib.send('gg_spawnpoints', userid)
    else:
        popuplib.send('gg_spawnpoints', userid)

def sendShowMenu(userid):
    # Create menu
    menu = popuplib.easymenu('gg_spawnpoints_show', None, selectShowMenu)
    menu.settitle('GG Spawnpoints: Show spawnpoints')
    menu.setdescription('%s\n * Select a state' % menu.c_beginsep)
    
    # Add options
    menu.addoption(0, 'Hide spawnpoint models.')
    menu.addoption(1, 'Show spawnpoint models.')
    menu.addoption(None, 'Toggle from current state.')
    
    # Send menu
    menu.send(userid)

def selectShowMenu(userid, choice, popupid):
    # Execute command
    es.sexec(userid, 'gg_spawn_show %s' % (choice if choice else ''))
    
    # Return them
    popuplib.send('gg_spawnpoints', userid)
