from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import sqlite3

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

            login = str(data['login']).replace(
                "[", "").replace("]", "").replace("'", "").lower()

            password = str(data['password']).replace(
                "[", "").replace("]", "").replace("'", "")
            print(login, password)
            cursor.execute(
                f'SELECT * FROM Users WHERE Login = "{login}" AND Password = "{password}" ')
            result = cursor.fetchall()
            if not result:
                self.send_response(404)
                self.end_headers()
            else:
                self.send_response(200)
                self.end_headers()

        if self.path == "/registration":
            email = str(data['email']).replace(
                "[", "").replace("]", "").replace("'", "").lower()

            login = str(data['login']).replace(
                "[", "").replace("]", "").replace("'", "").lower()

            password = str(data['password']).replace(
                "[", "").replace("]", "").replace("'", "").lower()

            print(email, login, password)
            cursor.execute(
                f'SELECT * FROM Users WHERE Login = "{login}" OR Email = "{email}"')
            result = cursor.fetchall()

            if not result:
                cursor.execute(
                    f'INSERT INTO Users VALUES(Null, "{email}", "{login}", "{password}")')
                conn.commit()
                self.send_response(200)
                self.end_headers()
            else:
                self.send_response(403)
                self.end_headers()

            print("\n")


server = HTTPServer(('localhost', 8080), Server_http)
print('Started httpserver on port ', 8080)

# Wait forever for incoming http requests
server.serve_forever()
