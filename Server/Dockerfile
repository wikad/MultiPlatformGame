# Używamy lekkiego obrazu z GCC
FROM gcc:latest

# Tworzymy folder w kontenerze
WORKDIR /app

# Kopiujemy server.c i protocol.h do kontenera
COPY server.c protocol.h .

# Kompilujemy z flagą -pthread
RUN gcc -o game_server server.c -lpthread

# Uruchamiamy serwer
CMD ["./game_server"]