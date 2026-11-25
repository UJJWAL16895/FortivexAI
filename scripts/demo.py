"""Start the local console and exercise its text endpoint in mock mode."""

import argparse
import asyncio
import json
import os
import socket
import sys
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx
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
                    if ready.get("mode") != "mock":
                        raise RuntimeError("Expected mock provider")
                    for prompt, expected in (
                        (
                            "My name is Asha. I work at Cedar Retail. We have three stores.",
                            "Is that correct?",
                        ),
                        ("yes", "confirmed"),
                        ("What do you remember?", "Cedar Retail"),
                        ("How much does Growth cost?", "2,499"),
                        ("My email is demo@example.test", "saved the demo contact"),
                        ("Book a demo", "UTC+05:30"),
                        ("Confirm booking", "Demo booked"),
                    ):
                        await ws.send(json.dumps({"text": prompt}))
                        while (reply := json.loads(await ws.recv()))["type"] not in {
                            "reply",
                            "error",
                        }:
                            pass
                        if reply["type"] != "reply" or expected not in reply["text"]:
                            raise RuntimeError("Unexpected scripted reply")
                        if expected == "2,499" and reply["citation"]["id"] != "growth":
                            raise RuntimeError("Expected the reviewed Growth citation")
                        print(f"Buyer: {prompt}\nAgent [{reply['mode']}]: {reply['text']}")
                        while json.loads(await ws.recv())["type"] != "profile":
                            pass
                    await ws.send(json.dumps({"text": "End conversation", "end_call": True}))
                    if "ended" not in json.loads(await ws.recv())["text"]:
                        raise RuntimeError("Expected end-of-conversation reply")
                async with httpx.AsyncClient(
                    base_url=f"http://{host}:{port}", trust_env=False
                ) as client:
                    crm = (await client.get("/api/crm")).json()
                    if len(crm["leads"]) != 1 or len(crm["bookings"]) != 1:
                        raise RuntimeError("Expected one saved lead and booking")
                    while True:
                        insights = (await client.get("/api/insights")).json()
                        if any(call["booked"] for call in insights["calls"]):
                            break
                        await asyncio.sleep(0.05)
                print(
                    "Demo passed: mock recall, cited price, confirmed booking, saved CRM and insights."
                )
        finally:
            server.should_exit = True
            await serving


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    with TemporaryDirectory(prefix="shelfpilot-demo-") as folder:
        os.environ.update(
            AGENT_MODE="mock",
            PUBLIC_DEMO="false",
            KNOWLEDGE_EMBEDDINGS="false",
            CRM_PATH=str(Path(folder) / "demo.sqlite3"),
        )
        asyncio.run(demo(args.port))
