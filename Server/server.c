#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include "protocol.h"

#define MAX_CLIENTS 10

// Globalna tablica klientów i licznik
int client_sockets[MAX_CLIENTS];
int client_count = 0;

// Mutex - strażnik, który pilnuje, by tylko jeden wątek na raz modyfikował tablicę
pthread_mutex_t clients_mutex = PTHREAD_MUTEX_INITIALIZER;


// Struktura przechowująca dane o połączonym kliencie
typedef struct {
    int socket;
    int id;
    char username[32]; 
    int type;
} Client;

int get_player_type(int socket) {
    int player_type = 0;
    ssize_t result = recv(socket, &player_type, sizeof(int), 0);

    if (result <= 0) {
        return -1; // Błąd połączenia lub zamknięty socket
    }

    // Konwersja z formatu sieciowego (Big-Endian) na lokalny
    return ntohl(player_type);
}

void remove_client(int socket) {
    pthread_mutex_lock(&clients_mutex);
    for (int i = 0; i < client_count; i++) {
        if (client_sockets[i] == socket) {
            // Przesuwamy pozostałe sockety, żeby załatać dziurę
            for (int j = i; j < client_count - 1; j++) {
                client_sockets[j] = client_sockets[j + 1];
            }
            client_count--;
            break;
        }
    }
    pthread_mutex_unlock(&clients_mutex);
}

void broadcast_packet(struct GamePacket *packet, int sender_socket) {
    pthread_mutex_lock(&clients_mutex); // Blokujemy dostęp do tablicy na czas wysyłki

    for (int i = 0; i < client_count; i++) {
        // Nie wysyłamy paczki z powrotem do nadawcy (opcjonalne, zależnie od logiki gry)
        if (client_sockets[i] != sender_socket) {
            if (send(client_sockets[i], packet, sizeof(struct GamePacket), 0) < 0) {
                perror("Błąd broadcastu");
            }
        }
    }

    pthread_mutex_unlock(&clients_mutex); // Zwalniamy blokadę
}

void *connection_handler(void *client_ptr) {
    Client cli = *(Client *)client_ptr;
    free(client_ptr);
    
    struct GamePacket packet;
    ssize_t read_size;

    // 1. Handshake
    int type = get_player_type(cli.socket);
    if (type < 0) {
        printf("[Klient %d] Błąd inicjalizacji.\n", cli.id);
        remove_client(cli.socket); // Usuwamy z tablicy, jeśli się rozłączył
        close(cli.socket);
        return NULL;
    }
    cli.type = type;

    printf("[Klient %d] Wybrał typ: %d. Start broadcastu.\n", cli.id, type);

    // 2. Główna pętla gry
    while ((read_size = recv(cli.socket, &packet, sizeof(struct GamePacket), 0)) > 0) {
        
        // Zabezpieczenie: Serwer nadpisuje ID nadawcy, żeby nikt nie oszukiwał
        packet.data.player.id = cli.id;

        // ROZSYŁANIE: Teraz każdy inny gracz dostanie tę paczkę
        broadcast_packet(&packet, cli.socket);
        
        // Opcjonalnie: echo do samego siebie, jeśli klient tego potrzebuje
        // send(cli.socket, &packet, sizeof(struct GamePacket), 0);
    }

    // 3. Sprzątanie
    printf("[Klient %d] Rozłączony.\n", cli.id);
    remove_client(cli.socket);
    close(cli.socket);
    return NULL;
}

int main(int argc, char *argv[]) {
    int listenfd;
    struct sockaddr_in serv_addr;
    int client_id_counter = 1; // Licznik do nadawania ID

    listenfd = socket(AF_INET, SOCK_STREAM, 0);
    
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(5000); 

    bind(listenfd, (struct sockaddr*)&serv_addr, sizeof(serv_addr));
    listen(listenfd, 10); 

    printf("Serwer RPG z obsługą ID uruchomiony...\n");

    for (;;) {
        struct sockaddr_in client_addr;
        socklen_t addr_len = sizeof(struct sockaddr_in);
        
        int connfd = accept(listenfd, (struct sockaddr*)&client_addr, &addr_len);
        
        if (connfd >= 0) {
            
            pthread_mutex_lock(&clients_mutex);
            if (client_count < MAX_CLIENTS) {
                client_sockets[client_count++] = connfd;
                pthread_mutex_unlock(&clients_mutex);
                
                // Uruchom wątek...
                // Alokujemy pamięć dla struktury Client
                Client *new_client = malloc(sizeof(Client));
                new_client->socket = connfd;
                new_client->id = client_id_counter++; // Nadaj ID i zwiększ licznik

                printf("Nowe połączenie: ID %d, IP: %s\n", 
                    new_client->id, inet_ntoa(client_addr.sin_addr));

                pthread_t thread_id;
                pthread_create(&thread_id, NULL, connection_handler, (void *)new_client);
                pthread_detach(thread_id);

            } else {
                printf("Serwer pełny!\n");
                close(connfd);
                pthread_mutex_unlock(&clients_mutex);
            }
        }
    }
    return 0;
}