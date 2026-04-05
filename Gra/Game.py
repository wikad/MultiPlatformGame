from Obj.Player import Mage
import pygame


class GAME:
    def __init__(self, entieties):
        self.entities = entieties  # Słownik przechowujący wszystkie byty w grze
        pygame.init()
        # Set up the game window
        self.screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("Hello Pygame")
        self.clock = pygame.time.Clock()


    def update(self, updates):
        # 1. Odbierz aktualizacje od serwera
        # Aktualizujemy byty na podstawie danych z serwera
        attrs_to_compare = ['x', 'y', 'hp', 'mana']  # Atrybuty do porównania
    
        for eid, obj in updates.items():
            
            if eid in self.entities:
                old_obj = self.entities[eid]
                changes = []
                
                for attr in attrs_to_compare:
                    if hasattr(old_obj, attr) and hasattr(obj, attr):
                        old_val = getattr(old_obj, attr)
                        new_val = getattr(obj, attr)
                        if old_val != new_val:
                            changes.append(f"{attr}:{old_val}->{new_val}")
                
                if changes:
                    print(f"ID:{eid} {', '.join(changes)}")
            else:
                print(f"ID:{eid} Nowa entity")
            
            self.entities[eid] = obj

        # 2. Zaktualizuj stan gry (np. poruszanie się, kolizje, itp.)
        

        # 3. Renderuj grę (jeśli używasz biblioteki graficznej)        

    
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
    
    def render(self):
        """Renderuj okno"""
        self.screen.fill((0, 0, 0))
        # TODO: Tutaj rysujesz obiekty
        pygame.display.flip()
        self.clock.tick(60)  # 60 FPS