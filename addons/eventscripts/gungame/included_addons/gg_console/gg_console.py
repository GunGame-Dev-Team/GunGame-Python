''' (c) 2008 by the GunGame Coding Team

    Title: gg_console
    Version: 1.0.285
    Description: Provides console commands to be used by admins.
'''

# ==============================================================================
#   IMPORTS
# ==============================================================================
# EventScripts imports
import es

# GunGame imports
import gungamelib

# ==============================================================================
#   ADDON REGISTRATION
# ==============================================================================
# Register with EventScripts
info = es.AddonInfo()
info.name     = 'gg_console (for GunGame: Python)'
info.version  = '1.0.285'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45'
info.basename = 'gungame/included_addons/gg_console'
info.author   = 'GunGame Development Team'

# ==============================================================================
#   GAME EVENTS
# ==============================================================================
def load():
    # Register
    gg_console = gungamelib.registerAddon('gg_console')
    gg_console.setDisplayName('GG Console')
    
    # Command registration
    #  Format: registerCommand(name   , callback , syntax               )
    gg_console.registerCommand('isafk', cmd_isafk, '<variable> <userid>')

# ==============================================================================
#   CONSOLE COMMANDS
# ==============================================================================
def cmd_isafk(userid, variable, player):
    # Make sure the client is in the server
    if not gungamelib.clientInServer(player):
        gungamelib.msg('gungame', 0, 0, 'InvalidUserid', {'userid': userid})
    
    # Get player then set the variable
    playerObj = gungamelib.getPlayer(player)
    es.ServerVar(variable).set(int(playerObj.isPlayerAFK()))

