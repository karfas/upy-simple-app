# 
# start_wlan.py
#
# utility script to connect to WLAN.
#
import uasyncio as asyncio
from lib.asy_wlan_client import WLANClient as WLAN

wlan = WLAN("settings")
asyncio.run(wlan.asy_connect())


