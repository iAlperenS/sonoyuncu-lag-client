import asyncio
from utils.sv import Saved
from .pipe import pipe
from utils.errors import ProxyConnectionError
from utils.console import Console

async def handle_client(client_reader, client_writer):
    peer = client_writer.get_extra_info('peername')
    Console.log(f"[+] Yeni client: {peer}")
    try:
        remote_reader, remote_writer = await asyncio.open_connection(Saved.REMOTE_HOST, Saved.REMOTE_PORT)
    except Exception as e:
        client_writer.close()
        await client_writer.wait_closed()
        raise ProxyConnectionError(f"[!] Server bağlanama hatası: {e}")

    t1 = asyncio.create_task(pipe(client_reader, remote_writer, 'SEND'))
    t2 = asyncio.create_task(pipe(remote_reader, client_writer, 'RECV'))

    done, pending = await asyncio.wait([t1, t2], return_when=asyncio.FIRST_COMPLETED)
    for p in pending:
        p.cancel()

    try:
        remote_writer.close(); await remote_writer.wait_closed()
    except: pass
    try:
        client_writer.close(); await client_writer.wait_closed()
    except: pass
    Console.log(f"[-] Client kapandı: {peer}")
