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
// Format: category (int) | entity_type (int) | id (int) | x (float) | y (float) | size (int) | hp (int) | v1 (int) | v2 (int)
// Całkowity rozmiar: 36 bajtów (stały dla każdego pakietu)

struct GamePacket {
    int category;        // PACKET_ENTITY_UPDATE, PACKET_ACTION, itp.
    int entity_type;     // MSG_PLAYER, MSG_MAGE, MSG_WARRIOR, MSG_TOWER
    int id;              // ID gracza/entity
    float x;             // Pozycja X
    float y;             // Pozycja Y
    int size;            // Rozmiar entity
    int hp;              // Punkty zdrowia
    int v1;              // v1: mana (dla Mage), shield_durability (dla Warrior), range (dla Tower)
    int v2;              // v2: spell_power (dla Mage), strength (dla Warrior), damage (dla Tower)
};

#pragma pack(pop)
#endif