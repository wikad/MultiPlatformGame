import time
from client import GameClient
from Obj.Player import Mage, Warrior, Player, MSG_MAGE, MSG_WARRIOR, MSG_TOWER
from Obj.Map import Map, MapObject # Zakładając, że Tower też tam może być
import queue
from Game import GAME
class GameEngine:
    def __init__(self):
        self.client = GameClient()
        self.entities = {}  # Główna "tablica" obiektów: {id: obiekt}
        self.game_map = None
        self.is_running = True
        self.gra = GAME(self.entities)
        self.frame_updates = {}  # Przechowuj updaty z tego frame'a
    def start(self):
        self.client.start()
        # Pętla gry
        try:
            while self.is_running:
                self.update_network()
                self.update_game_logic()
                self.render()
                # time.sleep(0.016) # ~60 FPS
                time.sleep(0.064) # ~60 FPS
        except KeyboardInterrupt:
            self.client.running = False

    def update_network(self):
        """Pobieramy wszystko co przyszło z serwera od ostatniej klatki."""
        self.frame_updates = {}  # Resetuj updaty z tego frame'a
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
        # Tworzymy nowy obiekt z danymi z serwera (bez aktualizowania self.entities)
        if e_type == MSG_MAGE:
            new_obj = Mage(p_id, x, y, size, hp, v1, v2)
        elif e_type == MSG_WARRIOR:
            new_obj = Warrior(p_id, x, y, size, hp, v1, v2)
        else:
            new_obj = Player(p_id, x, y, size, hp)
        
        # Przechowaj jako update do porównania
        self.frame_updates[p_id] = new_obj
        
        # Jeśli to nowa entity - dodaj do self.entities
        if p_id not in self.entities:
            self.entities[p_id] = new_obj
            print(f"Nowy obiekt w grze! ID: {p_id}, Typ: {e_type}")

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
        
        # 2. Obsługuj eventy Pygame
        if not self.gra.handle_events():
            self.is_running = False
            return
        
        # 3. Porównaj updaty z serwera ze stanem lokalnym
        if self.frame_updates:
            self.gra.update(self.frame_updates)
            # Aktualizuj self.entities nowymi danymi z serwera
            self.entities.update(self.frame_updates)
        
        # 4. Pobierz gracza
        me = self.entities.get(self.client.my_id)
        if not me:
            return
        
        # 5. Obsługuj input gracza
        me = self.gra.on_key_event(me)

        # 6. Wysyłanie aktualizacji do serwera
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
        # Renderuj okno Pygame
        self.gra.render()

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