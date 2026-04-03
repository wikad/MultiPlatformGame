import time
from client import GameClient
from Obj.Player import Mage, Warrior, Player, MSG_MAGE, MSG_WARRIOR, MSG_TOWER
from Obj.Map import Map, MapObject # Zakładając, że Tower też tam może być
import queue
class GameEngine:
    def __init__(self):
        self.client = GameClient()
        self.entities = {}  # Główna "tablica" obiektów: {id: obiekt}
        self.game_map = None
        self.is_running = True

    def start(self):
        self.client.start()
        # Pętla gry
        try:
            while self.is_running:
                self.update_network()
                self.update_game_logic()
                self.render()
                time.sleep(0.016) # ~60 FPS
        except KeyboardInterrupt:
            self.client.running = False

    def update_network(self):
        """Pobieramy wszystko co przyszło z serwera od ostatniej klatki."""
        while not self.client.inbox.empty():
            try:
                packet = self.client.inbox.get_nowait()
                category, e_type, p_id, x, y, size, hp, v1, v2 = packet

                # Jeśli to pierwsza paczka jaką dostaliśmy, przypiszmy sobie nasze ID
                if self.client.my_id is None:
                    self.client.my_id = p_id
                    print(f"Moje ID to: {p_id}")

                if category == 0:  # PACKET_ENTITY_UPDATE
                    self._handle_entity_update(e_type, p_id, x, y, size, hp, v1, v2)
                
                # Po przetworzeniu oznaczamy zadanie jako wykonane
                self.client.inbox.task_done()
            except queue.Empty:
                break
    def _handle_entity_update(self, e_type, p_id, x, y, size, hp, v1, v2):
        """Decyduje czy stworzyć nowy obiekt, czy zaktualizować istniejący."""
        if p_id not in self.entities:
            # TWORZENIE (Fabryka)
            if e_type == MSG_MAGE:
                self.entities[p_id] = Mage(p_id, x, y, size, hp, v1, v2)
            elif e_type == MSG_WARRIOR:
                self.entities[p_id] = Warrior(p_id, x, y, size, hp, v1, v2)
            # Tutaj możesz dodać Tower lub inne typy
            else:
                self.entities[p_id] = Player(p_id, x, y, size, hp)
            print(f"Nowy obiekt w grze! ID: {p_id}, Typ: {e_type}")
        else:
            # AKTUALIZACJA
            obj = self.entities[p_id]
            # Używamy metod update, które napisałeś wcześniej
            if isinstance(obj, (Mage, Warrior)):
                obj.update_stats(x, y, hp, v1, v2)
            else:
                obj.update_base(x, y, hp)

    def send_action_to_server(self, category, e_type, p_id, x, y, size, hp, v1, v2):
        """Proces pakowania danych do wysyłki."""
        # LOG: Co pakujemy?
        print(f"[PAKOWANIE] Wysyłam ruch/akcję ID:{p_id} na pozycję {x},{y}")
        
        # Wywołujemy metodę klienta, która zrobi struct.pack
        self.client.send_action(x, y) 

    def update_game_logic(self):
        # 1. Sprawdź czy mamy już przypisane ID przez serwer
        if self.client.my_id is None:
            return
        #TODO sparwić żeby nie wysyłało bez żadnej akcji od gracza
        # 2. Pobierz obiekt reprezentujący CIEBIE (lokalnego gracza)
        me = self.entities.get(self.client.my_id)
        if not me:
            return

        # 3. PRZYKŁAD: Poruszanie (np. jeśli używasz jakiejś biblioteki do klawiszy)
        # Tutaj zmieniasz me.x i me.y na podstawie wejścia od gracza
        
        # 4. Wysyłanie aktualizacji do serwera (Zpakowywanie)
        # Używamy metody z client.py, która wrzuci to do outbox
        self.client.send_action(
            0,              # category: PACKET_ENTITY_UPDATE
            1,              # e_type: MSG_MAGE (przykładowo)
            me.id, 
            me.x, me.y, 
            me.size, me.hp, 
            getattr(me, 'mana', 0), # v1
            getattr(me, 'spell_power', 0) # v2
        )

    def render(self):
        # Tutaj rysujesz. Na razie tylko tekstowo dla testu:
        if self.entities:
            for eid, obj in self.entities.items():
                # Sprytne wypisywanie stanu
                status = f"ID:{eid} Pos:({obj.x},{obj.y}) HP:{obj.hp}"
                if isinstance(obj, Mage): status += f" Mana:{obj.mana}"
                print(status)

    def perform_attack(self, target_id):
        # Wysyłamy pakiet typu ACTION
        self.client.send_action(
            1,              # category: PACKET_ACTION
            0,              # e_type: (nieistotne dla akcji)
            self.client.my_id, 
            float(target_id), # x -> target_id (zgodnie z Twoją unią w C)
            0.0,            # y -> action_id
            0, 0, 0, 0      # reszta zerowana
        )

if __name__ == "__main__":
    game = GameEngine()
    game.start()