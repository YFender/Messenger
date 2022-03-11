# import socket
# from pyngrok import ngrok
from http.server import BaseHTTPRequestHandler, HTTPServer
# from io import BytesIO
# import cgi
import urllib
import sqlite3
#
# class Server:
#     def __init__(self):
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#
#         self.sock.bind(('localhost', 5000))
#         print(self.sock)
#
#         self.sock.listen(3)
#
#     def mainloop(self):
#         while True:
#             self.conn, self.address = self.sock.accept()
#             print("connected:", self.address)
#             self.data = self.conn.recv(1024)
#             print(self.data)
#             self.conn.send(self.data.upper())
#             self.conn.close()

# if __name__ == "__main__":
#         Server().mainloop()

conn = sqlite3.connect("users.sqlite")
cursor = conn.cursor()


class Server_http(BaseHTTPRequestHandler):

    def do_GET(self):
        print(self.headers)

        self.send_response(200)
        self.end_headers()
        # self.wfile.write()

    def do_POST(self):
        # ctype, pdict = CGIHTTPRequestHandler.
        print(self.headers)
        # ctype, pdict = cgi.parse_header(self.headers['content-type'])
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        print(body)
        data = urllib.parse.parse_qs(body.decode())
        print(data["login"])

        print("\n", self.path)
        if self.path == "/login":
            login = data['login']
            password = data['password']
            cursor.execute(
                f'SELECT * FROM Users WHERE Login = "{login}" AND Password = "{password}" ')
            result = cursor.fetchall()
            print(result)
        self.send_response(200)
        self.end_headers()


server = HTTPServer(('localhost', 8080), Server_http)
print('Started httpserver on port ', 8080)

# Wait forever for incoming http requests
server.serve_forever()
