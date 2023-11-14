#
# asy_ntptime.py
#
import time
import struct
import uasyncio as asyncio
import socket

from asy_udp_client import AsyUDPClient

# The NTP host can be configured at runtime by doing: ntptime.host = 'myhost.org'
_host = "pool.ntp.org"

async def asy_ntp_time(host=_host):
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]

    print("addr:", addr)

    cli = AsyUDPClient(addr)

    tsk = asyncio.create_task(cli.send_and_receive(NTP_QUERY))
    msg = await tsk

    if msg is None:
        print("asy_ntp_time returns None")
        return None

    val = struct.unpack("!I", msg[40:44])[0]

    EPOCH_YEAR = time.gmtime(0)[0]
    if EPOCH_YEAR == 2000:
        # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        NTP_DELTA = 3155673600
    elif EPOCH_YEAR == 1970:
        # (date(1970, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        NTP_DELTA = 2208988800
    else:
        raise Exception("Unsupported epoch: {}".format(EPOCH_YEAR))

    print("asy_ntp_time returns:", val - NTP_DELTA)
    return val - NTP_DELTA

# There's currently no timezone support in MicroPython, and the RTC is set in UTC time.
def settime():
    t = time()
    import machine

    tm = time.gmtime(t)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))

if __name__ == "__main__":
    rc = asyncio.run(asy_ntp_time())
    print("asy_ntp_time returns: ", rc)
