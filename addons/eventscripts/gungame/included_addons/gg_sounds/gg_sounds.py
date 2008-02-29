'''
(c)2008 by the GunGame Coding Team

    Title:      gg_sounds
Version #:      1.0.102
Description:    When a player makes 3 levels in one round he get faster and have an effect for 10 secs
'''

import es, os
import ConfigParser
import gungamelib
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = "gg_sounds Addon for GunGame: Python" 
info.version  = "1.0.102"
info.url      = "http://forums.mattie.info/cs/forums/viewforum.php?f=45" 
info.basename = "gungame/included_addons/gg_sounds" 
info.author   = "GunGame Development Team"

global gg_sounds
gg_sounds = {}

soundPackINI                = ConfigParser.ConfigParser()
gameDir                     = es.ServerVar('eventscripts_gamedir')
soundPackName               = gungamelib.getVariableValue('gg_soundpack')
soundPackPath               = gameDir + '/cfg/gungame/sound_packs/' + soundPackName + '.ini'
soundFolder                 = gameDir + '/sound/'
list_validSoundPackOptions  = ['levelup',
                               'leveldown',
                               'levelsteal', 
                               'nadelevel',
                               'knifelevel',
                               'triplelevel',
                               'welcome',
                               'winner',
                               'handicap']

def load():
    # Register this addon with GunGame
    gungame.registerAddon('gg_sounds', 'GG Sounds')
    
    readSoundPack()
    
def unload():
    # Unregister this addon with GunGame
    gungame.unregisterAddon('gg_sounds')

def readSoundPack():
    soundPackName               = gungamelib.getVariableValue('gg_soundpack')
    soundPackPath               = gameDir + '/cfg/gungame/sound_packs/' + soundPackName + '.ini'
    soundPackINI.read(soundPackPath)

    # Loop through each section (should only be 1) in the soundpack INI
    for section in soundPackINI.sections():
        # Loop through each option in the soundpack INI
        for option in soundPackINI.options(section):
            # Make sure that the option is valid
            if option in list_validSoundPackOptions:
                soundFile = soundPackINI.get(section, option)
                # Check to make sure they don't have the option set to "0" ... this means they want no sound for whatever event triggers it
                if soundPackINI.get(section, option) != '0':
                    # Check to make sure that the sound file exists
                    if os.path.isfile(soundFolder + soundFile):
                        # ADD THE SOUND HERE...
                        gg_sounds[option] = soundFile
                    else:
                        # The sound does not exist ... let's let them know
                        es.dbgmsg(0, soundFolder + soundFile + ' does NOT exist...')
                        # Load defaults here if the sound pack has an error.
                        gungamelib.setVariableValue('gg_soundpack', 'default')
                        # Notify them that we have changed the soundpack
                        es.dbgmsg(0, 'The sound pack \'%s\' is corrupted. Loading the GunGame default sounds.' %soundPackName)
                else:
                    # They have the sound disabled for this option. We'll set it to "0" in the gg_sounds dictionary
                    gg_sounds[option] = soundFile
            else:
                # The option is not valid...let's let them know
                es.dbgmsg(0, 'The \'%s\' option is invalid ... skipping.' %option)
    addSounds()

def addSounds():
    for soundName in gg_sounds:
        if gg_sounds[soundName] != '0':
            es.stringtable('downloadables', 'sound/' + gg_sounds[soundName])
    
def gg_levelup(event_var):
    userid = event_var['userid']
    if int(gungamelib.getVariableValue('gg_knife_pro')) > 0:
        if event_var['weapon'] == 'knife':
            if gg_sounds['levelsteal'] != '0':
                es.playsound(userid, gg_sounds['levelsteal'], 1.0)
        else:
            es.playsound(userid, gg_sounds['levelup'], 1.0)
    else:
        if gg_sounds['levelup'] != '0':
            es.playsound(userid, gg_sounds['levelup'], 1.0)
    gungamePlayer = gungamelib.getPlayer(userid)
    playerWeapon = gungamePlayer.getWeapon()
    if playerWeapon == 'hegrenade':
        if gg_sounds['nadelevel'] != '0':
            es.playsound(userid, gg_sounds['nadelevel'], 1.0)
    if playerWeapon == 'knife':
        if gg_sounds['knifelevel'] != '0':
            es.playsound(userid, gg_sounds['knifelevel'], 1.0)

def gg_leveldown(event_var):
    if gg_sounds['leveldown'] != '0':
        es.playsound(event_var['userid'], gg_sounds['leveldown'], 1.0)

def player_team(event_var):
    if int(event_var['team']) > 1:
        if gg_sounds['welcome'] != '0':
            es.playsound(event_var['userid'], gg_sounds['welcome'], 1.0)

def es_map_start(event_var):
    addSounds()

def server_cvar(event_var):
    if event_var['cvarname'] == 'gg_soundpack':
        readSoundPack()
            