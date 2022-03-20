# from http.server import BaseHTTPRequestHandler, HTTPServer
# from urllib import parse
from aiosqlite import connect
from smtplib import SMTP_SSL
# import asyncio
from aiohttp import web
# from multidict import MultiDict, CIMultiDictProxy
from random import randint

# пароль для ящика XQb56ic4VCy5ccwuvviH

email_server = SMTP_SSL("smtp.mail.ru", 465)
email_server.login("yfen_python@mail.ru", "XQb56ic4VCy5ccwuvviH")


class Server_http(web.View):

    async def get(self):
        return web.Response(status=200)

    async def post(self):
        try:
            path = str(self.request.match_info.get('path', None))
            print(path)
            data = await self.request.post()
            # print(data)
            # print(data['login'])

            if path == "login":
                return await self.login_def(str(data['login']), str(data['password']))

            elif path == "registration":
                return await self.registration_def(data["email"], data["login"], data["password"])

            elif path == "message":
                return await self.message_def(data)

            else:
                return web.Response(status=404)

        except Exception as ex:
            return web.Response(status=500)
            print(ex)

    async def login_def(self, login, password):
        try:

            request = f'SELECT * FROM Users WHERE Login = "{login}" AND Password = "{password}" '

            if not await self.sql_request_users(request, "login"):
                return web.Response(status=404)
                print("not")
            else:
                print("not not")
                return web.Response(status=200)

        except Exception as ex:
            return web.Response(status=500)
            print(ex)

    async def registration_def(self, email, login, password):
        try:
            request = f'SELECT * FROM Users WHERE Login = "{login}" OR Email = "{email}"'
            # cursor.execute(
            #     f'SELECT * FROM Users WHERE Login = "{login}" OR Email = "{email}"')
            # result = cursor.fetchall()

            if not await self.sql_request_users(request, "registration"):
                check_num = randint(100000, 999999)
                request = f'INSERT INTO Users VALUES(Null, "{email}", "{login}", "{password}")'
                await self.sql_request_users(request)
                return web.Response(status=200)
            else:
                return web.Response(status=403)

        except Exception:
            return web.Responce(status=500)

    async def message_def(self, data):
        return web.Response(status=200)

    async def sql_request_users(self, request, request_type):
        conn = await connect("./users.sqlite")
        if request_type == "login":
            cursor = await conn.execute(request)
            result = await cursor.fetchone()
            await cursor.close()
            await conn.close()
            return result
        elif request_type == "registration":
            cursor = await conn.execute(request)
            await conn.commit()
        await cursor.close()
        await conn.close()
        # print("db zakrita")


if __name__ == "__main__":
    app = web.Application()
    app.router.add_view('/{path}', Server_http)
    app.router.add_view('', Server_http)

    web.run_app(app, port=8080)
