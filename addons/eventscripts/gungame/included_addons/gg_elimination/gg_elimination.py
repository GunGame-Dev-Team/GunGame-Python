import es
import playerlib
import gamethread

roundActive = 0
currentRound = 0
dict_playersEliminated = {}

def load():
    global dict_playersEliminated
    players = playerlib.getUseridList('#all')
    for userid in players:
        dict_playersEliminated[str(userid)] = []

def es_map_start(event_var):
    global roundActive
    global currentRound
    roundActive = 0
    currentRound = 0

def round_start(event_var):
    global roundActive
    global currentRound
    global dict_playersEliminated
    roundActive = 1
    currentRound += 1
    for player in dict_playersEliminated:
        dict_playersEliminated[player] = []
    es.msg('#multi', '#green[Elimination] #lightgreenPlayers respawn when their killer is killed')
        
def round_end(event_var):
    global roundActive
    roundActive = 0
    
def player_activate(event_var):
    global dict_playersEliminated
    userid = event_var['userid']
    if not dict_playersEliminated.has_key(userid):
        dict_playersEliminated[userid] = []

def player_disconnect(event_var):
    global dict_playersEliminated
    userid = event_var['userid']
    if dict_playersEliminated.has_key(userid):
        del dict_playersEliminated[userid]

def player_death(event_var):
    global roundActive
    global dict_playersEliminated
    if roundActive:
        userid = event_var['userid']
        attacker = event_var['attacker']
        respawnMsgFormat = ''
        if userid == attacker or attacker == '0':
            gamethread.delayed(5, respawnPlayer, (userid, currentRound))
            es.msg('#multi', '#green[Elimination] #lightgreenSuicide auto respawn: 5 seconds')
        elif event_var['es_userteam'] == event_var['es_attackerteam']:
            gamethread.delayed(5, respawnPlayer, (userid, currentRound))
            es.msg('#multi', '#green[Elimination] #lightgreenTeamkill auto respawn: 5 seconds')
        else:
            dict_playersEliminated[attacker].append(userid)
            es.msg('#multi', '#green[Elimination] #lightgreenYou will respawn when %s dies.' %event_var['es_attackername'])
        gamethread.delayed(1, respawnEliminated, (userid, currentRound))

def respawnPlayer(userid, respawnRound):
    global roundActive
    global currentRound
    if roundActive and currentRound == respawnRound:
        es.server.cmd('est_spawn %s' %userid)
        es.msg('#multi', '#green[Elimination] #lightgreenRespawning: #default%s' %es.getplayername(userid))

def respawnEliminated(userid, respawnRound):
    global roundActive
    global currentRound
    global dict_playersEliminated
    msgFormat = ''
    if roundActive and currentRound == respawnRound:
        for player in dict_playersEliminated[userid]:
            if es.exists('userid', player):
                es.server.cmd('est_spawn %s' %player)
                msgFormat = '%s%s, ' %(msgFormat, es.getplayername(player))
        if msgFormat != '':
            es.msg('#multi', '#green[Elimination] #lightgreenRespawning: #default%s' %msgFormat[0:-2])
        dict_playersEliminated[userid] = []