'''
(c)2008 by the GunGame Coding Team

    Title:      gg_triple_level
Version #:      1.12.2008
Description:    When a player makes 3 levels in one round he get faster and have an effect for 10 secs
'''

import es
import playerlib
import gamethread
from gungame import gungame

# Register this addon with EventScripts
info = es.AddonInfo() 
info.name     = 'gg_triple_level Addon for GunGame: Python' 
info.version  = '1.5.2008'
info.url      = 'http://forums.mattie.info/cs/forums/viewforum.php?f=45' 
info.basename = 'gungame/included_addons/gg_triple_level' 
info.author   = 'cagemonkey, XE_ManUp, GoodFelladeal, RideGuy, JoeyT2007, Chrisber'

# Dic for Triple Level

def load():
	# Register this addon with GunGame
	gungame.registerAddon('gungame/included_addons/gg_triple_level', 'GG Triple Level')

def unload():
	# Unregister this addon with GunGame
	gungame.unregisterAddon('gungame/included_addons/gg_triple_level')

def gg_levelup(event_var):
	# If is it a Triple Level
	userid = event_var['userid']
	tripler = gungame.getPlayer(event_var['userid'])
	tripler.set('triple', int(tripler.get('triple')) + 1)

	if tripler.get('triple') == 3:
		# Sound and Messages
		es.emitsound('player', event_var['userid'], gungame.getGunGameVar('gg_sound_triple'), 1.0, 1.0)
		announce('\4%s\1 triple levelled!' % event_var['name'])
		es.centermsg('%s triple levelled!' % event_var['name'])
        
		# Effect to player
		es.server.cmd('es_xgive %s env_spark' %userid)
		es.server.cmd('es_xfire %s env_spark setparent !activator' %userid)
		es.server.cmd('es_xfire %s env_spark addoutput \"spawnflags 896\"' %userid)
		es.server.cmd('es_xfire %s env_spark addoutput \"angles -90 0 0\"' %userid)
		es.server.cmd('es_xfire %s env_spark addoutput \"magnitude 8\"' %userid)
		es.server.cmd('es_xfire %s env_spark addoutput \"traillength 3\"' %userid)
		es.server.cmd('es_xfire %s env_spark startspark' %userid)
        
        # Speed
		player = playerlib.getPlayer(userid)
		player.set('speed', 1.5)
        
        # Gravity (experimental)
		es.server.cmd('es_xgive %s trigger_gravity' %userid)
		es.server.cmd('es_xfire %s trigger_gravity setparent !activator' %userid)
		es.server.cmd('es_xfire %s trigger_gravity addoutput \"gravity 0.55\"' %userid)
		es.server.cmd('es_xfire %s trigger_gravity enable' %userid)

		# Reset the level counter to 0 since they just tripled
		tripler.set('triple', 0)
		
        # Stop Triple Level Bonus after 10 secs
        gamethread.delayed(10, removetriple, event_var['userid'])

def player_death(event_var):
	tripler = gungame.getPlayer(event_var['userid'])
	tripler.set('triple', 0)

def removetriple(userid):
    # Check if UserID exists
    # In the 10 secs the user maybe left
    if es.exists('userid', userid):
        # Stop Effect
		es.server.cmd('es_xfire %s env_spark stopspark' %userid)
        
        # Stop Speed
        player = playerlib.getPlayer(userid)
        player.set('speed', 1)
        
        # Stop Gravity (experimental)
		es.server.cmd('es_xfire %s trigger_gravity kill' %userid)
    else:
        # Echo debug message, the user left
        echo('Cannot remove triple bonus, the user left.')
        
def announce(message):
    es.msg('#multi', '\4[GG:Triple Level]\1 %s' % message)
   
def tell(userid, message):
    es.tell(userid, '#multi', '\4[GG:Triple Level]\1 %s' % message)

def echo(message):
    es.dbgmsg(0, '[GG:Triple Level] %s' % message)