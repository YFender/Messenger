import socket

sock = socket.socket()

sock.bind(('', 5555))

sock.listen(1)

conn, address = sock.accept()
print("connected:", address)

while True:
    data = conn.recv(1024)
    conn.send(data.upper())
