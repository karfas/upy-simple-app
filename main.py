#
# main.py
#
# for low-power/battery-powered app
#
# calls app.run() with appropriate power mode.
#
# IN THE MOMENT, app.run() is responsible for calling machine.deepsleep()
#

import machine
import time

def main():
    run = True
    cause = machine.reset_cause()
    if cause == machine.SOFT_RESET:
        print("main() BOOT: soft reset")
        run = False
        # do nothing, drop to REPL
    elif cause == machine.DEEPSLEEP_RESET:
        print("main() BOOT: deep sleep reset")
    elif cause == machine.PWRON_RESET:
        print("main() BOOT: PWRON_RESET") # e.g. machine.PWRON_RESET
        time.sleep(10)
    elif cause == machine.WDT_RESET:
        print("main() BOOT: WDT_RESET")
    else:
        pass

    if run:
        import app
        app.run()

    print("main(): drop to repl")

if __name__ == "__main__":
    main()
