import socket
from _thread import *
import sys

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

# Game state
players = [
    {"x": 3, "y": 10},  # Player 1
    {"x": 17, "y": 10}  # Player 2
]

def threaded_client(conn, player_id):
    try:
        # Send initial position and player ID
        initial_data = f"{players[player_id]['x']},{players[player_id]['y']},{player_id}"
        conn.send(str.encode(initial_data))
        
        while True:
            # Receive player data
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
                players[player_id]['x'] = x
                players[player_id]['y'] = y
                
                # Send opponent's position
                opponent_id = 1 if player_id == 0 else 0
                reply = f"{players[opponent_id]['x']},{players[opponent_id]['y']}"
                conn.send(str.encode(reply))
            except ValueError:
                print(f"Invalid data received from player {player_id}")
                break
                
    except ConnectionResetError:
        print(f"Player {player_id} connection reset")
    except Exception as e:
        print(f"Error with player {player_id}: {e}")
    finally:
        print(f"Lost connection with player {player_id}")
        conn.close()

current_player = 0
try:
    while True:
        conn, addr = s.accept()
        print(f"Connected to: {addr}, assigned player {current_player}")
        
        if current_player < 2:
            start_new_thread(threaded_client, (conn, current_player))
            current_player += 1
        else:
            print("Game is full, rejecting connection")
            conn.close()
except KeyboardInterrupt:
    print("Server shutting down")
finally:
    s.close()