import asyncio
import time

async def foo():
    print("Foo started")
    await asyncio.sleep(2)
    print("Foo completed")

async def bar():
    print("Bar started")
    await asyncio.sleep(3)
    print("Bar completed")

async def main():
    task1 = asyncio.create_task(foo())
    task2 = asyncio.create_task(bar())

    # 主程序可以在这里执行其他操作，不会等待上面的任务完成
    print("Main program continues")

    # 等待任务完成（如果需要）
    # await asyncio.gather(task1, task2)

    # 主程序可以在这里执行其他操作，或者直接结束

asyncio.run(main())
