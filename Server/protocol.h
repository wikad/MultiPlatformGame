#ifndef PROTOCOL_H
#define PROTOCOL_H

// Baza - to co ma każdy gracz

struct Player {
    int id;
    float x, y;
    int size;
    int hp;
};

// "Dziedziczenie" - Mag to Player + mana
struct Mage {
    struct Player base; // MUSI być na samym początku
    int mana;
    int spell_power;
};

// "Dziedziczenie" - Wojownik to Player + tarcza
struct Warrior {
    struct Player base;
    int shield_durability;
    int strength;
};

struct Map {
    int width;
    int height;
    enum MapType {
        Sand,
        Grass,
    } type ;
    // Możesz dodać tu więcej informacji, np. przeszkody, itemy itp.
};

struct Tower {
    struct Player base;
    int range;
    int damage;
};

#endif