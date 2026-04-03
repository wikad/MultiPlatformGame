import socket
import struct
import threading
import time

# --- KONFIGURACJA ZGODNA Z protocol.h ---
# < oznacza "little-endian" (standard dla x86/C)
# i=int, f=float. Format: Category, EntityType, ID, X, Y, Size, HP, Val1, Val2
# (Val1 i Val2 to mana/spell_power lub shield/strength w zależności od klasy)
GAME_PACKET_FORMAT = "<iiiffiiii" 
PACKET_SIZE = struct.calcsize(GAME_PACKET_FORMAT)

# Kategorie i Typy
PACKET_ENTITY_UPDATE = 0
PACKET_ACTION = 1
MSG_PLAYER = 0
MSG_MAGE = 1
ACTION_HIT_TOWER = 0

class GameClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_id = None
        self.others = {} # Słownik na dane innych graczy {id: dane}
        self.running = True

    def connect(self, host='127.0.0.1', port=5000):
        try:
            self.sock.connect((host, port))
            print("Połączono z serwerem!")
            
            # Startujemy wątek odbierający dane w tle
            threading.Thread(target=self._receive_loop, daemon=True).start()
        except Exception as e:
            print(f"Błąd połączenia: {e}")

    def _receive_loop(self):
        """Pętla działająca w osobnym wątku - tylko odbiera."""
        while self.running:
            try:
                data = self.sock.recv(PACKET_SIZE)
                if not data: break
                
                # Rozpakowujemy
                unpacked = struct.unpack(GAME_PACKET_FORMAT, data)
                category, e_type, p_id, x, y, size, hp, v1, v2 = unpacked

                if self.my_id is None:
                    self.my_id = p_id
                    print(f"Moje ID nadane przez serwer: {self.my_id}")

                # Zapisujemy stan świata (innych graczy)
                if p_id != self.my_id:
                    self.others[p_id] = {"x": x, "y": y, "hp": hp, "type": e_type}
                    print(f"Aktualizacja gracza {p_id}: x={x}, y={y}")
                else:
                    # Potwierdzenie naszych danych od serwera
                    pass

            except Exception as e:
                print(f"Błąd odbierania: {e}")
                break

    def send_move(self, x, y):
        """Wysyła naszą pozycję do serwera."""
        if self.my_id is None: return
        # Przykład wysyłania jako MAG (MSG_MAGE)
        packet = struct.pack(GAME_PACKET_FORMAT, 
                             PACKET_ENTITY_UPDATE, MSG_MAGE, self.my_id, 
                             float(x), float(y), 32, 100, 50, 10) # 50 many, 10 power
        self.sock.sendall(packet)

    def attack_tower(self, tower_id):
        """Wysyła akcję ataku."""
        # W unii dla ActionData: actor_id, target_id, action_id, value
        # Musimy to dopasować do formatu (pamiętaj, że unia to ta sama pamięć!)
        packet = struct.pack(GAME_PACKET_FORMAT,
                             PACKET_ACTION, 0, self.my_id, 
                             float(tower_id), float(ACTION_HIT_TOWER), 25, 0, 0, 0)
        self.sock.sendall(packet)

# --- TEST ---
if __name__ == "__main__":
    client = GameClient()
    client.connect()

    # Symulacja pętli gry
    try:
        for i in range(10):
            client.send_move(100 + i*5, 200)
            if i == 5:
                client.attack_tower(100) # Atakujemy wieżę o ID 100
            time.sleep(0.5)
    except KeyboardInterrupt:
        client.running = False