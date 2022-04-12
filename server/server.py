from random import choice
from smtplib import SMTP_SSL
from string import ascii_uppercase, digits

from aiohttp import web
from aiosqlite import connect


# пароль для ящика 1UYJ5rCiuKbqKJyFLGtB


class Server_http(web.View):

    async def get(self):
        # return web.Response(status=200)
        return web.FileResponse(status=200, path="./picture.jpg")

    async def post(self):
        try:
            path = str(self.request.match_info.get('path', None))
            # print(path)
            data = await self.request.post()

            if path == "login":
                return await self.login_def(str(data['login']), str(data['password']))

            elif path == "registration":
                return await self.registration_def(data["email"], data["login"], data["password"])

            elif path == "message":
                return await self.message_def(data["from_user"], data["to_user"], data["message_text"])

            elif path == "check_messages":
                return await self.check_messages(data["from_user"], data["to_user"])

            elif path == "email_verification":
                return await self.verification(data["email"], data["login"], data["password"], data["check_str"])

            elif path == "email_verification_delete":
                return await self.email_verification_delete(data["email"], data["login"])

            elif path == "friendship_request":
                return await self.friendship_request(data["from_user"], data["to_user"])

            elif path == "friendship_requests_check":
                return await self.friendship_requests_check(data["login"])
                # return web.Response(status=404)
            elif path == "friendship_requests_check_yes":
                return await self.friendship_requests_check_yes(data["to_login"], data["from_login"])

            elif path == "friendship_requests_check_no":
                return await self.friendship_requests_check_no(data["to_login"], data["from_login"])

            elif path == "friends_check":
                return await self.friends_check(data["login"])

            elif path == "delete_friend":
                return await self.delete_friend(data["from_login"], data["delete_login"])

            else:
                return web.Response(status=404)

        except Exception as ex:
            print(ex, "post_request_error")
            return web.Response(status=500)

    async def login_def(self, login, password):
        try:

            request = f'SELECT * FROM Users WHERE Login = "{login}" AND Password = "{password}" '
            if not await self.sql_request_users(request):
                return web.Response(status=404)
            else:
                return web.Response(status=200)

        except Exception as ex:
            print(ex, "login_error")
            return web.Response(status=500)

    async def registration_def(self, email, login, password):
        try:
            request = f'SELECT * FROM Users WHERE Login = "{login}" OR Email = "{email}"'
            if not await self.sql_request_users(request):
                check_str = ''.join([choice(ascii_uppercase + digits) for _ in range(6)])

                email_server = SMTP_SSL("smtp.mail.ru", 465)
                email_server.login("yfen_python@mail.ru", "1UYJ5rCiuKbqKJyFLGtB")
                email_server.sendmail("yfen_python@mail.ru", email,
                                      f'Subject: Подтвердите свою регистрацию в YFenMessenger\nВаш код подтверждения: {check_str}'.encode(
                                          "utf-8"))

                request = f'INSERT INTO Verification VALUES(Null, "{email}", "{login}", "{password}","{check_str}")'
                await self.sql_request_users(request)

                return web.Response(status=200)
            else:
                return web.Response(status=403)
            # email_server.close()

        except Exception as ex:
            print(ex, "registration_error")
            return web.Response(status=550)

    async def verification(self, email, login, password, check_str):
        try:

            request = f'SELECT * FROM Verification WHERE Email = "{email}" AND Login = "{login}" AND Password = "{password}" AND CheckStr = "{check_str}"'
            if not await self.sql_request_users(request):
                return web.Response(status=403)
            else:
                request = f'DELETE FROM Verification WHERE Email = "{email}" AND Login = "{login}"'
                await self.sql_request_users(request)
                request = f'INSERT INTO Users VALUES(Null, "{email}", "{login}", "{password}")'
                await self.sql_request_users(request)
                return web.Response(status=200)
        except Exception as ex:
            print(ex, "verification_error")
            return web.Response(status=500)

    async def message_def(self, from_user, to_user, message_text):
        try:
            request = f'INSERT INTO Messages VALUES(Null, "{from_user}", "{to_user}", "{message_text}")'
            await self.sql_request_users(request)
            return web.Response(status=200)
        except Exception as ex:
            print(ex, "message_def error")
            web.Response(status=500)

    async def check_messages(self, from_user, to_user):
        request = f'SELECT * FROM Messages WHERE From_user = "{from_user}" AND To_user = "{to_user}" OR From_user = "{to_user}" AND To_user = "{from_user}"'
        conn = await connect("./database.sqlite")
        cursor = await conn.execute(request)
        result = await cursor.fetchall()
        await cursor.close()
        await conn.close()
        data = {}
        if result:
            for i in result:
                data[i[0]] = [i[1], i[3]]
            return web.json_response(data=data)
        else:
            return web.Response(status=404)

    async def email_verification_delete(self, email, login):

        request = f'DELETE FROM Verification WHERE Email = "{email}" AND Login = "{login}"'
        await self.sql_request_users(request)
        return web.Response(status=200)

    async def friendship_request(self, from_user, to_user):
        request = f'SELECT * FROM Friends WHERE User_1 = "{from_user}" AND User_2 = "{to_user}" OR User_1 = "{to_user}" AND User_2 = "{from_user}"'
        if not await self.sql_request_users(request):
            request = f'SELECT * FROM Users WHERE Login = "{to_user}"'
            if not await self.sql_request_users(request):
                return web.Response(status=404)
            else:
                request = f'SELECT * FROM Friendship_requests WHERE From_user = "{from_user}" AND To_user = "{to_user}" OR From_user = "{to_user}" AND To_user = "{from_user}"'
                if not await self.sql_request_users(request):
                    request = f'INSERT INTO Friendship_requests VALUES(Null, "{from_user}", "{to_user}")'
                    await self.sql_request_users(request)
                    return web.Response(status=200)
                else:
                    return web.Response(status=406)
        else:
            return web.Response(status=406)

    async def friendship_requests_check(self, login):
        request = f'SELECT * FROM Friendship_requests WHERE To_user = "{login}"'
        # print(await self.sql_request_users(request))
        if not await self.sql_request_users(request):
            return web.Response(status=404)
        else:
            from_user = await self.sql_request_users(request)
            print(from_user)
            return web.Response(status=200, text=f"{from_user[1]}")

    async def friendship_requests_check_yes(self, to_login, from_login):
        request = f'SELECT * FROM Friendship_requests WHERE To_user = "{to_login}" AND From_user = "{from_login}"'
        # print(from_login, to_login)
        if not await self.sql_request_users(request):
            return web.Response(status=404)
        else:
            request = f'INSERT INTO Friends VALUES(Null, "{from_login}", "{to_login}")'
            await self.sql_request_users(request)

            request = f'DELETE FROM Friendship_requests WHERE To_user = "{to_login}" AND From_user = "{from_login}"'
            await self.sql_request_users(request)

            return web.Response(status=200)

    async def friendship_requests_check_no(self, to_login, from_login):
        request = f'DELETE FROM Friendship_requests WHERE To_user = "{to_login}" AND From_user = "{from_login}"'
        await self.sql_request_users(request)
        return web.Response(status=200)

    async def friends_check(self, login):
        request = f'SELECT * FROM Friends WHERE User_1 = "{login}" OR User_2 = "{login}"'
        conn = await connect("./database.sqlite")
        cursor = await conn.execute(request)
        result = await cursor.fetchall()
        await cursor.close()
        await conn.close()
        a = str()
        if result:
            for i in result:
                if i[1] == login:
                    a += str(i[2] + " ")
                elif i[2] == login:
                    a += str(i[1] + " ")

            return web.Response(status=200, text=a.strip())
        else:
            return web.Response(status=404)

    async def delete_friend(self, from_login, delete_login):
        request = f'DELETE FROM Friends WHERE User_1 = "{from_login}" AND User_2 = "{delete_login}" OR User_1 = "{delete_login}" AND User_2 = "{from_login}"'
        await self.sql_request_users(request)
        return web.Response(status=200)

    """----------------------------------------sql запросы---------------------------------------"""

    async def sql_request_users(self, request):
        try:
            conn = await connect("./database.sqlite")
            cursor = await conn.execute(request)
            if "SELECT" in request:
                result = await cursor.fetchone()
                await cursor.close()
                await conn.close()
                return result
            elif "DELETE" in request or "INSERT" in request or "CREATE" in request:
                await conn.commit()
                await cursor.close()
                await conn.close()
        except Exception as ex:
            print(ex, "sql_error")
            return web.Response(status=500)


if __name__ == "__main__":
    app = web.Application()
    app.router.add_view('/{path}', Server_http)
    app.router.add_view('', Server_http)
    web.run_app(app, port=8080)
