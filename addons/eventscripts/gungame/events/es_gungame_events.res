//=========== (C) Copyright 2007 GunGame 4 All rights reserved. ===========
//
// Events triggered by GunGame mod version 1.0.58
//
// No spaces in event names, max length 32
// All strings are case sensitive
// total game event byte length must be < 1024
//
// valid data key types are:
//   none   : value is not networked
//   string : a zero terminated string
//   bool   : unsigned int, 1 bit
//   byte   : unsigned int, 8 bit
//   short  : signed int, 16 bit
//   long   : signed int, 32 bit
//   float  : float, 32 bit

"gungame_events"
{
	"gg_levelup"
	{
		"userid"	"short"		// The userid of the player that levelled up
		"steamid"	"string"	// The steamid of player that levelled up
		"old_level"	"byte"		// The old level of the player that levelled up
		"new_level"	"byte"		// The new level of the player that levelled up
		"team"		"byte"		// The team # of the player that levelled up: team 2= Terrorists, 3= CT
		"name"		"string"	// The name of the player that levelled up
		"victim"	"short"		// The userid of victim
		"victimname" "string"	// The victim's name
        "weapon"    "string"    // The attackers weapon
	}
	"gg_leveldown"
	{
		"userid"	"short"		// userid of player
		"attacker"	"short"		// userid of the attacker
		"steamid"	"string"	// steamid of player
		"old_level"	"byte"		// old player level
		"new_level"	"byte"		// new player level
		"team"		"byte"		// player team 2= Terrorists, 3= CT
		"name"		"string"	// player name
		"attackername"	"string"	// attacker's name
	}
	"gg_win"
	{
		"userid"	"short"		// userid of player
		"steamid"	"string"	// steamid of player
		"team"		"byte"		// player team 2= Terrorists, 3= CT
		"name"		"string"	// player name
		"loser"		"short"		// userid of player that gave up the win
	}
	"gg_start"
	{
		// No event_vars for this event
		// This event only fires at the end of the warmup round
		// This will fire on es_map_start if there is no warmup round
	}
	"gg_vote"
	{
		// No event_vars for this event
		// This event only fires when the leader has reached the max level - 2
		// and no other scripts has set the nextmap and a vote has not already been started
    }
    "gg_variable_changed"
    {
        "cvarname"  "string"    // The name of the GunGame cvar that was changed
        "oldvalue"  "string"    // The old value of the GunGame cvar that was changed
        "newvalue"  "string"    // The new value of the GunGame cvar that was changed
    }
    "gg_load"
    {
		// No event_vars for this event
		// This event only fires when gungame is loaded
    }
    "gg_unload"
    {
		// No event_vars for this event
		// This event only fires when gungame is unloaded
    }
}
