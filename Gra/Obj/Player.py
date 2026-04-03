
# struct Player {
#     int id;
#     float x, y;
#     int size;
#     int hp;
# };

# struct Mage {
#     struct Player base; 
#     int mana;
#     int spell_power;
# };

# struct Warrior {
#     struct Player base;
#     int shield_durability;
#     int strength;
# };

class Player:
    def __init__(self, id, x, y, size, hp):
        self.id = id
        self.x = x
        self.y = y
        self.size = size
        self.hp = hp

class Mage(Player):
    def __init__(self, id, x, y, size, hp, mana, spell_power):
        super().__init__(id, x, y, size, hp)
        self.mana = mana
        self.spell_power = spell_power

class Warrior(Player):
    def __init__(self, id, x, y, size, hp, shield_durability, strength):
        super().__init__(id, x, y, size, hp)
        self.shield_durability = shield_durability
        self.strength = strength