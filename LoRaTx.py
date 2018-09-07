#! /usr/bin/python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# LoRaTx.py
# Send data between LoRa devices without Gateway
# Sending data script
# Python 3+
# RN2483 documentation: http://ww1.microchip.com/downloads/en/DeviceDoc/40001784F.pdf
# Jorge Mendes, Raul Morais, Nuno Silva, 09/2018
# --------------------------------------------------------------------------

import serial
from time import sleep
from LoRaBase import LoRaBase
import binascii

tx_usb_port = '/dev/ttyUSB0'
eui_node_address_to_send = b'XXXXXXXXXXXXXXXX'
msg_to_send = b'LoRa P2P messaging test'

# ---------------------------------------------------------- 
# LoRaTx class
# ---------------------------------------------------------- 
class LoRaTx(LoRaBase):
    def __init__(self, port=None):
        super().__init__(port)

    # ---------------------------------------------------------- 
    # Transmit function
    # ---------------------------------------------------------- 
    def transmit(self,data=None):
        assert data is not None, "\t[ERROR] Can not send None to other side!"
        print('\nTRANSMISSION...')
        print('\t[INFO] Send data to', eui_node_address_to_send.decode())
        i = 0
        msglen = len(data)
        tx_allow = True
        while True:
            if self._ptx.readable():
                r = self._ptx.readline()
                if len(r):
                    print('\t<< tx {r}'.format(r=r[:-2]))
                    s = r.decode()
                    if s.startswith('radio_tx_ok'):
                        print('\t\t[INFO] Module confirmed Tx by radio')
                        # Tx is done, we can send more data now
                        tx_allow = True
                    elif s.startswith('ok'):
                        print('\t\t[INFO] Module accepted Tx command')
                    else:
                        print("\t\t[ERROR] Module reponse unexpected\n")
                        break

            if tx_allow:
                # Write something in TX
                if i < msglen:
                    #c = hex(data[i])[2:]  # strip 0x        # Send byte to byte
                    c = binascii.hexlify(data).decode()
                    m = 'radio tx {xx}'.format(xx=c)
                    print('\t>> {m}'.format(m=m))
                    self._ptx.write(m.encode())
                    self._ptx.write(b'\r\n')
                    #i += 1                                  # Send byte to byte
                    i = msglen
                    tx_allow = False
                else:
                    print('')
                    break


# ###################################################### #
# ################### MAIN FUNCTION #################### #
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
    data = eui_node_address_to_send + b' ' + msg_to_send

    # Transmit data
    tx.transmit(data)

