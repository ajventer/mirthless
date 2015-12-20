# mirthless
![Screenshot from pre-release version](/screenshots/mirthless_screenshot_4.jpg?raw=true "Designing a map in the mirthless editor")
A single player RPG in which you are the evil bad guy.

https://www.facebook.com/mirthlessrpg/

Mirthless is based on (heavily modified) code from EZDM and intends to create a full fledged single player role playing game with an ADND2E ruleset in which the player gets to play a truly evil character intent on becoming a dark lord.

The story outline is complete for the main quest, lots of side quests would be good.

*Contributors wanted:*

Right now more coders would be most valuable. Once the editor is complete we'll have lots of room for artists, writers, quest designers or other game-mod types.
If you're keen to contribute in any way please join the contributors mailing list:
https://groups.google.com/forum/#!forum/mirthless-rpg--contributors

There is a lot of documentation to be written. I'll make an effort to expand the WIKI as things start approaching usable forms. Help would be greatly appreciated.

TODO list for initial release (in no particular order):

1. Clean up EZDM data files and convert to flat YAML format - DONE
  - This is needed to fix some stability issues with the way much of EZDMlibs was written) 

2. Modify EZDM libraries to utilize the new format data - DONE 
  -(well the unit tests are passing, dunno what gator-sized bugs may be lurking)

3. Rewrite the game interface in pygame replacing the current web based interface. 

  - Write the editor in pygame
  	- Map Editor - in progress
  	- NPC and Monster editor
  	- Quest editor ? 

4. New character generator suitable for a game

5. Improve the data finding system - gamedata part DONE
  - seperate player savegame data from main game data properly

6. Support for quests is missing

7. A fast-travel system for places previously discovered (low priority)

8. Support for roguelike procedural maps
 - This was previously listed as "low priority".  I did a quick test and found that a viable procedural maps algorythm was ridiculously easy to write. It would also make a great way to reduce the labour involved in making a big game. You take a fixed map as a start, add a traversal link to a procedural map (with rules to fit the theme), maybe add a few more of those and then another fixed map where the the quest concludes and it's a much bigger and more fun quest than the two fixed maps alone for almost no extra work. So I am shifting this to higher priority and must be done for 1.0.

9. Fix the json loading and file-handling code to use preloading and not spend time waiting to process stuff like EZDM does.

10. NPC AI - this can improve with time but at the very least NPCs and monsters should be able to fight - unlike in EZDM there won't be a game-master to control their actions

11. Add a platino easter egg somewhere to meet dawnhack attribution requirements.



I am going to try and get an initial playable alpha release up to the end of the opening chapter done by the end of December, more helpers will reduce that time. But the TODO list is quite long, even though the engine inheritted from EZDM is largely complete this involves quite a bit of work. So please be patient.

The built in make file can install the game:

`make install`

You can also build a debian/ubuntu/mint package instead:

`make deb`

If you prefer to track the installation.
To run the unit tests use:

`make test`

Credits:
Game art from: 

1. kenney.nl

2. http://opengameart.org/content/dawnlike-16x16-universal-rogue-like-tileset-v181

3. Adonthel

4. Fist icon from: https://openclipart.org/detail/19831/chibi-fist

The GLYPH text rendering library for pygame is included with the project and used in several parts of the interface.
http://www.pygame.org/project-Glyph-1002-2794.html

Wallpaper:
http://opengameart.org/content/landscape

Blackchancery font from: 
http://www.1001fonts.com/blackchancery-font.html
