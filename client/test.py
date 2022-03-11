import socket


class Client():
    # def __init_

    def mainloop(self):
        while True:
            self.sock = socket.socket()
            a = input(">")
            if a != "":
                self.sock.connect(("185.32.135.106", 80))
                self.sock.send(a.encode())
                self.data = self.sock.recv(1024)
                print(self.data)
                self.sock.detach()


if __name__ == "__main__":
    Client().mainloop()
