"""
rtcmpoller.py

This example illustrates a simple implementation of a
'pseudo-concurrent' threaded RTCMMessage streaming utility.

(NB: Since Python implements a Global Interpreter Lock (GIL),
threads are not truly concurrent.)

It connects to the receiver's serial port and sets up a
RTCMReader read thread.

Created on 14 Feb 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from sys import platform
from io import BufferedReader
from threading import Thread, Lock
from time import sleep
from serial import Serial
from pyrtcm import (
    RTCMReader,
)

# initialise global variables
reading = False


def read_messages(stream, lock, rtcmreader):
    """
    Reads, parses and prints out incoming rtcm messages
    """
    # pylint: disable=unused-variable, broad-except

    while reading:
        if stream.in_waiting:
            try:
                lock.acquire()
                (raw_data, parsed_data) = rtcmreader.read()
                lock.release()
                if parsed_data:
                    print(parsed_data)
            except Exception as err:
                print(f"\n\nSomething went wrong {err}\n\n")
                continue


def start_thread(stream, lock, rtcmreader):
    """
    Start read thread
    """

    thr = Thread(target=read_messages, args=(stream, lock, rtcmreader), daemon=True)
    thr.start()
    return thr


def send_message(stream, lock, message):
    """
    Send message to device
    """

    lock.acquire()
    stream.write(message.serialize())
    lock.release()


if __name__ == "__main__":

    # set port, baudrate and timeout to suit your device configuration
    if platform == "win32":  # Windows
        port = "COM13"
    elif platform == "darwin":  # MacOS
        port = "/dev/tty.usbmodem14101"
    else:  # Linux
        port = "/dev/ttyACM1"
    baudrate = 9600
    timeout = 0.1

    with Serial(port, baudrate, timeout=timeout) as ser:

        # create rtcmReader instance, reading only rtcm messages
        rtr = RTCMReader(BufferedReader(ser))

        print("\nStarting read thread...\n")
        reading = True
        serial_lock = Lock()
        read_thread = start_thread(ser, serial_lock, rtr)

        print("\nPolling complete. Pausing for any final responses...\n")
        sleep(1)
        print("\nStopping reader thread...\n")
        reading = False
        read_thread.join()
        print("\nProcessing Complete")
