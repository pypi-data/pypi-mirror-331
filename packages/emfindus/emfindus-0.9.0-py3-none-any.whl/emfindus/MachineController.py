#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MachineController

Used to control the 3018 PRO (3 Axis) via GRBL.

Use at your own risk and do not use without full consent of everyone involved.
"""

import serial
from time import sleep
from pynput import keyboard
import re
import json
from collections import namedtuple
from itertools import product
from more_itertools import numeric_range
from random import choices

class MachineController:
    """MachineController class"""

    # https://github.com/gnea/grbl/wiki/Grbl-v1.1-Jogging
    _JOG_CMD = b'$J='
    _HOMING_CMD = b'$H\n'
    _UNITS_MM_CMD = b'G21'
    _ABS_POS_CMD = b'G90'
    _REL_POS_CMD = b'G91'
    _SET_POS_CMD = b'G92'
    _UNLOCK_CMD = b'$X'
    _SET_COORD_SYS_CMD = b'G10P0L20'
    _GO_TO_ZERO_XY = b'G90G0X0Y0\n'
    _GO_TO_ZERO_Z = b'G90G0Z0\n'
    _JOG_ABS_MM_CMD = _JOG_CMD + _UNITS_MM_CMD + _ABS_POS_CMD
    _JOG_REL_MM_CMD = _JOG_CMD + _UNITS_MM_CMD + _REL_POS_CMD

    # config file
    _CONFIG_FILE = "configuration.json"

    def __init__(self, port, baudrate=115200, limits=False, max_x=0, max_y=0, max_z=0):
        self._port = port
        self._baudrate = baudrate
        self._timeout = 3
        self._serial_iface = None
        self._safety_distance = 3
        self._limits = limits
        self._max_x = max_x
        self._max_y = max_y
        self._max_z = max_z
        self._poll = 0.2

    def _check_command_success(self):
        """Checks if the command failed"""
        # Command is confirmed with 'ok' or 'error:'
        return b'ok' in self._serial_iface.read_until(b"ok\r\n")

    def _wait_for_idle(self):
        """Waits until the 3018 returns Idle as status"""
        if self._serial_iface is not None:
            while True:
                self._serial_iface.write(b'?')
                data = self._serial_iface.readline()
                if b'<Idle' in data:
                    break
                sleep(self._poll)
        else:
            print('[!] Error serial connection is not available')
        return False

    def get_machine_position(self):
        if self._serial_iface is not None:
            while True:
                self._serial_iface.write(b'?')
                data = self._serial_iface.readline()
                if b'MPos' in data:
                    match = re.search(r"MPos:([-.\d]+),([-.\d]+),([-.\d]+)", data.decode('utf-8'))
                    mpos_values = list(map(float, match.groups()))
                    return mpos_values
        else:
            print('[!] Error serial connection is not available')
        return []

    def get_relative_machine_position(self):
        config = None
        with open(self._CONFIG_FILE, "r") as file:
            config = json.load(file)
            x_offset = config["machine_offsets"][0]
            y_offset = config["machine_offsets"][1]
            z_offset = config["machine_offsets"][2]
            if self.get_machine_position() != []:
                position = [a - b for a, b in zip(self.get_machine_position(), [x_offset, y_offset, z_offset])]
                return position
        return []

    def _send_cmd(self, cmd):
        if self._serial_iface is not None:
            cmd = cmd + b'\r\n'
            self._serial_iface.write(cmd)
            return self._check_command_success()
        else:
            print('[!] Error serial connection is not available')
        return False

    def _check_limits(self, x, y, z, relative):
        """Verify if the x, y, z values are within the defined limits (limits included)"""
        if not self._limits:
            return True
        if self._serial_iface is not None:
            while True:
                self._serial_iface.write(b'?')
                data = self._serial_iface.readline()
                if b'<Idle|MPos:' in data:
                    cx, cy, cz = data.split(b'|')[1].replace(b'MPos:', b'').split(b',')
                    _x = float(cx) + x if relative else x
                    _y = float(cy) + y if relative else y
                    _z = float(cz) + z if relative else z
                    if 0 <= _x <= self._max_x and 0 <= _y <= self._max_y and 0 <= _z <= self._max_z:
                        return True
                    else:
                        print('[!] Error limits were violated')
                        break
                else:
                    # In case of a timeout or Jog
                    print('[!] Error in locating the current position or final position not yet reached. Try again.')
                sleep(self._poll)
        else:
            print('[!] Error serial connection is not available')
        return False

    def connect(self):
        """Establishes a serial connection and waits for the prompt"""
        prompt = b"Grbl 1.1f ['$' for help]\x0D\x0A"
        print('[+] Initializing CNC table')
        self._serial_iface = serial.Serial(port=self._port, baudrate=self._baudrate, timeout=self._timeout)
        data = self._serial_iface.read_until(prompt)
        if prompt not in data:
            # In case of a timeout
            print('[!] Error during initialization')
        print(f'[+] Prompt received:{data}')

    def homing(self):
        """Homing the machine by using the limit switches"""

        if self._serial_iface is not None:
            self._serial_iface.write(self._HOMING_CMD)
            while b'ok' not in self._serial_iface.readline():
                sleep(0.1)
        else:
            print('[!] Error serial connection is not available')

    def zeroing(self):
        """Offsets the origin of the axes in the coordinate system to 0. No physical motion will occur"""
        if self._serial_iface is not None:
            data = self._serial_iface.read_until(b"\r\n")
            if b'\'$X\' to unlock' in data:
                if input('[!] Machine is locked. Do you want to unlock the machine (be cautious)? (y/n): ').lower() in ['y', 'yes']:
                    self._send_cmd(MachineController._UNLOCK_CMD)
            self._send_cmd(MachineController._SET_COORD_SYS_CMD + b'X0Y0Z0\n')
            self._send_cmd(MachineController._SET_POS_CMD + b'X0Y0Z0\n')
        else:
            print('[!] Error serial connection is not available')

    def setup_position(self, homing=True, manual_positioning=False, go_to_last_working_position=False):
        """
        homing: Move Table to the home position. The machine offsets are stored in configuration.json.
        manual_positioning: Do not home the table and go from the last position.
        homing + manual_positioning: Move Table to the home position and position the table manually afterwards. The last zero position relative to home is stored into configuration.json.
        homing + go_to_last_working_position: Move Table to the home position and go to the last stored zero position.
        manual_positioning without homing does nothing.
        go_to_last_working_position without homing does nothing.
        If homing = False, manual_positioning = False and go_to_last_working_position = False, the machine starts from the last working position.
        """
        if homing:
            self.homing()
            self.store_machine_offsets()
        self.zeroing()
        if manual_positioning:
            self.manual_pos()
        # we can only store the last zero position, if we know the absolute machine position (homing performed)
        if homing and manual_positioning:
            self.store_last_position()
        self.zeroing()
        # we can only go to the last zero position if we know the absolute machine position (homing performed)
        if homing and go_to_last_working_position:
            self.go_to_last_position()
        self.working_pos()
        sleep(1)

    def working_pos(self):
        """Moves to the set zero point of the target"""
        current_z = self.get_machine_position()[2]
        print(f"current z position: {current_z}")
        if self._serial_iface is not None:
            if current_z < 0:
                self._send_cmd(MachineController._GO_TO_ZERO_Z)
            self._send_cmd(MachineController._GO_TO_ZERO_XY)
            if current_z > 0:
                self._send_cmd(MachineController._GO_TO_ZERO_Z)
            self._wait_for_idle()
        else:
            print('[!] Error serial connection is not available')

    def manual_pos(self):
        """Provides manual positioning"""
        x = y = z = 0
        dx = dy = dz = 0
        while True:
            try:
                x = float(input('[+] Approximate relative position for x [mm]? (e.g. 1.2, positive is to the right): '))
                y = float(input('[+] Approximate relative position for y [mm]? (e.g. 3.4, positive is to back): '))
                break
            except ValueError:
                pass
        self.move_rel_xy(x, y, f=500)
        while True:
            try:
                z = float(input('[+] Approximate relative position for z [mm]? (e.g. -1.2, down is negative): '))
                break
            except ValueError:
                pass
        self.move_rel_z(z, f=500)
        print('[+] Now perform the exact positioning.')
        print('[+] Use keys (w, a, s, d) for x and y axis (backwards, left, forward, right).')
        print('[+] Use keys (e, f) for z axis (up and down).')
        print('[+] Cancel with n. ')
        def on_press(key):
            nonlocal dx, dy, dz
            try:
                if key.char == 'f':
                    dz += -0.1
                elif key.char == 'e':
                    dz += 0.1
                elif key.char == 's':
                    dy += -0.1
                elif key.char == 'a':
                    dx += -0.1
                elif key.char == 'w':
                    dy += 0.1
                elif key.char == 'd':
                    dx += 0.1
                elif key.char == 'n':
                    return False
            except AttributeError:
                pass
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        try:
            while listener.running:
                update = False
                if dx != 0:
                    self.move_rel_x(dx, f=100)
                    dx = 0
                    update = True
                if dy != 0:
                    self.move_rel_y(dy, f=100)
                    dy = 0
                    update = True
                if dz != 0:
                    self.move_rel_z(dz, f=100)
                    dz = 0
                    update = True
                if update:
                    print(f"[+] Current relative machine position: {self.get_relative_machine_position()}")
                sleep(0.1)
        except Exception as e:
            print(e)

    def store_machine_offsets(self):
        config = None
        with open(self._CONFIG_FILE, "r") as file:
            config = json.load(file)
            if self.get_machine_position() != []:
                position = self.get_machine_position()
                print(f"[+] Current machine position: {position}")
                config["machine_offsets"] = position
        if config is not None:      
            with open(self._CONFIG_FILE, "w") as file:
                json.dump(config, file)

    def store_last_position(self):
        config = None    
        with open(self._CONFIG_FILE, "r") as file:
            config = json.load(file)
            if self.get_relative_machine_position() != []:
                position = self.get_relative_machine_position()
                print(f"[+] Current relative machine position: {position}")
                config["last_position"] = position
        if config is not None:
            with open(self._CONFIG_FILE, "w") as file:
                json.dump(config, file)

    def go_to_last_position(self):
        with open(self._CONFIG_FILE, "r") as file:
            config = json.load(file)
            x = config["last_position"][0]
            y = config["last_position"][1]
            z = config["last_position"][2]
            self.move_rel_xy(x, y, f=500)
            self.move_rel_z(z, f=500)
            self.zeroing()

    def move_abs_x(self, x, f=100, safety_mode=False):
        """Absolute (from the defined zero point) movement (in mm) of the X axis"""
        self.move(x, 0, 0, f, safety_mode, relative=False)

    def move_abs_y(self, y, f=100, safety_mode=False):
        """Absolute (from the defined zero point) movement (in mm) of the Y axis"""
        self.move(0, y, 0, f, safety_mode, relative=False)

    def move_abs_z(self, z, f=100, safety_mode=False):
        """Absolute (from the defined zero point) movement (in mm) of the Z axis"""
        self.move(0, 0, z, f, safety_mode, relative=False)

    def move_abs_xy(self, x, y, f=100, safety_mode=False):
        """Absolute (from the defined zero point) movement (in mm) of the X and Y axis"""
        self.move(x, y, 0, f, safety_mode, relative=False)

    def move_abs_xyz(self, x, y, z, f=100, safety_mode=False):
        """Absolute (from the defined zero point) movement (in mm) of the X, Y and Z axis"""
        self.move(x, y, z, f, safety_mode, relative=False)

    def move_rel_x(self, x, f=100, safety_mode=False):
        """Relative movement (in mm) of the X axis"""
        self.move(x, 0, 0, f, safety_mode, relative=True)

    def move_rel_y(self, y, f=100, safety_mode=False):
        """Relative movement (in mm) of the Y axis"""
        self.move(0, y, 0, f, safety_mode, relative=True)

    def move_rel_z(self, z, f=100, safety_mode=False):
        """Relative movement (in mm) of the Z axis"""
        self.move(0, 0, z, f, safety_mode, relative=True)

    def move_rel_xy(self, x, y, f=100, safety_mode=False):
        """Relative movement (in mm) of the X and Y axis"""
        self.move(x, y, 0, f, safety_mode, relative=True)

    def move(self, x, y, z, f=100, safety_mode=False, relative=False, wait_for_idle=True):
        """Absolute or relative movement (in mm) of all 3 axis (X, Y and Z)

        With a safety feature that first moves the Z axis positively
        and then returns it to its original position after X and/or Y are have been positioned.
        """
        if self._serial_iface is None:
            print('[!] Error serial connection is not available')
            return
        
        if not self._check_limits(x, y, z, relative):
            return
    
        if safety_mode:
            # Lift Z axis to not cause damage
            if not self.move(0, 0, 0 - self._safety_distance, f, safety_mode=False):
                return

        # move
        self._serial_iface.flush()
        movement_type = 'Relative' if relative else 'Absolute'
        cmd = MachineController._JOG_REL_MM_CMD if relative else MachineController._JOG_ABS_MM_CMD
        print(f'[+] {movement_type} movement: x={x} y={y} z={z} with feed rate f={f}')
        cmd += b'X' + str(x).encode('utf-8')
        cmd += b'Y' + str(y).encode('utf-8')
        cmd += b'Z' + str(z).encode('utf-8')
        cmd += b'F' + str(f).encode('utf-8')
        self._send_cmd(cmd)

        self._serial_iface.flush()
        if wait_for_idle:
            self._wait_for_idle()

        if safety_mode:
            # Set Z axis to original position
            if not self.move(0, 0, self._safety_distance, f, safety_mode=False):
                return

    def gen_random_path(self, min_x, min_y, max_x, max_y, step_x=1.0, step_y=1.0, number_of_points=0):
        """Generates a path with the specified amount of random points"""
        # Rounding errors may occur in theory. In practice, this should be irrelevant for our accuracy (0.01)
        decimals = 2
        list_x = [round(x, decimals) for x in numeric_range(min_x, max_x + step_x, step_x)]
        list_y = [round(y, decimals) for y in numeric_range(min_y, max_y + step_y, step_y)]
        tmp_path = [namedtuple("Point", "x y")(p[0], p[1]) for p in product(list_x, list_y)]
        if not number_of_points:
            number_of_points = len(tmp_path)
        return [choices(tmp_path, k=number_of_points)]

    def gen_zigzag_path(self, min_x, min_y, max_x, max_y, step_x, step_y, horizontal=False, force_max=False):
        """Generates a zigzag path (straight lines) within the specified boundaries, taking into account the given steps

        This lines can vertically or horizontally.
        If the individual steps do not reach the specified boundaries, this can be forced by the force_max parameter.
        """
        path = self.gen_line_path(min_x, min_y, max_x, max_y, step_x, step_y, horizontal=horizontal, force_max=force_max)
        reverse = False
        for line in path:
            if reverse:
                line.reverse()
            reverse = not reverse
        return path

    def gen_line_path(self, min_x, min_y, max_x, max_y, step_x, step_y, horizontal=False, force_max=False):
        """Generates a path with straight lines within the specified boundaries, taking into account the given steps

        This lines can vertically or horizontally.
        If the individual steps do not reach the specified boundaries, this can be forced by the force_max parameter.
        """
        path = []
        if horizontal:
            max_y, max_x = max_x, max_y
            step_y, step_x = step_x, step_y
        # Rounding errors may occur in theory. In practice, this should be irrelevant for our accuracy (0.01)
        for x in numeric_range(min_x, max_x + step_x, step_x):
            path.append([])
            if x > max_x:
                if force_max:
                    x = max_x
                else:
                    break
            # Rounding errors may occur in theory. In practice, this should be irrelevant for our accuracy (0.01)
            for y in numeric_range(min_y, max_y + step_y, step_y):
                if y > max_y:
                    if force_max:
                        y = max_y
                    else:
                        break
                _x, _y = x, y
                if horizontal:
                    _y, _x = x, y
                decimals = 2
                path[-1].append(namedtuple("Point", "x y")(round(_x, decimals), round(_y, decimals)))
            if x == max_x:
                break
        return path


if __name__ == '__main__':
    print('[+] MachineController')
