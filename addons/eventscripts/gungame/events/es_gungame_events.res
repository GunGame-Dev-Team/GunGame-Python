//    +-------------------------------------------------------------------------
//    |   Copyright (C) 2007-2008 Saul Rennison
//    |   Author: Saul Rennison <saul.rennison@gmail.com>
//    +-------------------------------------------------------------------------
//    |   es_gungame_events.res
//    |       GunGame event definition file.
//    |       
//    |       If a "victim" event_var is supplied, the following will also be
//    |       automagically added:
//    |         * victim_name, victim_steamid and victim_team
//    |
//    |       EventScripts automatically provides a lot of event_vars if "userid"
//    |       or "attacker" event_var's has been passed.
//    +-------------------------------------------------------------------------

"gungame_events"
{

	"gg_levelup"
	{
		"userid"	"short"		// userid of player that levelled up
		"victim"	"short"		// userid of victim
		"old_level"	"byte"		// old player level
		"new_level"	"byte"		// new player level
		"weapon"        "string"        // weapon
	}
	
	"gg_leveldown"
	{
		"userid"	"short"		// userid of player that levelled down
		"attacker"	"short"		// userid of the attacker
		"old_level"	"byte"		// old player level
		"new_level"	"byte"		// new player level
		"weapon"        "string"        // weapon
	}
	
	"gg_knife_steal"
	{
		"userid"	"short"		// The userid of the attacker
		"attacker_level" "byte"	        // The new level of the attacker
		"victim"        "short"         // The userid of victim
		"victim_level"  "byte"	        // The new level of the victim
	}
	
	"gg_new_leader"
	{
		"userid"	"short"		// The userid of the player that became the new leader
	}
	
	"gg_tied_leader"
	{
		"userid"	"short"		// The userid of the player that tied the leader(s)
	}
	
	"gg_leader_lostlevel"
	{
		"userid"	"short"		// The userid of the leader that lost a level
	}
	
	"gg_start"
	{
		// This event fires at the end of the warmup round
		// This will fire on es_map_start if there is no warmup round
	}
	
	"gg_vote"
	{
		// This event fires when a vote had started
	}
	
	"gg_win"
	{
		"userid"	"short"		// userid of player that won the game
		"loser"		"short"		// userid of player that gave up the win
	}
	
	"gg_round_win"
	{
		"userid"	"short"		// userid of player that won
		"loser"		"short"		// userid of player that gave up the win
	}
	
	"gg_map_end"
	{
		// This event fires at the end of a map when there is no winner
	}
	
	"gg_variable_changed"
	{
		"cvarname"      "string"        // The name of the cvar that was changed
		"value"         "string"        // The new value of the cvar
	}
	
	"gg_load"
	{
		// This event fires when GG is loaded
	}
	
	"gg_unload"
	{
		// This event fires when GG is unloaded
	}

}