"""
TODO (Gulp):

def cmd_seteyeangle():
    '''gg_seteyeangle <userid> <pitch> <yaw>
    
    Sets a player's eye angles.
    '''
    if not checkArgs(3, '<userid> <pitch> <yaw>'): return
    
    userid, pitch, yaw = gungamelib.formatArgs()
    
    if not gungamelib.clientInServer(userid):
        gungamelib.msg('gungame', 0, 0, 'InvalidUserid', {'userid': userid})
    
    player = gungamelib.getPlayer(userid)
    player.setPlayerEyeAngles(pitch, yaw)

def cmd_teleport():
    '''gg_teleport <userid> <x> <y> <z> <pitch> <yaw>
    
    Sets a player's eye angles.
    '''
    if not checkArgs(5, '<userid> <x> <y> <z> <pitch> <yaw>'): return
    
    userid, x, y, z, pitch, yaw = gungamelib.formatArgs()
    
    if not gungamelib.clientInServer(userid):
        gungamelib.msg('gungame', 0, 0, 'InvalidUserid', {'userid': userid})
    
    player = gungamelib.getPlayer(userid)
    player.teleport(x, y, z, pitch, yaw)

def cmd_resetafk():
    # gg_resetafk <userid>
    if int(es.getargc()) == 2:
        userid = es.getargv(1)
        if es.exists('userid', userid):
            gungame.resetPlayerAfk(userid)
        else:
            raise UseridError, str(userid) + ' is an invalid userid'
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def cmd_getlevel():
    # gg_getlevel <variable> <userid>
    if int(es.getargc()) == 3:
        userid = es.getargv(2)
        if es.exists('userid', userid):
            varName = es.getargv(1)
            gungamePlayer = gungamelib.getPlayer(userid)
            playerLevel = gungamePlayer['level']
            es.set(varName, playerLevel)
        else:
            raise UseridError, str(userid) + ' is an invalid userid'
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def cmd_setlevel():
    # gg_setlevel <userid> <level>
    if int(es.getargc()) == 3:
        userid = es.getargv(1)
        if es.exists('userid', userid):
            varName = es.getargv(2)
            gungamePlayer = gungamelib.getPlayer(userid)
            gungamePlayer.set('level', es.getargv(2))
        else:
            raise UseridError, str(userid) + ' is an invalid userid'
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def cmd_gungamelib.getLeaderLevel():
    # gg_gungamelib.getLeaderLevel <variable>
    if int(es.getargc()) == 2:
        varName = es.getargv(1)
        leaderLevel = gungame.gungamelib.getLeaderLevel()
        es.set(varName, leaderLevel)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def cmd_getgungamevar():
    # gg_getgungamevar <variable> <variable name>
    if int(es.getargc()) == 3:
        varName = es.getargv(1)
        queriedVar = es.getargv(2)
        gungamelib.getVariableValue(varName)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'
        
def cmd_setgungamevar():
    # gg_setgungamevar <variable name> <value>
    if int(es.getargc()) == 3:
        varName = es.getargv(1)
        varValue = es.getargv(2)
        gungamelib.setVariableValue(varName, varValue)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def cmd_getpreventlevel():
    # gg_getpreventlevel <variable> <userid>
    if int(es.getargc()) == 3:
        varName = es.getargv(1)
        userid = es.getargv(2)
        gungamePlayer = gungamelib.getPlayer(userid)
        es.set(varName, gungamePlayer.get('preventlevel'))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'
        
def cmd_setpreventlevel():
    # gg_setgungamevar <userid> <0 | 1>
    if int(es.getargc()) == 3:
        userid = es.getargv(1)
        preventValue = int(es.getargv(2))
        gungamePlayer = gungamelib.getPlayer(userid)
        gungamePlayer.set('preventlevel', preventValue)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def cmd_stripplayer():
    # gg_stripplayer <userid>
    if int(es.getargc()) == 2:
        userid = es.getargv(1)
        if es.exists('userid', userid):
            stripPlayer(userid)
        else:
            raise UseridError, str(userid) + ' is an invalid userid'
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def cmd_getweapon():
    # gg_getweapon <variable> <userid>
    if int(es.getargc()) == 3:
        userid = es.getargv(2)
        varName = es.getargv(1)
        gungamePlayer = gungamelib.getPlayer(userid)
        es.set(varName, dict_gungameWeaponOrder[gungamePlayer['level']])
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'
    
def cmd_giveweapon():
    # gg_giveweapon <userid>
    if int(es.getargc()) == 2:
        userid = es.getargv(1)
        giveWeapon(userid)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def cmd_gungamelib.getTotalLevels():
    if int(es.getargc()) == 2:
        varName = es.getargv(1)
        es.set(varName, gungamelib.getTotalLevels())
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def cmd_setweapons():
    # gg_setweapons < #default | #random | #reversed >
    if int(es.getargc()) == 2:
        weaponOrder = es.getargv(1).lower()
        gungamelib.setVariableValue('gg_weapon_order', weaponOrder)
        setWeapons(weaponOrder)
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def cmd_setweaponorderfile():
    # gg_setweaponorderfile <Path to File>
    if int(es.getargc()) == 2:
        weaponOrderFile = es.getargv(1)
        gungamelib.setVariableValue('gg_weapon_order_file', weaponOrderFile)
        setWeaponOrderFile(gungamelib.getVariableValue('gg_weapon_order_file'))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'
        
def cmd_registeraddon():
    #gg_registeraddon <Path to Script> <Script Name>
    if int(es.getargc()) == 3:
        registerAddon(str(es.getargv(1)), es.getargv(2))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def cmd_unregisteraddon():
    #gg_unregisteraddon <Path to Script>
    global dict_gungameRegisteredAddons
    if int(es.getargc()) == 2:
        # addonName = es.getargv(1)
        unregisterAddon(str(es.getargv(1)))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def cmd_getregisteredaddons():
    #gg_getregisteredaddons <variable>
    global dict_gungameRegisteredAddons
    if int(es.getargc()) == 2:
        keygroupName = es.getargv(1)
        if es.exists('keygroup', keygroupName):
            es.keygroupdelete(keygroupName)
        es.keygroupcreate(keygroupName)
        keygroup_registeredAddons = keyvalues.getKeyGroup(keygroupName)
        keygroup_registeredAddons['addons'] = keyvalues.KeyValues(name='addons')
        for addonName in dict_gungameRegisteredAddons:
            keygroup_registeredAddons['addons'][addonName] = dict_gungameRegisteredAddons[addonName]
            
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def cmd_registerdependency():
    #gg_registerdependency <Path to Script> <Script Name>
    if int(es.getargc()) == 3:
        registerAddon(str(es.getargv(1)), es.getargv(2))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 2'

def cmd_loadcustom():
    #gg_loadcustom <addonName>
    global dict_gungameRegisteredAddons
    if int(es.getargc()) == 2:
        # addonName = es.getargv(1)
        loadCustom(es.getargv(1))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'

def cmd_unloadcustom():
    #gg_unloadcustom <addonName>
    global dict_gungameRegisteredAddons
    if int(es.getargc()) == 2:
        # addonName = es.getargv(1)
        unloadCustom(es.getargv(1))
    else:
        raise ArgumentError, str(int(es.getargc()) - 1) + ' is the amount of arguments provided. Expected: 1'
"""