import os

import pygame

from Obj.Player import MSG_MAGE, MSG_WARRIOR, MSG_PLAYER, MSG_TOWER

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
CLASS_NAMES = {MSG_PLAYER: "Player", MSG_MAGE: "Mage", MSG_WARRIOR: "Warrior", MSG_TOWER: "Tower"}


class GAME:
    def __init__(self, entieties, client):
        self.entities = entieties  # Słownik przechowujący wszystkie byty w grze
        pygame.init()
        # Set up the game window
        self.screen = pygame.display.set_mode((1000, 800))
        pygame.display.set_caption("MultiPlatformGame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 22)
        self.client = client

         # Załaduj obrazy raz
        try:
            self.player_img = pygame.image.load(os.path.join(ASSETS_DIR, "player.png")).convert_alpha()
            self.warrior_img = pygame.image.load(os.path.join(ASSETS_DIR, "golem.png")).convert_alpha()
            # Mag = sprite gracza zabarwiony na niebiesko
            self.mage_img = self.player_img.copy()
            self.mage_img.fill((90, 140, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
        except (pygame.error, FileNotFoundError):
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
        # Gracz nie może wyjść poza mapę
        w, h = self.screen.get_size()
        me.x = max(0, min(w - 64, me.x))
        me.y = max(0, min(h - 64, me.y))
        return me
    
    def update_entieties_in_game(self, frame_updates):
        for p_id, new_data in frame_updates.items():
            if p_id in self.entities:
                # AKTUALIZACJA (Chirurgia)
                current_obj = self.entities[p_id]
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
        for obj in self.entities.values():
            if obj.entity_type == MSG_TOWER:
                self._render_tower(obj)
                continue
            if obj.entity_type == MSG_MAGE:
                img = self.mage_img
            elif obj.entity_type == MSG_WARRIOR:
                img = self.warrior_img
            else:  # MSG_PLAYER lub inne
                img = self.player_img

            x, y = int(obj.x), int(obj.y)
            if img:
                self.screen.blit(img, (x, y))
            else:
                pygame.draw.rect(self.screen, (200, 200, 200), (x, y, 64, 64))

            # Podpis: ID, klasa, oznaczenie własnej postaci
            is_me = obj.id == self.client.my_id
            label = f"{'TY' if is_me else 'ID ' + str(obj.id)} · {CLASS_NAMES.get(obj.entity_type, '?')}"
            color = (255, 220, 90) if is_me else (220, 220, 220)
            text = self.small_font.render(label, True, color)
            self.screen.blit(text, (x + 32 - text.get_width() // 2, y - 18))

    def _render_tower(self, tower):
        x, y = int(tower.x), int(tower.y)
        pygame.draw.rect(self.screen, (120, 90, 60), (x, y, 48, 72))
        text = self.small_font.render(f"Wieża HP {tower.hp}", True, (230, 200, 160))
        self.screen.blit(text, (x + 24 - text.get_width() // 2, y - 18))

    def _render_background(self):
        self.screen.fill((24, 28, 36))
        w, h = self.screen.get_size()
        for gx in range(0, w, 50):
            pygame.draw.line(self.screen, (34, 40, 52), (gx, 0), (gx, h))
        for gy in range(0, h, 50):
            pygame.draw.line(self.screen, (34, 40, 52), (0, gy), (w, gy))

    def render(self):
        """Renderuje jedną klatkę gry."""
        self._render_background()
        self.render_players()
        players = sum(1 for o in self.entities.values() if o.entity_type != MSG_TOWER)
        hud = self.font.render(f"Gracze online: {players}", True, (255, 255, 255))
        self.screen.blit(hud, (16, 12))
        pygame.display.flip()
        self.clock.tick(60)
