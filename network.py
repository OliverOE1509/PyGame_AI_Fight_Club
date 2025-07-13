import socket
import time

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = 'www.toliha.net'  # Change to your server IP
        self.port = 5555
        self.addr = (self.server, self.port)
        self.player_id = -1
        self.connected = False
        self.last_connection_attempt = 0
        self.connect()

    def connect(self):
        now = time.time()
        if now - self.last_connection_attempt < 2:  # 2 second cooldown
            return False
            
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(3.0)
            self.client.connect(self.addr)
            
            initial_data = self.client.recv(2048).decode('utf-8')
            if initial_data:
                parts = initial_data.split(',')
                if len(parts) == 3:
                    self.player_id = int(parts[2])
                    self.connected = True
                    print(f"Connected as player {self.player_id}")
                    return True
        except Exception as e:
            print(f"Connection error: {e}")
        
        self.last_connection_attempt = time.time()
        return False

    def send(self, data, retries=3):
        if not self.connected and not self.connect():
            return None
            
        for attempt in range(retries):
            try:
                self.client.settimeout(2.0)
                self.client.sendall(str.encode(data))
                reply = self.client.recv(2048).decode('utf-8')
                return reply if reply else None
            except socket.timeout:
                print(f"Timeout (attempt {attempt+1}/{retries})")
                if attempt == retries-1:
                    self.connected = False
            except socket.error as e:
                print(f"Network error: {e}")
                self.connected = False
                if not self.connect():
                    return None
        return None

    def get_player_id(self):
        return self.player_id

    def close(self):
        try:
            self.client.close()
        except:
            pass
        self.connected = False