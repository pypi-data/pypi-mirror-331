#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ChipShouterInterface

Used to control the ChipSHOUTER and the CNC 3018 PRO.

Use at your own risk and do not use without full consent of everyone involved.
"""

from time import sleep
from chipshouter import ChipSHOUTER
from chipshouter.com_tools import Reset_Exception
from findus import Glitcher

class ChipShouterInterface(Glitcher):
    """ChipShouterInterface class"""

    def __init__(self, port_chipshouter, external_trigger:bool = False):
        print("[+] Initializing ChipSHOUTER")
        self._port_chipshouter = port_chipshouter
        self._chipshouter = ChipSHOUTER(self._port_chipshouter)
        # ChipSHOUTER config backup for restore function
        self._voltage = None
        self._pulse_repeat = None
        self._pulse_width = None
        self._pulse_deadtime = None
        self._pat_enable = 0
        self._pat_wave = ''
        self._mute = None
        if external_trigger:
            self._chipshouter.hwtrig_mode = 0
            self._chipshouter.hwtrig_term = 0

    def __del__(self):
        print('[+] Disarming ChipSHOUTER')
        try:
            self._chipshouter.armed = 0
        except:
            pass

    def init(self, voltage=200, pulse_repeat=1, pulse_width=120, pulse_deadtime=15, pat_wave='',
                     mute=False, restore=False):
        """Sets default settings and arms the ChipSHOUTER"""
        # Save initial values for a possible restore
        if not restore:
            self._voltage = voltage
            self._pulse_repeat = pulse_repeat
            self._pulse_width = pulse_width
            self._pulse_deadtime = pulse_deadtime
            if pat_wave:
                self._pat_enable = 1
                self._pat_wave = pat_wave
            self._mute = mute
        # Restore saved values
        self._chipshouter.voltage = self._voltage
        self._chipshouter.pulse.repeat = self._pulse_repeat
        self._chipshouter.pulse.width = self._pulse_width
        self._chipshouter.pulse.deadtime = self._pulse_deadtime
        if self._pat_enable:
            self._chipshouter.pat_enable = self._pat_enable
            self._chipshouter.pat_wave = self._pat_wave
        if not self._chipshouter.armed:
            try:
                self._chipshouter.mute = self._mute
                self._chipshouter.armed = 1
                # clear faults and arm
                #self._chipshouter.clr_armed = 1
                print('[+] Armed')
                sleep(1)
            except:
                pass

    def clear_faults(self):
        for fault in self._chipshouter.faults_current:
            if fault == 'fault_high_voltage':
                print('[+] Try reducing voltage steps between consecutive experiments.')
            print(f"[+] Attempting to clear ChipSHOUTER fault: {fault}")
        for fault in self._chipshouter.faults_latched:
            print(f"[+] Attempting to clear ChipSHOUTER latched fault: {fault}")
        self._chipshouter.faults_current = 0

    def block(self):
        # check if shouter is available or if there are faults
        while self._chipshouter.faults_current != []:
            print(f"[+] ChipSHOUTER status: {self._chipshouter.state}")
            self.clear_faults()
            sleep(5)
            self.init(restore=True)

    def shout(self):
        """ChipSHOUTER executes the configured pulse
        """
        _voltage_measured = 0
        _pulse_width_measured = 0
        try:
            self._chipshouter.pulse = 1
            _voltage_measured = self._chipshouter.voltage.measured
            print(f'[+] Voltage set: {self._chipshouter.voltage.set} '
                  f'measured: {_voltage_measured}')
            _pulse_width_measured = self._chipshouter.pulse.measured
            print(f'[+] Pulse width set: {self._chipshouter.pulse.width} '
                  f'measured: {_pulse_width_measured}')
        except Reset_Exception:
            print("[+] ChipSHOUTER reboot")
            sleep(5)
            self.init(restore=True)

if __name__ == '__main__':
    print('[+] ChipShouterInterface')
