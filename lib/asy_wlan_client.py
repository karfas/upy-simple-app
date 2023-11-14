# asy_wlan.py
#
# 2022-10-14 TW created
#
import uasyncio as asyncio
import network
import ubinascii

class WLANClient:
    def __init__(self, conf, *args, **kwargs):
        """
        Wrapper for network.WLAN. 
        Provides access to WLAN parameters from a config file and 
        some async functions.
        """
        self._wlan = network.WLAN(network.STA_IF, *args, **kwargs)
        self._conf = conf
        if isinstance(conf, str):
            self._conf = __import__(conf)
        self._wlan.active(False)

    def __getattr__(self, attr):
        def wrapped_method(*args, **kwargs):
#            print("The method {} is executing.".format(attr))
            result = getattr(self._wlan, attr)(*args, **kwargs)
#            print("The result was {}.".format(result))
            return result    
        return wrapped_method

    def status_as_text(self):
        text = {
            network.STAT_IDLE: "idle",
            network.STAT_CONNECTING: "connecting",
            network.STAT_GOT_IP: "got_ip",
            network.STAT_NO_AP_FOUND: "no AP found",
            network.STAT_WRONG_PASSWORD: "wrong password",
            network.STAT_BEACON_TIMEOUT: "beacon timeout",
            network.STAT_ASSOC_FAIL: "assoc fail",
            network.STAT_HANDSHAKE_TIMEOUT: "handshake timeout",
            2: "WIFI_REASON_AUTH_EXPIRE",
            15: "4WAY_HANDSHAKE_TIMEOUT",
            205: "WIFI_REASON_CONNECTION_FAIL",
            }
        st = self._wlan.status();
        if st in text:
            return text[st]
        return "unknown({})".format(st)

    def connect(self, *args, **kwargs) -> None:
        wlan = self._wlan

        wlan.active(True)
        nw_tuple = ()
        for kw in ['NET_ADDRESS', 'NET_MASK', 'NET_GATEWAY', 'NET_NAMESERVER' ]:
            v = getattr(self._conf, kw, None)
            if v is None:
                break 
            nw_tuple = nw_tuple + (v,)
        if nw_tuple:
            wlan.ifconfig(nw_tuple)

        wlan.config(reconnects=getattr(self._conf, 'WIFI_RECONNECTS', 1))

        if dhcp_name := getattr(self._conf, 'WIFI_DHCP_NAME_PREFIX', None):
            mac_bin = wlan.config('mac')
            mac_hex = ubinascii.hexlify(mac_bin[4:]).decode()
            dhcp_name += mac_hex
            wlan.config(dhcp_hostname=dhcp_name)

        ap = getattr(self._conf, 'WIFI_SSID')
        passw = getattr(self._conf, 'WIFI_PASSWORD')
        self._wlan.connect(ap, passw)

    async def asy_connect(self, *args, **kwargs):
        """Connect and wait until connected. """
        self.connect(*args, **kwargs)
        return await self.asy_wait_connect();

    async def asy_wait_connect(self):
        """Wait until connected. """
        wlan = self._wlan
        st = None
        while True:
            st_new = wlan.status()
            if st_new != st:
                print("wlan status: {}".format(self.status_as_text()))
                st = st_new
            if st == network.STAT_CONNECTING:
                await asyncio.sleep(0)
            else:
                break

        r = wlan.isconnected()
        if r:
            print("WLAN: connected, ifconfig={}".format(wlan.ifconfig()))
        return r

"""
Example from uPy docs:
wlan = network.WLAN(network.STA_IF) # create station interface
wlan.active(True)       # activate the interface
wlan.scan()             # scan for access points
wlan.isconnected()      # check if the station is connected to an AP
wlan.connect('ssid', 'key') # connect to an AP
wlan.config('mac')      # get the interface's MAC address
wlan.ifconfig()         # get the interface's IP/netmask/gw/DNS addresses
"""

