import socket

sock = socket.socket()
sock.connect(("localhost", 5555))

while True:
    print("vvedite: ")
    a = input()
    sock.send(a.encode())
    data = sock.recv(1024)
    print(data)
