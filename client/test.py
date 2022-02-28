import socket

class Client():
    #def __init__(self):


    def mainloop(self):
        while True:
            self.sock = socket.socket()
            a = input(">")
            if a!="":
                self.sock.connect(("localhost", 5555))
                self.sock.send(a.encode())
                self.data = self.sock.recv(1024)
                print(self.data)
                self.sock.detach()

if __name__ == "__main__":
    Client().mainloop()
