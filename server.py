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
    0: {"x": 3, "y": 10, 'connected': False, 'addr': None, 'bullets': [], 'alive': True, 'health': 3},  # Player 1
    1: {"x": 17, "y": 10, 'connected': False, 'addr': None, 'bullets': [], 'alive': True, 'health': 3}  # Player 2
}

def reset_players(player_id):
    with players_lock:
        players[player_id] = {
            'x': 3 if player_id == 0 else 17,
            'y': 10,
            'connected': False,
            'addr': None,
            'bullets': [],
            'alive': True,
            'health': 3
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
            try:
                data = conn.recv(2048).decode().strip()
                if not data:
                    print(f"Player {player_id} disconnected")
                    break

                if data == "RESET":
                    reset_players(player_id)
                    continue
                    #opponent_id = 1 - player_id
                    #with players_lock:
                    #    if players[opponent_id]['connected']:
                    #        try:
                    #            conn.sendall(str.encode("GAME_OVER"))
                    #        except:
                    #            pass
                    #break

                parts = data.split('|')
                if not parts or not parts[0]:
                    continue
                
                try:
                    # Process position and bullets
                    x, y = map(int, parts[0].split(','))
                    bullet_data = [b for b in parts[1:] if b] if len(parts) > 1 else []

                    with players_lock:
                        players[player_id]['x'] = x
                        players[player_id]['y'] = y
                        players[player_id]['bullets'] = bullet_data

                    opponent_id = 1 - player_id
                    reply = None
                    with players_lock:
                        if players[opponent_id]['connected']:
                            if not players[opponent_id]['alive']:
                                reply = "GAME_OVER_WIN"
                            else:
                                reply = f"{players[opponent_id]['x']},{players[opponent_id]['y']},{int(players[opponent_id]['alive'])}"
                                if players[opponent_id]['bullets']:
                                    reply += '|' + '|'.join(players[opponent_id]['bullets'])
                        else:
                            reply = "OPPONENT_DISCONNECTED"

                    if reply:
                        try:
                            conn.sendall(str.encode(reply))
                        except:
                            print(f"Failed to send to player {player_id}")
                            break
                            
                except ValueError:
                    continue
                
            except ConnectionResetError:
                break
            except Exception as e:
                print(f"Error with player {player_id}: {e}")
                break
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
        #print(f"Connected to: {addr}, assigned player {player_id}")
        if player_id is not None:
            print(f"Player {player_id} connected from {addr}")
            start_new_thread(threaded_client, (conn, addr, player_id))
        else:
            print("No available slots, rejecting connection")
            conn.send(str.encode("Game is full"))
            conn.close()
        
except KeyboardInterrupt:
    print("Server shutting down")
finally:
    s.close()