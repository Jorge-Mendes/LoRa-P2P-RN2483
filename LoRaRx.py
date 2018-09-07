#! /usr/bin/python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# LoRa_Rx.py
# Send data between LoRa devices without Gateway
# Receiving data script
# Python 3+
# RN2483 documentation: http://ww1.microchip.com/downloads/en/DeviceDoc/40001784F.pdf
# Jorge Mendes, Raul Morais, Nuno Silva, 09/2018
# --------------------------------------------------------------------------

import serial
from time import sleep
from LoRaBase import LoRaBase
import binascii
import datetime

rx_usb_port = '/dev/ttyUSB1'
my_eui_node_address = 'XXXXXXXXXXXXXXXX'

# ---------------------------------------------------------- 
# LoRaRx class
# ---------------------------------------------------------- 
class LoRaRx(LoRaBase):
    def __init__(self, port=None):
        super().__init__(port)

    # ---------------------------------------------------------- 
    # Receive function
    # ---------------------------------------------------------- 
    def receive(self):
        print('\nRECEPTION...')
        # Tell the radio to get more data
        self._ptx.write(b'radio rx 0\r\n')

        while True:
            # Wait until we RX anything
            if self._ptx.readable():
                r = self._ptx.readline()

                if len(r):
                    # print('<< prx {r}'.format(r=r[:-2]))
                    s = r.decode()
                    if s.startswith('radio_rx'):
                        print('\t[INFO] Message received at', datetime.datetime.utcnow())
                        # We got some data
                        l = len(s)
                        h = s[10:][:-2]     # To discard "radio_rx"
                        st = binascii.unhexlify(h.encode()).decode()    # Otherwise: bytearray.fromhex("6A6F726765").decode()
                        if st.startswith(my_eui_node_address):
                            print('\t[INFO] The message is for me!')
                            print('\t\t<<', st[17:])
                        else:
                            print('\t[INFO] The message is not for me!')
                        break

                    elif s.startswith('busy'):
                        print('\t[WARNING] Unexpected, the receiver is still busy')
                    elif s.startswith('invalid_param'):
                        print('\t[WARNING] Unexpected protocol param error')
                    elif s.startswith('ok'):
                        pass
                        #print('All good')
                    else:
                        print('\t[WARNING] Really unexpected stuff')


# ###################################################### #
# ################### MAIN FUNCTION #################### #
# ###################################################### #

if __name__ == '__main__':

    try:
        rx = LoRaRx(port=rx_usb_port)
    except IOError as ioex:
        # Problem
        print('[ERROR] Could not connect to module!')
        exit(1)
    #else:
    #    print('Module connected : {x}'.format(x=rx.firmware))

    # Receive data until hell freezes over
    while True:
        rx.receive()

