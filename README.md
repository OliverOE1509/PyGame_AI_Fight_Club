# PyGame_AI_Fight_Club
Bootleg fireworks &amp; Shit

A 1v1 grid-based shooter with two game modes:
- **Online Multiplayer** (via server)
- **Local Splitscreen** (single-machine)

First, to play online, you must 
1. first open the terminal
2. navigate to where you have cloned the repository
3. Ask me kindly to initiate the server, I do this with `server.py`. Since its configured for my home network, it shouldnt work outside my house. 
4. and then run
`python pygame_online.py`

It is wise to open a virtual environment where you install the requirements to avoid unnecessary packages. This should be done in the same directory as the cloned repo

You should now see a pygame window opening up. Your opponent should run the same file, and once he runs the same file, the game will be initiated and you will be able to play against eachother





**For Local splitscreen

Run `pygame_local.py` on two different terminals, read the instructions on how to play splitscreen against eachother. 

Good luck to both players.

**Furhter developments:

We will use this game to learn about reinforcement learning, teaching both agents to play against eachother. We will use this approach to further advance the playing grid to 3 dimensions and with 3 degrees of freedom in movement, and increase complexity to make real life applications more realistic.


