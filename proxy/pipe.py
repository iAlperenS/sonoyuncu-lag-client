import asyncio
import keyboard
from collections import deque

from utils.errors import PipeError
from utils.console import Console
from utils.sv import Saved

lag_enabled = False

async def keyboard_listener():
    global lag_enabled

    while True:
        try:
            if keyboard.is_pressed(Saved.LAG_KEY):
                lag_enabled = not lag_enabled
                status = "ON" if lag_enabled else "OFF"
                Console.log(f"[LAG] CLIENT: {status}")
                await asyncio.sleep(0.4)
        except:
            pass

        await asyncio.sleep(0.01)


async def flush_buffer(writer, packet_buffer):
    if not packet_buffer:
        return

    try:
        Console.log(f"[LAG] {len(packet_buffer)} paket gönderiliyor")
        combined = b"".join(packet_buffer)
        writer.write(combined)
        await writer.drain()
        packet_buffer.clear()

    except Exception as e:
        Console.log(f"[LAG] Flush error: {e}")


async def pipe(reader, writer, direction):
    global lag_enabled
    packet_buffer = deque()
    last_lag_state = False
    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break

            out_bytes = data
            if direction == "SEND":

                if b"127.0.0.1" in data:

                    pattern = b'J\x00/D127.0.0.1'
                    replacement = b'U\x00/Omc.sonoyuncu.network'

                    pattern2 = b'<\x00/6127.0.0.1'
                    replacement2 = b'G\x00/Amc.sonoyuncu.network'

                    try:

                        if pattern in data:
                            out_bytes = data.replace(pattern, replacement)
                            Console.log("[1] Sonoyuncu giriş bypass edildi")

                        elif pattern2 in data:
                            out_bytes = data.replace(pattern2, replacement2)
                            Console.log("[2] Sonoyuncu giriş bypass edildi")

                    except Exception as e:
                        Console.log(f"Replace error: {e}")
            if lag_enabled:
                packet_buffer.append(out_bytes)
                Console.log(
                    f"[LAG] {len(out_bytes)} bytes "
                    f"(Toplam: {len(packet_buffer)})"
                )
                last_lag_state = True
                continue

            if last_lag_state and not lag_enabled:
                await flush_buffer(writer, packet_buffer)

            last_lag_state = lag_enabled
            writer.write(out_bytes)
            await writer.drain()
    except Exception as e:
        raise PipeError(f"Pipe error: {e}")
    finally:
        try:
            await flush_buffer(writer, packet_buffer)
            writer.close()
            await writer.wait_closed()
        except:
            pass