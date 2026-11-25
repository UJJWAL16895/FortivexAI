"""Start the local console and exercise its text endpoint in mock mode."""

import argparse
import asyncio
import json
import os
import socket
from contextlib import closing

from uvicorn import Config, Server
from websockets.asyncio.client import connect

from src.api.app import create_app


async def demo(port: int) -> None:
    server = Server(
        Config(create_app(), log_level="warning", access_log=False, ws="websockets-sansio")
    )
    with closing(socket.socket()) as listener:
        listener.bind(("127.0.0.1", port))
        host, port = listener.getsockname()
        serving = asyncio.create_task(server.serve(sockets=[listener]))
        try:
            async with asyncio.timeout(10):
                while not server.started:
                    if serving.done():
                        await serving
                        raise RuntimeError("Demo server did not start")
                    await asyncio.sleep(0.02)
                async with connect(f"ws://{host}:{port}/ws/text") as ws:
                    ready = json.loads(await ws.recv())
                    if ready != {"type": "ready", "provider": "mock"}:
                        raise RuntimeError("Expected mock provider")
                    for prompt, expected in (
                        ("Can I manage three stores?", "locations"),
                        ("How much does it cost?", "pricing"),
                        ("Can I see a demo?", "demo"),
                    ):
                        await ws.send(json.dumps({"text": prompt}))
                        reply = json.loads(await ws.recv())
                        if reply["type"] != "reply" or expected not in reply["text"]:
                            raise RuntimeError("Unexpected scripted reply")
                        print(f"Buyer: {prompt}\nAgent [mock]: {reply['text']}")
                    print("Demo passed: 3 replies over WebSocket (mock).")
        finally:
            server.should_exit = True
            await serving


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    os.environ["AGENT_MODE"] = "mock"
    asyncio.run(demo(args.port))
