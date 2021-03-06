import sqlite3
from os import path
from random import choice
from smtplib import SMTP_SSL
from string import ascii_uppercase, digits

from aiohttp import web
from aiosqlite import connect

"""Создание базы данных, если такой не имеется"""
if not path.isfile("./database.sqlite"):
    conn = sqlite3.connect("./database.sqlite")
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE Friends(Friendship_id integer, User_1 Varchar(50), User_2 Varchar(50))')
    conn.commit()
    cursor.execute(
        'CREATE TABLE "Friendship_requests" ("ReqId"	INTEGER PRIMARY KEy,"From_user"	TEXT not null,"To_user"	TEXT not null)')
    conn.commit()
    cursor.execute(
        'CREATE TABLE "Messages" ("MessageID"	INTEGER UNIQUE,"From_user"	VARCHAR(50) NOT NULL,"To_user"	VARCHAR(50) NOT NULL,"Message_text"	TEXT NOT NULL,PRIMARY KEY("MessageID" AUTOINCREMENT))')
    conn.commit()
    cursor.execute(
        'CREATE TABLE "Users" ("UserId"	INTEGER UNIQUE,"Email"	VARCHAR(20) NOT NULL UNIQUE,"Login"	VARCHAR(20) NOT NULL UNIQUE,"Password"	VARCHAR(20) NOT NULL,PRIMARY KEY("UserId"))')
    conn.commit()
    cursor.execute(
        'CREATE TABLE "Verification" ("VerId"	INTEGER,"Email"	VARCHAR(50) NOT NULL,"Login"	VARCHAR(50) NOT NULL,"Password"	VARCHAR(50) NOT NULL,"CheckStr"	VARCHAR(50) NOT NULL,PRIMARY KEY("VerId"))')
    conn.commit()
    cursor.close()
    conn.close()

"""Обьявление класса сервера"""
class Server_http(web.View):

    async def get(self):
        return web.FileResponse(status=200, path="./picture.jpg")

    async def post(self):
        try:
            """Определение значения пути запроса"""
            path = str(self.request.match_info.get('path', None))

            """получение данных от пользователя"""
            data = await self.request.post()

            """Проверка пути запроса с помощью оператора множественного выбора"""
            match path:
                case "login":
                    return await self.login_def(str(data['login']), str(data['password']))

                case "registration":
                    return await self.registration_def(data["email"], data["login"], data["password"])

                case "message":
                    return await self.message_def(data["from_user"], data["to_user"], data["message_text"])

                case "check_messages":
                    return await self.check_messages(data["from_user"], data["to_user"])

                case "email_verification":
                    return await self.verification(data["email"], data["login"], data["password"], data["check_str"])

                case "email_verification_delete":
                    return await self.email_verification_delete(data["email"], data["login"])

                case "friendship_request":
                    return await self.friendship_request(data["from_user"], data["to_user"])

                case "friendship_requests_check":
                    return await self.friendship_requests_check(data["login"])
                    # return web.Response(status=404)
                case "friendship_requests_check_yes":
                    return await self.friendship_requests_check_yes(data["to_login"], data["from_login"])

                case "friendship_requests_check_no":
                    return await self.friendship_requests_check_no(data["to_login"], data["from_login"])

                case "friends_check":
                    return await self.friends_check(data["login"])

                case "delete_friend":
                    return await self.delete_friend(data["from_login"], data["delete_login"])

                case _:
                    """Если путь запроса не подходит под какое-либо из перечисленных значений, возвращается код 404"""
                    return web.Response(status=404)

        except Exception as ex:
            """Возврат ответа 500, если происходит какая либо непредвиденная ошибка"""
            print(ex, "post_request_error")
            return web.Response(status=500)

    """Ниже перечислены методы, которые выполняются при получении определенного запроса"""

    """Логин пользователя"""
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

    """Регистрация пользователя"""
    async def registration_def(self, email, login, password):
        try:
            request = f'SELECT * FROM Users WHERE Login = "{login}" OR Email = "{email}"'
            if not await self.sql_request_users(request):
                check_str = ''.join([choice(ascii_uppercase + digits) for _ in range(6)])

                # email_server = SMTP_SSL("smtp.mail.ru", 465)
                email_server = SMTP_SSL("smtp.gmail.com", 465)
                # email_server.login("yfen_python@mail.ru", "1UYJ5rCiuKbqKJyFLGtB")
                email_server.login("yurik2159@gmail.com", "gcsmzcnjtrptysqv")
                email_server.sendmail("yurik2159@gmail.com", email,
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

    """Веривикация регистрации пользователя"""
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

    """Пользователь отправил сообщение"""
    async def message_def(self, from_user, to_user, message_text):
        try:
            request = f'INSERT INTO Messages VALUES(Null, "{from_user}", "{to_user}", "{message_text}")'
            await self.sql_request_users(request)
            return web.Response(status=200)
        except Exception as ex:
            print(ex, "message_def error")
            web.Response(status=500)

    """Проверка наличия сообщений в чате между пользователями"""
    async def check_messages(self, from_user, to_user):
        request = f'SELECT * FROM Messages WHERE From_user = "{from_user}" AND To_user = "{to_user}" OR From_user = "{to_user}" AND To_user = "{from_user}"'
        conn = await connect("./database.sqlite")
        cursor = await conn.execute(request)
        result = await cursor.fetchall()
        await cursor.close()
        await conn.close()
        data = {}
        if result:
            for i in result[-50::1]:
                data[i[0]] = [i[1], i[3]]
            return web.json_response(data=data)
        else:
            return web.Response(status=404)

    """Удаление колонки верификации регистрации. Происходит, если пользователь отменил регистрацию или прошел ее"""
    async def email_verification_delete(self, email, login):

        request = f'DELETE FROM Verification WHERE Email = "{email}" AND Login = "{login}"'
        await self.sql_request_users(request)
        return web.Response(status=200)

    """Пользователь отправляет запрос в друзья"""
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

    """Проверка запросов в друзья"""
    async def friendship_requests_check(self, login):
        request = f'SELECT * FROM Friendship_requests WHERE To_user = "{login}"'
        # print(await self.sql_request_users(request))
        if not await self.sql_request_users(request):
            return web.Response(status=404)
        else:
            from_user = await self.sql_request_users(request)
            print(from_user)
            return web.Response(status=200, text=f"{from_user[1]}")

    """Пользователь принял запрос в друзья"""
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

    """Пользователь отклонил запрос в друзья"""
    async def friendship_requests_check_no(self, to_login, from_login):
        request = f'DELETE FROM Friendship_requests WHERE To_user = "{to_login}" AND From_user = "{from_login}" '
        await self.sql_request_users(request)
        return web.Response(status=200)

    """Проверка существования друзей пользователя"""
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

    """Пользователь удалил другого пользователя из друзей"""
    async def delete_friend(self, from_login, delete_login):
        request = f'DELETE FROM Friends WHERE User_1 = "{from_login}" AND User_2 = "{delete_login}" OR User_1 = "{delete_login}" AND User_2 = "{from_login}"'
        await self.sql_request_users(request)
        return web.Response(status=200)

    """Здесь происходит обработка и выполнение большинства запросов базы данных"""
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
    """Запуск сервера"""
    app = web.Application()
    app.router.add_view('/{path}', Server_http)
    app.router.add_view('', Server_http)
    web.run_app(app, port=8080)
