#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# LoRaBase.py
# Send data between LoRa devices without Gateway
# Python 3+
# RN2483 documentation: http://ww1.microchip.com/downloads/en/DeviceDoc/40001784F.pdf
# Jorge Mendes, Raul Morais, Nuno Silva, 09/2018
# --------------------------------------------------------------------------

import serial
from time import sleep
import os

# ---------------------------------------------------------- 
# LoRaBase class
# ---------------------------------------------------------- 
class LoRaBase(object):
    # Some baseclass for RX an TX objects
    _cmd_no_mac = [
        'sys get ver',
        'sys get hweui',
        'radio set mod lora',
        'radio set freq 868000000',
        'radio set pwr 14',
        'radio set sf sf12',
        'radio set afcbw 125',
        'radio set rxbw 250',
        'radio set fdev 5000',
        'radio set prlen 8',
        'radio set crc on',
        'radio set cr 4/8',
        'radio set wdt 0',
        'radio set sync 12',
        'radio set bw 250',
        'mac pause'
    ]

    def connect_module(self, s=None):
        # Connect module (on serial port s)
        # Return version number or None on fail
        assert (s is not None)

        rv = None
        cnt = 5

        while cnt:
            s.send_break(duration=0.25)   # Send break, pull TX low
            s.write(b'U')                 # Send 0x55 for autobaud
            sleep(0.1)
            s.write(b'sys get ver\r\n')
            r = s.readline()
            # print(r)
            if len(r) and r.startswith(b'RN2483'):
                rv = r
                break
            cnt -= 1
        return rv

    def __init__(self, port=None):
        self._firmware = None
        assert port is not None, "\t[ERROR] Port must be given, name of serial device"

        try:
            self._ptx = serial.Serial(port=port, baudrate=57600, timeout=2.0, write_timeout=2.0)
        except serial.SerialException as sex:
            raise IOError(sex)

        m = self.connect_module(self._ptx)  # Connect and sync with module
        if m:
            os.system('clear')
            print('\nMODULE CONNECTION...')
            self._firmware = m
            print("\t<< {m}".format(m=m))
            print('\t\t[INFO] Success')
        else:
            raise IOError('\t[ERROR] Module not talking to me!')

        print('\nMODULE CONFIGURATION...')

        for m in self._cmd_no_mac:
                print('\t>> {m}'.format(m=m))
                self._ptx.write(m.encode())
                self._ptx.write(b'\r\n')
                r = self._ptx.readline()
                if len(r):
                    print('\t<< {r}'.format(r=r[:-2]))
                else:
                    print('\t<< no response')

    @property
    def serialport(self):
        # Exposing the port
        return self._ptx

    @property
    def firmware(self):
        return self._firmware

    def setup(self):
        raise ("Must me implemented in subclass")
