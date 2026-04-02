import socket
import struct
import time

def run_client():
    server_address = ('127.0.0.1', 5000)
    # Definiujemy format: i = int (4 bajty), f = float (4 bajty)
    # Łącznie 12 bajtów: [ID][X][Y]
    data_format = 'iff' 
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(server_address)
        print("Połączono z serwerem C w Dockerze!")

        # Symulacja wysyłania ruchu gracza przez 5 sekund
        for i in range(5):
            x, y = 10.5 + i, 20.0 + i
            # Pakujemy dane do formatu binarnego
            packet = struct.pack(data_format, 1, x, y)
            s.sendall(packet)
            
            # Odbieramy odpowiedź od serwera
            response = s.recv(struct.calcsize(data_format))
            my_id, rx, ry = struct.unpack(data_format, response)
            print(f"Serwer potwierdził pozycję: ID={my_id}, X={rx}, Y={ry}")
            
            time.sleep(1)

    except Exception as e:
        print(f"Błąd klienta: {e}")
    finally:
        s.close()
        print("Połączenie zamknięte.")

if __name__ == "__main__":
    run_client()