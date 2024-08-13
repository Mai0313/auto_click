import asyncio
from threading import Lock, Thread

from pydantic import BaseModel
from rich.console import Console

GLOBAL_LIST = []
console = Console()

lock = Lock()


class AsyncFOO(BaseModel):
    async def add_o_to_list(self) -> None:
        global GLOBAL_LIST
        GLOBAL_LIST.append("O")

    async def add_x_to_list(self) -> None:
        global GLOBAL_LIST
        GLOBAL_LIST.append("x")


class SyncFOO:
    def add_o_to_list(self) -> None:
        global GLOBAL_LIST
        GLOBAL_LIST.append("O")

    def add_x_to_list(self) -> None:
        global GLOBAL_LIST
        GLOBAL_LIST.append("x")


def main_with_lock() -> None:
    foo_func = SyncFOO()
    with lock:
        console.print(f"Line 1: {GLOBAL_LIST}")
        foo_func.add_o_to_list()
        console.print(f"Line 2: {GLOBAL_LIST}")
        foo_func.add_x_to_list()
        console.print(f"Line 3: {GLOBAL_LIST}")


def main_without_lock() -> None:
    foo_func = SyncFOO()
    console.print(f"Line 1: {GLOBAL_LIST}")
    foo_func.add_o_to_list()
    console.print(f"Line 2: {GLOBAL_LIST}")
    foo_func.add_x_to_list()
    console.print(f"Line 3: {GLOBAL_LIST}")


async def a_main() -> None:
    foo_func = AsyncFOO()
    console.print(f"Line 1: {GLOBAL_LIST}")
    test = foo_func.add_o_to_list()
    console.print(f"Line 2: {GLOBAL_LIST}")
    await foo_func.add_x_to_list()
    console.print(f"Line 3: {GLOBAL_LIST}")
    await test
    console.print(f"Line 4: {GLOBAL_LIST}")


async def a_main_tasks() -> None:
    await asyncio.gather(a_main(), a_main(), a_main(), a_main())


if __name__ == "__main__":
    # Single run with lock
    main_with_lock()
    # Single run without lock
    main_without_lock()
    # Single run with async
    asyncio.run(a_main())

    # 4 runs with lock
    threads = []
    for i in range(4):
        th = Thread(target=main_with_lock)
        th.start()
        threads.append(th)
    for th in threads:
        th.join()

    # 4 runs without lock
    threads = []
    for i in range(4):
        th = Thread(target=main_without_lock)
        th.start()
        threads.append(th)
    for th in threads:
        th.join()

    # 4 runs with async
    asyncio.run(a_main_tasks())
