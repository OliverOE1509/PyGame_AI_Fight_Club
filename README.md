# PyGame_AI_Fight_Club
Bootleg fireworks &amp; Shit

Two options to play:
 a. multiplayer (splitscreen)
 b. multiplayer (over network)

To play, you must run server.py regardless to initialize the server. This needs to be done only once
Then you need to find your ip address and paste this into network.py, and into self.address in the __init__ function.
Once this is done

a:
1. For splitscreen, run server.py on an python instance
2. run py_game_test.py on a separate instance

b:
1. For multiplayer, run server.py
2. run pygame_GAME.py on a separate instance
