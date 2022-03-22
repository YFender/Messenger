# from http.server import BaseHTTPRequestHandler, HTTPServer
# from urllib import parse
from aiosqlite import connect
from smtplib import SMTP_SSL
# import asyncio
from aiohttp import web
# from multidict import MultiDict, CIMultiDictProxy
from random import choice
from string import ascii_uppercase, digits

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

            elif path == "email_verification":
                return await self.verification(data["email"], data["login"], data["password"], data["check_str"])

            elif path == "friendship_request":
                return await self.friendship_request()

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

            if not await self.sql_request_users(request, "registration_check"):
                check_str = ''.join(
                    [choice(ascii_uppercase + digits)for i in range(6)])
                try:
                    email_server.sendmail(
                        "yfen_python@mail.ru", email, f'Subject: Подтвердите свою регистрацию в YFenMessenger\nВаш код подтверждения: {check_str}'.encode("utf-8"))
                except:
                    return web.Response(status=550)

                request = f'INSERT INTO Verification VALUES(Null, "{email}", "{login}", "{password}","{check_str}")'
                await self.sql_request_users(request, "email_verification_plan")
                print(email, login, password, check_str)

                return web.Response(status=200)
            else:
                return web.Response(status=403)

        except Exception as ex:
            print(ex)
            return web.Response(status=500)

    async def verification(self, email, login, password, check_str):
        try:
            print(email, login, password, check_str)
            request = f'SELECT * FROM Verification WHERE Email = "{email}" AND Login = "{login}" AND Password = "{password}" AND CheckStr = "{check_str}"'
            if await self.sql_request_users(request, "verification_check", email=f"{email}", login=f"{login}") == False:
                return web.Response(status=403)
            else:
                request = f'INSERT INTO Users VALUES(Null, "{email}", "{login}", "{password}")'
                await self.sql_request_users(request, "registration_final")
                return web.Response(status=200)
        except Exception as ex:
            print(ex)
            return web.Response(status=500)

    async def message_def(self, data):
        return web.Response(status=200)

    async def friendship_request(self):
        pass

        """----------------------------------------sql запросы---------------------------------------"""
    async def sql_request_users(self, request, request_type, **kwargs):
        try:
           if request_type == "login":
               conn = await connect("./users.sqlite")
               cursor = await conn.execute(request)
               result = await cursor.fetchone()
               await cursor.close()
               await conn.close()
               return result

           elif request_type == "registration_check":
               conn = await connect("./users.sqlite")
               cursor = await conn.execute(request)
               result = await cursor.fetchone()
               await cursor.close()
               await conn.close()
               return result

           elif request_type == "verification_check":
               conn = await connect("./email_verification.sqlite")
               cursor = await conn.execute(request)
               result = await cursor.fetchone()
               if not result:
                   await cursor.close()
                   await conn.close()
                   return False
               else:
                   email = kwargs["email"]
                   login = result["login"]
                   print(email, login)
                   cursor = await conn.execute(f'DELETE FROM Verification WHERE Email = "{email}" AND Login = "{login}"')
                   await conn.commit()
                   await cursor.close()
                   await conn.close()
                   return True

           elif request_type == "registration_final":
               conn = await connect("./users.sqlite")
               cursor = await conn.execute(request)
               await conn.commit()
               await cursor.close()
               await conn.close()

           elif request_type == "email_verification_plan":
               conn = await connect("./email_verification.sqlite")
               cursor = await conn.execute(request)
               await conn.commit()
               await cursor.close()
               await conn.close()

           elif request_type == "friendship_request":
               conn = await connect("./email_verification.sqlite")
               cursor = await conn.execute(request)
               await conn.commit()
               await cursor.close()
               await conn.close()

           # print("db zakrita")
        except Exception as ex:
            print(ex)
            return web.Response(status=500)


if __name__ == "__main__":
    app = web.Application()
    app.router.add_view('/{path}', Server_http)
    app.router.add_view('', Server_http)

    web.run_app(app, port=8080)
