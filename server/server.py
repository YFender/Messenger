from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import sqlite3
# import re
from smtplib import SMTP_SSL
from random import randint

conn = sqlite3.connect("users.sqlite")
cursor = conn.cursor()

# пароль для ящика XQb56ic4VCy5ccwuvviH

email_server = SMTP_SSL("smtp.mail.ru", 465)
email_server.login("yfen_python@mail.ru", "XQb56ic4VCy5ccwuvviH")


class Server_http(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        try:
            # ctype, pdict = CGIHTTPRequestHandler.
            print(self.headers)
            # ctype, pdict = cgi.parse_header(self.headers['content-type'])
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            print(body)
            data = urllib.parse.parse_qs(body.decode())

            if self.path == "/login":

                login = str(data['login']).strip("[").rstrip("]")
                if login[0] == '"':
                    login = login.strip('"')
                elif login[0] == "'":
                    login = login.strip("'")

                password = str(data['password']).strip("[").rstrip("]")
                if password[0] == '"':
                    password = password.strip('"')
                elif password[0] == "'":
                    password = password.strip("'")

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

                email = str(data['email']).strip("[").rstrip("]")
                if email[0] == '"':
                    email = email.strip('"')
                elif email[0] == "'":
                    email = email.strip("'")

                login = str(data['login']).strip("[").rstrip("]")
                if login[0] == '"':
                    login = login.strip('"')
                elif login[0] == "'":
                    login = login.strip("'")

                password = str(data['password']).strip("[").rstrip("]")
                if password[0] == '"':
                    password = password.strip('"')
                elif password[0] == "'":
                    password = password.strip("'")

                checknum = randint(10000, 99999)

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
        except:
            self.send_response(500)
            self.end_headers()


server = HTTPServer(('localhost', 8080), Server_http)
print('Started httpserver on port ', 8080)

# Wait forever for incoming http requests
server.serve_forever()
