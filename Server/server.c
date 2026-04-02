#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>

// Struktura danych gracza (musi być identyczna w Pythonie!)
struct PlayerData {
    int id;
    float x;
    float y;
};

void *connection_handler(void *socket_desc) {
    int sock = *(int *)socket_desc;
    free(socket_desc); // Zwalniamy pamięć zaalokowaną w main
    
    int read_size;
    struct PlayerData p_data;
    
    printf("Wątek obsługujący gracza wystartował.\n");

    // Pętla gry dla tego konkretnego klienta
    while ((read_size = recv(sock, &p_data, sizeof(struct PlayerData), 0)) > 0) {
        
        // Logika serwera: tutaj możesz np. sprawdzić kolizje
        printf("Gracz [%d]: X=%.2f, Y=%.2f\n", p_data.id, p_data.x, p_data.y);

        // Odsyłamy dane z powrotem (potwierdzenie)
        // W przyszłości tutaj będziesz wysyłać stan CAŁEGO świata
        send(sock, &p_data, sizeof(struct PlayerData), 0);
    }

    if (read_size == 0) {
        printf("Klient rozłączony.\n");
    } else if (read_size == -1) {
        perror("recv failed");
    }

    close(sock);
    return NULL;
}

int main(int argc, char *argv[]) {
    int listenfd = 0;
    struct sockaddr_in serv_addr;

    listenfd = socket(AF_INET, SOCK_STREAM, 0);
    
    // Pozwala na szybkie ponowne użycie portu po restarcie
    int opt = 1;
    setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(5000);

    if (bind(listenfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("Bind failed");
        return 1;
    }

    listen(listenfd, 10);
    printf("Serwer gry nasłuchuje na porcie 5000...\n");

    while (1) {
        int *connfd = malloc(sizeof(int)); // Alokujemy pamięć dla deskryptora (bezpieczne dla wątków)
        *connfd = accept(listenfd, (struct sockaddr *)NULL, NULL);
        
        printf("Połączenie zaakceptowane, tworzę wątek...\n");
        pthread_t thread_id;
        if (pthread_create(&thread_id, NULL, connection_handler, (void *)connfd) < 0) {
            perror("Could not create thread");
            free(connfd);
        }
        
        // Nie musimy robić join, wątek sam się posprząta
        pthread_detach(thread_id);
    }

    return 0;
}