import asyncio


async def async_func(task_no, i):
    print(f'{task_no}: Запуск ...')
    await asyncio.sleep(i)
    print(f'{task_no}: ... Готово!')


async def main():
    await asyncio.gather(async_func("fast fast", 2), async_func(
        "kick kick", 2), async_func("bi ba", 2))
    await async_func("i'm solo boy", 3)

# if __name__ == "__main__":
loop = asyncio.get_event_loop()
a = loop.create_task(async_func("just run", 1))
b = loop.create_task(async_func("just run", 2))
# loop.create_task(async_func("just run", 0))
loop.run_until_complete(asyncio.wait([a, b]))
# asyncio.run(main())
