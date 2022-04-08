from aiohttp import web


class Server(web.View):

    async def post(self):
        return web.Response(text="asd")


if __name__ == "__main__":
    app = web.Application()
    app.router.add_view('', Server)
    web.run_app(app, port=8080)
