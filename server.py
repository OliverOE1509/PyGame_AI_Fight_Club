import socket
from _thread import *
import sys
from threading import Lock

server = "0.0.0.0"  # Listen on all interfaces
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))
    sys.exit()

s.listen(2)
print("Waiting for connections, Server started")

players_lock = Lock()
players = {
    0: {"x": 3, "y": 10, 'connected': False, 'addr': None},  # Player 1
    1: {"x": 17, "y": 10, 'connected': False, 'addr': None}  # Player 2
}

def reset_players(player_id):
    with players_lock:
        players[player_id] = {
            'x': 3 if player_id == 0 else 17,
            'y': 10,
            'connected': False,
            'addr': None
        }

def find_available_slot():
    with players_lock:
        for player_id, player in players.items():
            if not player['connected']:
                player['connected'] = True
                return player_id
        return None

def threaded_client(conn, addr, player_id):
    try:
        with players_lock:
            initial_data = f"{players[player_id]['x']},{players[player_id]['y']},{player_id}"
            players[player_id]['addr'] = addr
        
        conn.send(str.encode(initial_data))
        print(f"Player {player_id} initialized from {addr}")
        
        while True:
            # Receive player data
            try:
                data = conn.recv(2048).decode()
                if not data:
                    print(f"Player {player_id} disconnected")
                    break

                if data == "GAME_OVER":
                    opponent_id = 1 if player_id == 0 else 0
                    break
                
                # Update player position
                try:
                    x, y = map(int, data.split(','))
                    with players_lock:
                        players[player_id]['x'] = x
                        players[player_id]['y'] = y
                    
                    # Send opponent's position
                    opponent_id = 1 if player_id == 0 else 0
                    with players_lock:
                        if players[opponent_id]['connected']:
                            reply = f"{players[opponent_id]['x']},{players[opponent_id]['y']}"
                            conn.send(str.encode(reply))
                except ValueError:
                    print(f"Invalid data received from player {player_id}")
                    break
            except ConnectionResetError:
                print(f"Connection reset by player {player_id}")
                break
                

    except Exception as e:
        print(f"Error with player {player_id}: {e}")
    finally:
        print(f"Closing connection with player {player_id}")
        with players_lock:
            players[player_id]['connected'] = False
            players[player_id]['addr'] = None
        conn.close()

try:
    while True:
        conn, addr = s.accept()
        player_id = find_available_slot()
        print(f"Connected to: {addr}, assigned player {player_id}")
        if player_id is not None:
            print(f"Player {player_id} connected from {addr}")
            start_new_thread(threaded_client, (conn, addr, player_id))
        else:
            print("No available slots, rejecting connection")
            conn.send(str.encode("Game is full"))
            conn.close()
            continue
        
except KeyboardInterrupt:
    print("Server shutting down")
finally:
    s.close()