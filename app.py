#
# app/app.py
#
# from config import config           # for MQTT
import uasyncio as asyncio
import machine
import time

from lib.asy_wlan_client import WLANClient
from lib.asy_ntp_time import asy_ntp_time

import settings

########
# globals

class NTPClient():
    def __init__(self, servername:str):
        self._server = servername

    async def set_rtc_time(self, *args, **kwargs):
        print("start set_rtc_time")
        self._have_time = False
        return self.have_time()

    def have_time(self):
        return self._have_time

async def measure():
    return 123;

class Task:
    def __init__(self, coro, when = None):
        if when:
            async def wrap():
                """
                wrap() starts the task if when() returns true.
                In this case, the handle gets replaced by the real task.
                """
                while not (c := when()):
                    # print("when() returns {}".format(c))
                    await asyncio.sleep(0)
                print("wrap(): {} returns {}".format(when, c))
                print("wrap(): starts coro ", coro)
                return await coro

            self.handle = asyncio.create_task(wrap())
        else:
            self.handle = asyncio.create_task(coro)

def create_task(coro, when = None):
    if when:
        async def wrap():
            """
            wrap() starts the task if when() returns true.
            In this case, the handle gets replaced by the real task.
            """
            while not (c := when()):
                # print("when() returns {}".format(c))
                await asyncio.sleep(0)
            # print("wrap(): {} returns {}".format(when, c))
            # print("wrap(): starts coro ", coro)
            return await coro

        return asyncio.create_task(wrap())
    else:
        return asyncio.create_task(coro)


class App:
    def __init__(self, config):
        self.have_time = time.gmtime(time.time())[0] >= 2022
        self.wlan = WLANClient(config)
        self.config = config

    async def run(self):

        async def asy_dummy():
            return None

        require_network = not self.have_time
        connect_tsk = asy_dummy()
        ntp_tsk = asy_dummy()
        measure_task = None

        if require_network:
            connect_tsk = create_task(self.wlan.asy_connect())
            if server := getattr(self.config, 'NTP_SERVER', None):
                ntp_tsk = create_task(asy_ntp_time(), when=self.wlan.isconnected)
        measure_tsk = create_task(measure())

        g = await asyncio.gather(connect_tsk, ntp_tsk, measure_tsk)

        ntp_time = g[1]
        print(ntp_time)

        if require_network:
            self.wlan.active(0)

config_file = "settings"

def run(once=True):
    """Start the application"""
    asyncio.run(App(settings).run())
    if once:
        print("goto sleep")
        machine.deepsleep(5000)

# print("__name__={}".format(__name__) )

