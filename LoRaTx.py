#! /usr/bin/python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# LoRaTx.py
# Send data between LoRa devices without Gateway
# Description: Sending data script
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
import textwrap


tx_usb_port = '/dev/ttyUSB0'
my_eui_node_address = b'0004A30B001C2622'
send_eui_node_address = b'0004A30B001E7EB7'
#msg_to_send = b'LoRa P2P messaging test!'
msg_to_send = b'{"formatver":"2.0","dataarray":[{"ts":"2017-05-18 13:37:00","tsarray":[{"ch":"1","value":"1302.0"},{"ch":"2","value":"22.0"}]},{"ts":"2017-05-18 13:39:00","tsarray":[{"ch":"2","value":"0.0"}]}]}'

# ---------------------------------------------------------- 
# Log function
# ---------------------------------------------------------- 
def log(log_msg):
    if LoRaMain.LoRaDebug:
        print(log_msg)

# ---------------------------------------------------------- 
# LoRaTx class
# ---------------------------------------------------------- 
class LoRaTx(LoRaMain):
    def __init__(self, port=None):
        super().__init__(port)

    # ---------------------------------------------------------- 
    # Transmit function
    # ---------------------------------------------------------- 
    def transmit(self,data=None):
        assert data is not None, "\t[ERROR] Can not send None to other side!"
        print('\nTRANSMISSION...')
        i = 0
        msglen = len(data)
        tx_allow = True
        while True:
            if self._ptx.readable():
                r = self._ptx.readline()
                if len(r):
                    print('\t<< {r}'.format(r=r[:-2].decode()))
                    s = r.decode()
                    if s.startswith('radio_tx_ok'):
                        log('\t\t[INFO] Module confirmed Tx by radio')
                        # Tx is done, we can send more data now
                        tx_allow = True
                    elif s.startswith('ok'):
                        log('\t\t[INFO] Module accepted Tx command')
                    else:
                        log('\t\t[ERROR] Module reponse unexpected')
                        log('\t\t        The data size probably exceeded 255 bytes\n')
                        break

            if tx_allow:
                # Write something in TX
                if i < msglen:
                    #c = hex(data[i])[2:]  # strip 0x        # Send byte to byte
                    c = binascii.hexlify(data).decode()
                    m = 'radio tx {xx}'.format(xx=c)
                    if len(m) < 75:
                        print('\t>> {m}'.format(m=m))
                    else:
                        print('\t>> {m}...'.format(m=m[:75]))
                    msg = '[INFO] Send message "' + str(msg_to_send.decode()) + '" from "' + str(my_eui_node_address.decode()) + '" to "' + str(send_eui_node_address.decode()) + '"'
                    log(textwrap.fill(msg, initial_indent='\t\t', subsequent_indent='\t\t       ',width=75,break_long_words=True,replace_whitespace=False))
                    self._ptx.write(m.encode())
                    self._ptx.write(b'\r\n')
                    #i += 1                                  # Send byte to byte
                    i = msglen
                    tx_allow = False
                else:
                    print('')
                    break


# ###################################################### #
# ######################## MAIN ######################## #
# ###################################################### #

if __name__ == '__main__':

    try:
        tx = LoRaTx(port=tx_usb_port)
    except IOError as ioex:
        # Problem
        print('[ERROR] Could not connect to module!')
        exit(1)
    #else:
    #    print('Module connected : {x}'.format(x=tx.firmware))

    # Data format <ID_DO_LORA> <MSG>
    data = my_eui_node_address + b';' + send_eui_node_address + b';' + msg_to_send

    # Transmit data
    tx.transmit(data)

