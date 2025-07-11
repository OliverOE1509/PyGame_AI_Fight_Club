# PyGame_AI_Fight_Club
Bootleg fireworks &amp; Shit

A 1v1 grid-based shooter with two game modes:
- **Online Multiplayer** (via server)
- **Local Splitscreen** (single-machine)

First, to play online, you must 
1. first open the terminal
2. navigate to where you have cloned the repository
3. and then run
`python server.py`

It is wise to open a virtual environment where you install the requirements to avoid unnecessary packages. This should be done in the same directory as the cloned repo

Once you run server.py, you should see 
`Waiting for connections, Server started`
in the terminal. This means that the server is listening to other connections. 

Now you can open another terminal, and navigate to the same cloned directory. Now you run 
`pygame_online.py`
Now you should see in the server.py terminal, below "Waiting for connections, Server started": 
`Connected to: ("server", "port"), assigned player 0`


