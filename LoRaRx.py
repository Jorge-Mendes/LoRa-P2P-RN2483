#! /usr/bin/python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# LoRa_Rx.py
# Send data between LoRa devices without Gateway
# Description: Receiving data script
# Python version: Python 3+
# RN2483 documentation: http://ww1.microchip.com/downloads/en/DeviceDoc/40001784F.pdf
# Author: Jorge Mendes
# Contributors: Raul Morais, Nuno Silva
# Date: 09/2018
# --------------------------------------------------------------------------

import serial
from time import sleep
from LoRaMain import LoRaMain
import binascii
import datetime
import textwrap

rx_usb_port = '/dev/ttyUSB1'
my_eui_node_address = '0004A30B001E7EB7'

# ---------------------------------------------------------- 
# Log function
# ---------------------------------------------------------- 
def log(log_msg):
    if LoRaMain.LoRaDebug:
        print(log_msg)

# ---------------------------------------------------------- 
# LoRaRx class
# ---------------------------------------------------------- 
class LoRaRx(LoRaMain):
    def __init__(self, port=None):
        super().__init__(port)

    # ---------------------------------------------------------- 
    # Receive function
    # ---------------------------------------------------------- 
    def receive(self):
        print('\nRECEPTION...')
        # Tell the radio to get more data
        self._ptx.write(b'radio rx 0\r\n')
        print('\t>> radio rx 0')
        gmdr = self._ptx.readline().decode()
        log('\t\t[INFO] Enable the Continuous Reception mode')
        print('\t<< {s}'.format(s=gmdr[:-2]))
        if gmdr.startswith('ok'):
            log('\t\t[INFO] Continuous Reception mode enabled')
        if gmdr.startswith('busy'):
            log('\t\t[INFO] Continuous Reception mode was already enabled')

        while True:
            # Wait until we RX anything
            if self._ptx.readable():
                r = self._ptx.readline()

                if len(r):
                    # print('<< prx {r}'.format(r=r[:-2]))
                    s = r.decode()
                    if s.startswith('radio_rx'):
                        if len(s) < 75:
                            print('\t<< {s}'.format(s=s[:-2]))
                        else:
                            print('\t<< {s}...'.format(s=s[:75]))
                        #print('\t\t[INFO] Message received at', datetime.datetime.utcnow())
                        # We got some data
                        l = len(s)
                        h = s[10:][:-2]                                 # To discard "radio_rx"
                        st = binascii.unhexlify(h.encode()).decode()    # Otherwise: bytearray.fromhex("6A6F726765").decode()
                        st_from_eui_node_address, st_to_eui_node_address, st_message = st.split(';')
                        #print("aaa:", st_from_eui_node_address)
                        #print("bbb:", st_to_eui_node_address)
                        #print("ccc:", st_message)
                        log('\t\t[INFO] Received message from "' + str(st_from_eui_node_address) + '" to "' + str(st_to_eui_node_address) + '"')
                        if st_to_eui_node_address == my_eui_node_address:
                            log('\t\t[INFO] The message is for me!')
                            log('\t\t[INFO] Received message content:')
                            log(textwrap.fill(st_message, initial_indent='\t\t       ', subsequent_indent='\t\t       ',width=75,break_long_words=True,replace_whitespace=False))
                            #print('\t\t      ', st_message)
                        else:
                            log('\t\t[INFO] The message is not for me!')
                        break

                    elif s.startswith('busy'):
                        log('\t[WARNING] Unexpected, the receiver is still busy')
                    elif s.startswith('invalid_param'):
                        log('\t[WARNING] Unexpected protocol param error')
                    elif s.startswith('ok'):
                        pass
                        #print('All good')
                    else:
                        log('\t[WARNING] Really unexpected stuff')


# ###################################################### #
# ######################## MAIN ######################## #
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

