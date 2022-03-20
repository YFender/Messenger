import aiosqlite
import asyncio


async def asd():
    db = await aiosqlite.connect("./users.sqlite")
    cursor = await db.execute('SELECT * FROM Users WHERE Email = "yavmayn@bk.com"')
    row = await cursor.fetchone()
    print(row)
    rows = await cursor.fetchall()
    print(rows)
    await cursor.close()
    await db.close()

loop = asyncio.get_event_loop()
a = loop.create_task(asd())
loop.run_until_complete(asyncio.wait([a]))
