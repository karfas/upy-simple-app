#
# asy_udp_client.py
#
import time
import uasyncio as asyncio
import select
import socket

class AsyUDPClient:
    def __init__(self, addr, rx_timeout_ms = 1000, tx_timeout_ms = 200):
        self.addr = addr
        self.sock = None
        self.poller = None
        self.rx_timeout_us = rx_timeout_ms * 1000
        self.tx_timeout_us = tx_timeout_ms * 1000

    async def _connect(self):
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.connect(self.addr)
            self.sock.settimeout(0)
            self.poller = select.poll()
            self.poller.register(self.sock, select.POLLIN | select.POLLOUT)

    async def ready(self, mask, timeout_ms = None):
        await self._connect()
        t0 = time.ticks_us()
        while True:
            if (p := self.poller.poll(0)):
                if (p[0][1] & mask):
#                    print("ready: ",time.ticks_diff(time.ticks_us(), t0), " us")
                    return True
            else:
                if timeout_ms > 0 and time.ticks_diff(time.ticks_us(), t0) > timeout_us:
                    return False
            await asyncio.sleep(0)

    async def send(self, msg):
        if await self.ready(select.POLLOUT):
            return self.sock.write(msg)
        return None

    async def receive(self, n=None, timeout_ms=-1):
        if await self.ready(select.POLLIN, timeout_ms=timeout_ms):
            return self.sock.read()
        return None

    async def send_and_receive(self, msg, tries=1):
        for _ in range(tries):
            await self.send(msg)
            return await self.receive()
        return None

    async def disconnect(self):
        if not (self.sock is None):
            self.poller.unregister(self.sock)
            self.sock.close()
            self.sock = undef
