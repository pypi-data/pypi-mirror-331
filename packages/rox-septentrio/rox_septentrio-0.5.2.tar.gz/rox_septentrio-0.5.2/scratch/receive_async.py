#!/usr/bin/env python3
"""
Receive data stream from http server

Copyright (c) 2024 ROX Automation - Jev Kuznetsov
"""

import asyncio

HOST = "localhost"
PORT = 28000


async def listen(host: str, port: int) -> None:
    reader, writer = await asyncio.open_connection(host, port)
    data_stream_str = ""

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            data_stream_str += data.decode(errors="ignore")
            print(data_stream_str)
    except asyncio.CancelledError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    try:
        asyncio.run(listen(HOST, PORT))
    except KeyboardInterrupt:
        print("done.")
