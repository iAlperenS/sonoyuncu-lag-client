from proxy.client import handle_client
from utils.console import Console
from utils.sv import Saved
from proxy.pipe import keyboard_listener

import asyncio
import signal

async def main():
    asyncio.create_task(keyboard_listener())
    server = await asyncio.start_server(handle_client, Saved.LOCAL_IP, Saved.LOCAL_PORT)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    Console.log(f"Proxy: {addrs}")

    # trick
    async with server:
        await server.serve_forever()

loop = asyncio.get_event_loop()
for sig in (signal.SIGINT, signal.SIGTERM):
    try: loop.add_signal_handler(sig, loop.stop)
    except Exception: pass
try: loop.run_until_complete(main())
except KeyboardInterrupt: Console.log("Kapatılıyor...")
finally: loop.close()