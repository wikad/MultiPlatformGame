#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include "protocol.h"

int main() {
    int sock;
    struct sockaddr_in serv_addr;
    struct GamePacket packet;

    // 1. Tworzenie socketu
    sock = socket(AF_INET, SOCK_STREAM, 0);
    
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(5000);
    serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");

    // 2. Łączenie z serwerem
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("Błąd połączenia");
        return 1;
    }
    printf("Połączono z serwerem!\n");

    // 3. Faza Handshake - wysyłamy typ postaci (np. MSG_MAGE = 1)
    int my_type = htonl(MSG_MAGE); 
    send(sock, &my_type, sizeof(int), 0);
    printf("Wysłano typ postaci: Mage\n");

    // 4. Przygotowanie paczki testowej (Update pozycji)
    memset(&packet, 0, sizeof(struct GamePacket));
    packet.category = PACKET_ENTITY_UPDATE;
    packet.entity_type = MSG_MAGE;
    packet.data.player.x = 100.5f;
    packet.data.player.y = 200.0f;
    packet.data.player.hp = 100;

    // 5. Wysyłanie paczki
    send(sock, &packet, sizeof(struct GamePacket), 0);
    printf("Wysłano paczkę GamePacket (Pozycja: 100.5, 200.0)\n");

    // 6. Oczekiwanie na odpowiedź (Broadcast/Echo)
    struct GamePacket response;
    if (recv(sock, &response, sizeof(struct GamePacket), 0) > 0) {
        printf("Odebrano odpowiedź od serwera!\n");
        printf("ID przypisane przez serwer: %d\n", response.data.player.id);
    }

    close(sock);
    return 0;
}