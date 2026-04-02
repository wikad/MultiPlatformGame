# Używamy lekkiego obrazu z GCC
FROM gcc:latest

# Tworzymy folder w kontenerze
WORKDIR /app

# Kopiujemy server.c do kontenera
COPY server.c .

# Kompilujemy z flagą -pthread
RUN gcc -o game_server server.c -lpthread

# Uruchamiamy serwer
CMD ["./game_server"]