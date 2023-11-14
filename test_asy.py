import uasyncio as asyncio


async def test():
    print("in test")
    await asyncio.sleep(0)

async def start():
    tsk = asyncio.create_task(test())
    g = await asyncio.gather(tsk)

def run():
    asyncio.run(start())

if __name__ == "__main__":
    run()
