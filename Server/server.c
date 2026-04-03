#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include "protocol.h"

// --- KONFIGURACJA ---
#define MAX_PLAYERS 10
#define MAX_TOWERS 5
#define PORT 5000

// --- STRUKTURY ZARZĄDZAJĄCE ---
struct Client {
    int socket;
    int player_id;
    int active;
};

// --- STAN GRY (GLOBALNY) ---
struct Client clients[MAX_PLAYERS];
struct GamePacket all_players[MAX_PLAYERS];
struct Tower game_towers[MAX_TOWERS];

int total_players = 0;
int tower_count = 0;

// --- MUTEXY (OCHRONA DANYCH) ---
pthread_mutex_t world_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t tower_mutex = PTHREAD_MUTEX_INITIALIZER;

// --- FUNKCJE POMOCNICZE ---

// Rozsyła pakiet do wszystkich aktywnych graczy (opcjonalnie pomijając nadawcę)
void broadcast_packet(struct GamePacket *packet, int sender_sock) {
    pthread_mutex_lock(&world_mutex);
    for (int i = 0; i < MAX_PLAYERS; i++) {
        if (clients[i].active && clients[i].socket != sender_sock) {
            send(clients[i].socket, packet, sizeof(struct GamePacket), 0);
        }
    }
    pthread_mutex_unlock(&world_mutex);
}

// --- OBSŁUGA POŁĄCZENIA ---

void *connection_handler(void *socket_desc) {
    int sock = *(int *)socket_desc;
    free(socket_desc);
    
    struct GamePacket packet;
    int read_size;
    int my_index = -1;

    // 1. REJESTRACJA I SYNCHRONIZACJA POCZĄTKOWA
    pthread_mutex_lock(&world_mutex);
    for (int i = 0; i < MAX_PLAYERS; i++) {
        if (!clients[i].active) {
            clients[i].socket = sock;
            clients[i].active = 1;
            clients[i].player_id = i + 1;
            my_index = i;
            total_players++;
            
            // Inicjalizacja pustego profilu gracza
            memset(&all_players[i], 0, sizeof(struct GamePacket));
            all_players[i].category = PACKET_ENTITY_UPDATE;
            all_players[i].data.player.id = clients[i].player_id;
            
            printf("[Serwer] Gracz ID %d dołączył (slot %d).\n", clients[i].player_id, i);
            
            // A. Wyślij nowemu graczowi jego własne ID
            struct GamePacket id_msg = all_players[i];
            send(sock, &id_msg, sizeof(struct GamePacket), 0);

            // B. Wyślij nowemu graczowi pozycje pozostałych graczy
            for (int j = 0; j < MAX_PLAYERS; j++) {
                if (clients[j].active && j != my_index) {
                    send(sock, &all_players[j], sizeof(struct GamePacket), 0);
                }
            }
            break;
        }
    }
    pthread_mutex_unlock(&world_mutex);

    if (my_index == -1) {
        printf("[Serwer] Brak wolnych slotów. Rozłączanie.\n");
        close(sock); return NULL;
    }

    // 2. PĘTLA GŁÓWNA KOMUNIKACJI
    while ((read_size = recv(sock, &packet, sizeof(struct GamePacket), 0)) > 0) {
        
        // --- AKTUALIZACJA POZYCJI/STATYSTYK ---
        if (packet.category == PACKET_ENTITY_UPDATE) {
            pthread_mutex_lock(&world_mutex);
            // Anty-cheat: wymuszamy ID przypisane przez serwer
            int real_id = clients[my_index].player_id;
            if (packet.entity_type == MSG_MAGE) packet.data.mage.base.id = real_id;
            else if (packet.entity_type == MSG_WARRIOR) packet.data.warrior.base.id = real_id;
            else packet.data.player.id = real_id;

            all_players[my_index] = packet; // Zapisz stan na serwerze
            pthread_mutex_unlock(&world_mutex);

            broadcast_packet(&packet, sock); // Powiadom innych o ruchu
        }

        // --- OBSŁUGA AKCJI (np. Atak) ---
        else if (packet.category == PACKET_ACTION) {
            struct ActionData *act = &packet.data.action;
            if (act->action_id == ACTION_HIT_TOWER) {
                pthread_mutex_lock(&tower_mutex);
                for (int i = 0; i < tower_count; i++) {
                    if (game_towers[i].base.id == act->target_id) {
                        game_towers[i].base.hp -= act->value;
                        
                        // Przygotuj pakiet rozgłoszeniowy z nowym stanem wieży
                        struct GamePacket t_packet;
                        t_packet.category = PACKET_ENTITY_UPDATE;
                        t_packet.entity_type = MSG_TOWER;
                        t_packet.data.tower = game_towers[i];

                        broadcast_packet(&t_packet, 0); // Wysyłamy do wszystkich (w tym nadawcy)
                        break;
                    }
                }
                pthread_mutex_unlock(&tower_mutex);
            }
        }
    }

    // 3. CZYSZCZENIE PO ROZŁĄCZENIU
    pthread_mutex_lock(&world_mutex);
    clients[my_index].active = 0;
    total_players--;
    printf("[Serwer] Gracz ID %d rozłączony.\n", clients[my_index].player_id);
    pthread_mutex_unlock(&world_mutex);

    close(sock);
    return NULL;
}

// --- PROGRAM GŁÓWNY ---

int main() {
    // Inicjalizacja obiektów (Wieże)
    game_towers[0].base.id = 100;
    game_towers[0].base.x = 500;
    game_towers[0].base.y = 500;
    game_towers[0].base.hp = 1000;
    tower_count = 1;

    // Zerowanie slotów graczy
    for(int i = 0; i < MAX_PLAYERS; i++) clients[i].active = 0;

    // Konfiguracja Socketu
    int listenfd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in serv_addr = {
        .sin_family = AF_INET,
        .sin_addr.s_addr = htonl(INADDR_ANY),
        .sin_port = htons(PORT)
    };

    if (bind(listenfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("Bind failed"); return 1;
    }

    listen(listenfd, 10);
    printf("[Serwer] Start: port %d. Czekam na graczy...\n", PORT);

    while (1) {
        int *connfd = malloc(sizeof(int));
        *connfd = accept(listenfd, NULL, NULL);
        
        pthread_t tid;
        pthread_create(&tid, NULL, connection_handler, connfd);
        pthread_detach(tid);
    }

    return 0;
}