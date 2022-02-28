import socket

class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind(('', 5555))

        self.sock.listen(3)



    def mainloop(self):
        while True:
            self.conn, self.address = self.sock.accept()
            print("connected:", self.address)
            self.data = self.conn.recv(1024)
            print(self.data)
            self.conn.send(self.data.upper())
            self.conn.close()

if __name__ == "__main__":
        Server().mainloop()
