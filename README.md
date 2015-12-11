# mirthless
A single player RPG in which you are the evil bad guy.

Mirthless is based on (heavily modified) code from EZDM and intends to create a full fledged single player role playing game with an ADND2E ruleset in which the player gets to play a truly evil character intent on becoming a dark lord.

The story outline is complete for the main quest, lots of side quests would be good.

I will migrate EZDM files into this tree one at a time as I get to them.

TODO list for initial release (in no particular order):
1. Clean up EZDM data files and convert to flat YAML format - DONE
...* This is needed to fix some stability issues with the way much of EZDMlibs was written)
2. Modify EZDM libraries to utilize the new format data
3. Rewrite the game interface in pygame replacing the current web based interface. 
...* The editor should also get this treatment but will likely be quite a bit more work and is less urgent
...# If the editor isn't ported immediately then new format code should be backported to EZDM so that at least the browser-based editor can be used to create content.
4. New character generator suitable for a game
5. Improve the data finding system
...# seperate player savegame data from main game data properly
6. Support for quests needs is missing
7. A fast-travel system for places previously discovered (low priority)
8. Support for roguelike procedural maps (low priority)
9. Fix the json loading and file-handling code to use preloading and not spend time waiting to process stuff like EZDM does.
10. NPC AI - this can improve with time but at the very least NPCs and monsters should be able to fight - unlike in EZDM there won't be a game-master to control their actions.

I am going to try and get an initial playable alpha release up to the end of the opening chapter done by the end of December, more helpers will reduce that time. But the TODO list is quite long, even though the engine inheritted from EZDM is largely complete this involves quite a bit of work. So please be patient.

The built in make file can install the game:

`make install`

You can also build a debian/ubuntu/mint package instead:

`make deb`

If you prefer to track the installation.
To run the unit tests use:

`make test`

Game art from: kenney.nl
