# Stałe odpowiadające EntityType w protocol.h
MSG_PLAYER = 0
MSG_MAGE = 1
MSG_WARRIOR = 2
MSG_TOWER = 3

class Player:
    def __init__(self, id, x, y, size, hp):
        self.id = id
        self.x = x
        self.y = y
        self.size = size
        self.hp = hp

    def update_base(self, x, y, hp):
        self.x = x
        self.y = y
        self.hp = hp

class Mage(Player):
    def __init__(self, id, x, y, size, hp, mana, spell_power):
        super().__init__(id, x, y, size, hp)
        self.mana = mana
        self.spell_power = spell_power

    def update_stats(self, x, y, hp, mana, spell_power):
        self.update_base(x, y, hp)
        self.mana = mana
        self.spell_power = spell_power
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
class Warrior(Player):
    def __init__(self, id, x, y, size, hp, shield, strength):
        super().__init__(id, x, y, size, hp)
        self.shield_durability = shield
        self.strength = strength

    def update_stats(self, x, y, hp, shield, strength):
        self.update_base(x, y, hp)
        self.shield_durability = shield
        self.strength = strength

class Tower(Player): # W C Tower ma bazę Player, więc tutaj też dajemy Player
    def __init__(self, id, x, y, size, hp, range_val, damage):
        super().__init__(id, x, y, size, hp)
        self.range = range_val
        self.damage = damage

    def update_stats(self, x, y, hp, range_val, damage):
        self.update_base(x, y, hp)
        self.range = range_val
        self.damage = damage