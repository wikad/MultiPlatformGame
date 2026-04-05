# client.py
import socket
import struct
import threading
import queue

class GameClient:
    # Format: category (i) | entity_type (i) | id (i) | x (f) | y (f) | size (i) | hp (i) | v1 (i) | v2 (i)
    # Łącznie: 36 bajtów (3 int + 2 float + 4 int = 9 elementów)
    GAME_PACKET_FORMAT = "<iiiffiii"
    PACKET_SIZE = struct.calcsize(GAME_PACKET_FORMAT)

    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Kolejki do komunikacji z main.py
        self.inbox = queue.Queue()  # Dane z serwera do gry
        self.outbox = queue.Queue() # Dane z gry do serwera
        
        self.my_id = None
        self.selected_class = None  # Wybrana klasa: 0=Player, 1=Mage, 2=Warrior
        self.running = False
        self.class_sent = False  # Flaga czy wysłaliśmy typ klasy
        
    @staticmethod
    def get_format_for_entity_type(entity_type):
        """Zwraca format struct dla danego typu entity."""
        # category, e_type, id, x, y, size, hp, v1, v2
        if entity_type == 0:  # MSG_PLAYER
            return "<iiiifii"  # 2 int (cat, type) + 3 int (id, size, hp) + 2 float (x, y)
        else:  # MSG_MAGE=1, MSG_WARRIOR=2, MSG_TOWER=3
            return "<iiiiifiii"  # 2 int (cat, type) + 5 int (id, size, hp, v1, v2) + 2 float (x, y)

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
        # Jeśli to pierwsza paczka i mamy wybraną klasę, upewnij się że wysyłamy prawidłowy e_type
        if not self.class_sent and self.selected_class is not None:
            e_type = self.selected_class
            self.class_sent = True
            print(f"[HANDSHAKE] Wysyłam typ klasy: {e_type}")
        
        packet = struct.pack(self.GAME_PACKET_FORMAT, category, e_type, p_id, 
                             float(x), float(y), s, hp, v1, v2)
        self.outbox.put(packet)