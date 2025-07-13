import socket

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = 'www.toliha.net'  # Change to your server IP
        self.port = 5555
        self.addr = (self.server, self.port)
        self.player_id = -1
        self.connected = False
        
        try:
            self.client.connect(self.addr)
            initial_data = self.client.recv(2048).decode('utf-8')
            if initial_data:
                parts = initial_data.split(',')
                if len(parts) == 3:
                    self.player_id = int(parts[2])
                    self.connected = True
                    print(f"Connected as player {self.player_id}")
                else:
                    print("Invalid initial data format from server")
        except Exception as e:
            print(f"Connection error: {e}")

    def send(self, data):
        if not self.connected:
            return None
            
        try:
            self.client.settimeout(2.0)
            self.client.sendall(str.encode(data))
            reply = self.client.recv(2048).decode('utf-8')
            return reply
        except socket.timeout:
            print("Socket timeout, no response from server")
            return None
        except socket.error as e:
            print(f"Network error: {e}")
            self.connected = False
            return None

    def get_player_id(self):
        print(self.player_id)
        return self.player_id

    def close(self):
        try:
            self.client.close()
        except:
            pass