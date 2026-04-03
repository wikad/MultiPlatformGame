#ifndef PROTOCOL_H
#define PROTOCOL_H

#pragma pack(push, 1) // Ściśnij struktury (brak ukrytych bajtów)

// Definiujemy ogólny typ paczki, żeby serwer wiedział co odbiera
typedef enum {
    PACKET_ENTITY_UPDATE, // Aktualizacja pozycji/statystyk (Player/Mage/Tower)
    PACKET_ACTION,        // Interakcja (Atak/Leczenie)
    PACKET_MAP_DATA       // Dane mapy
} PacketCategory;

typedef enum {
    MSG_PLAYER,
    MSG_MAGE,
    MSG_WARRIOR,
    MSG_TOWER
} EntityType;

struct Player {
    int id;
    float x, y;
    int size;
    int hp;
};

struct Mage {
    struct Player base;
    int mana;
    int spell_power;
};

struct Warrior {
    struct Player base;
    int shield_durability;
    int strength;
};

struct Tower {
    struct Player base;
    int range;
    int damage;
};

// --- SEKCA AKCJI ---

typedef enum {
    ACTION_HIT_TOWER,
    ACTION_HEAL_PLAYER,
    ACTION_HIT_PLAYER
} ActionType;

struct ActionData {
    int actor_id;
    int target_id;
    ActionType action_id;
    int value;
};

// --- GŁÓWNA PACZKA (KOPERTA) ---

struct GamePacket {
    PacketCategory category; // 1. Najpierw patrzymy co to za kategoria
    EntityType entity_type;  // 2. Jeśli to Entity, to jaki typ?
    
    union {
        struct Player player;
        struct Mage mage;
        struct Warrior warrior;
        struct Tower tower;
        struct ActionData action; // Dodaliśmy akcje do unii!
    } data;
};

#pragma pack(pop)
#endif