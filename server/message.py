
import ssl
import urllib
from http.server import HTTPServer, BaseHTTPRequestHandler

import cgi


import sys

import argparse


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        print(self.headers)
        # ctype, pdict = cgi.parse_header(self.headers['content-type'])
        # print(ctype, pdict)
        # data = None
        #
        # if ctype == 'multipart/form-data':
        #     pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        #     pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
        #     data = cgi.parse_multipart(self.rfile, pdict)
        #     print("multi")
        # elif ctype == 'application/x-www-form-urlencoded':
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = urllib.parse.parse_qs(body.decode())
        print("applic")

        print(data)
        print()
        while True:
            try:
                if self.path == '/':
                    if "password" == data['key']:
                        if data["msisdn"] is None or data["call_start_time"] is None:
                            self.send_response(400)
                            self.end_headers()
                            self.wfile.write(b'bb')
                            return
                        result = "OK!"
                        if result is None:
                            result = b'ok'
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(result)
                        return
                if self.path == '/analysis':
                    if 'name' == data['key']:
                        self.send_response(200)
                        self.send_header(
                            "Content-type", "application/vnd.ms-excel")
                        self.send_header(
                            'Content-Disposition', 'attachment; filename="tmpForAnalisysRequest.xls"')
                        self.end_headers()
                        return
                    else:
                        print("AccessDenied! Name {0}, ip {1}".format(
                            data['name'], self.headers))
                        break
            except KeyError:
                print("KeyError! Name {0}, ip {1}. \n Data contain: ".format(
                    data['name'], self.headers, data))
                break
            except TypeError:
                print("TypeError! Name {0}, ip {1}".format(
                    data['name'], self.client_address))
                break
        self.send_response(403)
        self.end_headers()
        self.wfile.write(b'bb')
        return

    def do_GET(self):
        try:
            if self.path == '/':
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                file = open("./html/index.html", "rb")
                self.wfile.write(file.read())
                file.close()
                return
            else:
                file = open("./html" + self.path, "rb")
                content = file.read()
                file.close()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content)
                return
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            file = open("./html/404.html", "rb")
            self.wfile.write(file.read())
            file.close()
            return
        except IsADirectoryError:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            file = open("./html/404.html", "rb")
            self.wfile.write(file.read())
            file.close()
            return


def initServer(args):
    httpd = HTTPServer(('0.0.0.0', int(args.port)), SimpleHTTPRequestHandler)
    if args.ssl:
        httpd.socket = ssl.wrap_socket(httpd.socket,
                                       ssl_version=ssl.PROTOCOL_TLS,
                                       keyfile=args.keyfile,
                                       certfile=args.certfile, server_side=True)
    httpd.serve_forever()


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--ssl', dest='ssl', action='store_true')
    parser.set_defaults(feature=False)
    parser.add_argument('-p', '--port', default=8080)
    parser.add_argument('-k', '--keyfile')
    parser.add_argument('-c', '--certfile')

    return parser.parse_args(sys.argv[1:])


args = parseArgs()
print(args)

initServer(args)
