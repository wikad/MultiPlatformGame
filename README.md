### CIAO BELLA 
## LISTA DO ZROBIENIA


# Technologia 
    ** Server 
        - C
        - Pthread
        - Sockets
    ** Infrastruktura
        - Docker     
        - Linux 
    ** Gra
        - Python
        - Pygame



# Server 
    * Zmiana profilu
        - ustalenie co ma mieć w sobie profil clienta dane do przekazania itp 
        - liczba graczy

    * Schemat łącznia
        - model łączenia z socketem 
        - tworzenie wątków
        - nadawania inforamcji 

    * Błędy
        + usuwanie martwych wątków
        + usuwanie pustych graczy 
        + Mutexy, Komunikacja, Race Condition, DeadLock, Lag

    * Walidacja
        - anty cheat
        - utrata internetu
        - rozróznianie graczy

    * Game loop
        - odświeżanie
        - Synchronizacja stanu wątek server
        - rozsyłanie informacji o stanie 

    * Odpalenie w Dokerze
        - otwarcie portu na świat 
        - umożliwienie połączeń pod jakimś adresem



# Gra (python, pygame) Client side
    * Łączenie gracza z serverem
        - Przykładowe połączenie
            + data = struct.pack('iff', 1, 10.5, 20.0) s = socket.socket() s.connect(('127.0.0.1', 5000)) s.send(data)
        - Jakie dane przesyłamy 
            + Formatowanie tych danych w paczki
        - Przesyłanie danych
        - Odbieranie danych z servera osobny wątek asynchroniczny
        - Aktualizacja danych

    * Profile Gracza 
        - Self ID 
            + rozpoznawanie którym sie jest
        - Przechowywanie wszystkich graczy
        - Wyświetlanie wszystkich graczy 
    
    * Synchronizacja (lag)
        - rozłożenie ruchu pomiędzy klatkami żeby nie przeskakiwało
        - przewidywanie czy może się tak zdażyć i dostanie potwierdzenia od servera
    
    * Tekstury 
        - podstawowe tekstury użyte w grze
    
    * Gra 
        -Interpolacja liniowa (Lerp): To magiczne słowo, które sprawi, że gra będzie płynna. Zamiast x = nowa_pozycja, robisz x += (nowa_pozycja - x) * 0.1.



# Projekt protokołu
    - CDN

# UI
    - CDN

# Logika rozgrywki
    - CDN