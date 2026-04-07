from Obj.Player import Mage, Warrior, Player, MSG_MAGE, MSG_WARRIOR, MSG_PLAYER
import pygame


class GAME:
    def __init__(self, entieties, client):
        self.entities = entieties  # Słownik przechowujący wszystkie byty w grze
        pygame.init()
        # Set up the game window
        self.screen = pygame.display.set_mode((1000, 800))
        pygame.display.set_caption("Hello Pygame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.client = client

         # Załaduj obrazy raz
        try:
            self.player_img = pygame.image.load("assets/player.png").convert()
            self.mage_img = pygame.image.load("assets/player.png").convert()
            self.warrior_img = pygame.image.load("assets/golem.png").convert()
                
        except:
            self.player_img = None
            self.mage_img = None
            self.warrior_img = None
            print("Błąd: nie znaleziono jednego z obrazów")

    def show_class_selection_menu(self):
        """Menu do wyboru klasy przed grą. Zwraca wybraną klasę (0=Player, 1=Mage, 2=Warrior)"""
        selected = None
        while selected is None:
            # Obsługa eventów
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        selected = MSG_PLAYER  # 0
                    elif event.key == pygame.K_2:
                        selected = MSG_MAGE    # 1
                    elif event.key == pygame.K_3:
                        selected = MSG_WARRIOR # 2
            
            # Renderuj menu
            self.screen.fill((0, 0, 0))
            
            title = self.large_font.render("Wybierz swoją klasę", True, (255, 255, 255))
            self.screen.blit(title, (150, 100))
            
            option1 = self.font.render("1 - Player (Normalny)", True, (100, 255, 100))
            option2 = self.font.render("2 - Mage (Mag)", True, (100, 150, 255))
            option3 = self.font.render("3 - Warrior (Wojownik)", True, (255, 100, 100))
            
            self.screen.blit(option1, (200, 250))
            self.screen.blit(option2, (200, 350))
            self.screen.blit(option3, (200, 450))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return selected

    
    def game_exit(self ):
        pygame.quit()

    
    def handle_events(self):
        """Musi być wywoływane w pętli gry!"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def on_key_event(self, me):
        keys = pygame.key.get_pressed()
        moved = False
        if keys[pygame.K_LEFT]:
            me.x -= 5
            moved = True
        if keys[pygame.K_RIGHT]:
            me.x += 5
            moved = True
        if keys[pygame.K_UP]:
            me.y -= 5
            moved = True
        if keys[pygame.K_DOWN]:
            me.y += 5
            moved = True
        if moved:
            print(f"Ruch gracza: {me.x}, {me.y}")
        return me
    
    def update_entieties_in_game(self, frame_updates):
        for p_id, new_data in frame_updates.items():
            if p_id in self.entities:
                # AKTUALIZACJA (Chirurgia)
                current_obj = self.entities[p_id]
                print(f"Aktualizacja obiektu ID:{p_id} - Stary stan: ({current_obj.x}, {current_obj.y}, HP:{current_obj.hp}) -> Nowy stan: ({new_data.x}, {new_data.y}, HP:{new_data.hp})")
                # Przepisujemy TYLKO pozycję i stan, NIE podmieniamy całego obiektu
                current_obj.x = new_data.x
                current_obj.y = new_data.y
                current_obj.hp = new_data.hp
                
                # Jeśli to inny gracz i serwer przysłał konkretny typ klasy, to go zmieńmy
                if p_id != self.client.my_id and new_data.entity_type != 0:
                    current_obj.entity_type = new_data.entity_type
            else:
                # NOWY OBIEKT (Tylko jeśli go wcześniej nie było)
                self.entities[p_id] = new_data

    def render_players(self):
        #print(f"DEBUG: Aktualne byty w grze: {[f'ID:{obj.id} Type:{obj.entity_type}' for obj in self.entities.values()]}")  # Sprawdzenie typów bytów
        for obj in self.entities.values():
            size = obj.size if obj.size > 0 else 64
            # Wybierz obraz na podstawie entity_type
            if obj.entity_type == MSG_MAGE:
                img = self.mage_img
            elif obj.entity_type == MSG_WARRIOR:
                img = self.warrior_img
            else:  # MSG_PLAYER lub inne
                img = self.player_img
            
            if img:
                self.screen.blit(img, (int(obj.x), int(obj.y)))

    def render(self):
        """Renderuj okno"""
        print(f"obecne entities: {[f'ID:{obj.id} Type:{obj.entity_type}' for obj in self.entities.values()]}")  # Debug: jakie byty mamy do renderowania
        self.screen.fill((0, 0, 0))
        # TODO: Tutaj rysujesz obiekty
        self.render_players()
        pygame.display.flip()
        self.clock.tick(60)  # 60 FPS