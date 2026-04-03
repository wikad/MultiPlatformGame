# client.py
import socket
import struct
import threading
import queue

class GameClient:
    # ... (formaty struct te same co u Ciebie) ...
    GAME_PACKET_FORMAT = "<iiiffiiii"
    PACKET_SIZE = struct.calcsize(GAME_PACKET_FORMAT)

    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Kolejki do komunikacji z main.py
        self.inbox = queue.Queue()  # Dane z serwera do gry
        self.outbox = queue.Queue() # Dane z gry do serwera
        
        self.my_id = None
        self.running = False

    def start(self):
        self.sock.connect((self.host, self.port))
        self.running = True
        # Wątek do odbierania
        threading.Thread(target=self._receive_loop, daemon=True).start()
        # Wątek do wysyłania (opcjonalnie, lub metoda send)
        threading.Thread(target=self._send_loop, daemon=True).start()

    def _receive_loop(self):
        while self.running:
            try:
                data = self.sock.recv(self.PACKET_SIZE)
                if not data: break
                
                unpacked = struct.unpack(self.GAME_PACKET_FORMAT, data)
                # Wrzucamy surowe dane lub słownik do kolejki
                self.inbox.put(unpacked)
            except: break

    def _send_loop(self):
        """Wysyła wszystko, co gra wrzuci do outbox."""
        while self.running:
            packet = self.outbox.get()
            try:
                self.sock.sendall(packet)
            except: break

    def send_action(self, category, e_type, p_id, x, y, s, hp, v1, v2):
        """Pomocnicza metoda do pakowania i wrzucania do outbox."""
        packet = struct.pack(self.GAME_PACKET_FORMAT, category, e_type, p_id, 
                             float(x), float(y), s, hp, v1, v2)
        self.outbox.put(packet)