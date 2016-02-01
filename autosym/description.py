# -*- coding: utf-8 -*-
'''
    autosym - Automatic generic schematic symbol generation
    Copyright (C) 2015  Markus Hutzler

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
from enum import Enum

re_option = re.compile("^\[([A-Za-z ]+)\]$")
re_config = re.compile("^([\S ]+)=([\S ]+)$")
re_value2 = re.compile("^([\S ]+)\s*:\s*([\S ]+)$")
re_value3 = re.compile("^([\S ]+)\s*:\s*([\S ]+)\s*:\s*([\S ]+)\s*$")

table = {' ': 200, '!': 254, '"': 444, '#': 644, '$': 536, '%': 719, '&': 796, "'": 235, '(': 304, ')': 304,
         '*': 416, '+': 533, ',': 217, '-': 294, '.': 216, '/': 273, '[': 342, '\\': 273, ']': 342, '^': 247,
         '_': 475, '{': 380, '|': 265, '}': 380, '~': 533,
         '0': 533, '1': 533, '2': 533, '3': 533, '4': 533, '5': 533, '6': 533, '7': 533, '8': 533, '9': 533,
         ':': 216, ';': 217, '<': 533, '=': 533, '>': 533, '?': 361, '@': 757,
         'A': 724, 'B': 598, 'C': 640, 'D': 750, 'E': 549, 'F': 484, 'G': 720, 'H': 742, 'I': 326, 'J': 315,
         'K': 678, 'L': 522, 'M': 835, 'N': 699, 'O': 779, 'P': 532, 'Q': 779, 'R': 675, 'S': 536, 'T': 596,
         'U': 722, 'V': 661, 'W': 975, 'X': 641, 'Y': 641, 'Z': 684,
         'a': 441, 'b': 540, 'c': 448, 'd': 542, 'e': 466, 'f': 321, 'g': 479, 'h': 551, 'i': 278, 'j': 268,
         'k': 530, 'l': 269, 'm': 833, 'n': 560, 'o': 554, 'p': 549, 'q': 534, 'r': 398, 's': 397, 't': 340,
         'u': 542, 'v': 535, 'w': 818, 'x': 527, 'y': 535, 'z': 503,
         }


class ParsingError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Pin(object):
    class Direction(Enum):
        none, left, right, bottom, top = range(5)

    direction = Direction.none

    def __init__(self, data, variant_id=-1, direction=Direction.none, position=0):
        self._number = ""
        self._name = ""
        self._io_type = ""
        self._empty = True
        self._direction = direction
        self._position = position

        if len(data) == 3:
            self._empty = False
            if variant_id > -1 and type(data[0]) == list:
                self._number = data[0][variant_id]
            else:
                self._number = data[0]
            self._name = data[1]
            self._io_type = data[2]

    def __str__(self):
        return self.description()

    def description(self):
        ret = "<Pin: %s - %s (%d)>" % (self._number, self._name, self._position)
        return ret

    @property
    def number(self):
        """ The pin number """
        return self._number

    @property
    def name(self):
        """ The pin name """
        return self._name

    @property
    def position(self):
        return self._position

    @property
    def direction(self):
        return self._direction

    @property
    def type(self):
        return self._io_type

    @property
    def empty(self):
        return self._empty


class Variant(object):
    def __init__(self, package, name, footprint=""):
        self._index = False
        self._name = name
        self._package = package
        self._pins = []
        self.footprint = footprint
        self.options = {}

    def __str__(self):
        return self.description()

    def append_pin(self, pin, filter_empty=True):
        if pin.number == '-':
            return
        if filter_empty and pin.empty:
            return
        self._pins.append(pin)

    def description(self):
        ret = ''
        ret += "<Variant: %s>" % self._name
        # for pin in self.pins:
        #    ret += "    %s\n"%str(pin.name)
        return ret

    @property
    def name(self):
        return self._name
    @property
    def package(self):
        return self._package

    def pins(self, direction=None):
        if direction:
            return filter(lambda x: x.direction == direction, self._pins)

        return self._pins


class Description(object):
    """ The symbol description parses and holds information for a symbol.
    
    Args:
        path
    """

    def __init__(self, path):
        """ where does this go? """
        self._m_left = []
        self._m_right = []
        self._variant_lines = []
        self._variants = []
        self._descriptions = {}
        self._options = {}
        self._path = path
        self._error = False

    @property
    def height(self):
        """ Amount of registered lines """
        return max(len(self._m_left), len(self._m_right))

    @property
    def width(self):
        """
        Calculates and returns the with of the symbol box.
        
        Returns:
            width of the symbol box
        """
        ret = 0
        lines = []
        for pin in self._m_left:
            if len(pin):
                temp = 0
                name = pin[1].strip(' ')
                for ch in name:
                    temp += table[ch]
                lines.append(temp)

        line = 0
        for pin in self._m_right:
            if len(pin):
                temp = 0
                name = pin[1].strip(' ')
                for ch in name:
                    temp += table[ch]
                try:
                    lines[line] += temp
                except:
                    pass
                line += 1

        for line in lines:
            ret = max(ret, line)

        return ret

    @staticmethod
    def _parse_line(line):
        if len(line) == 0:
            return "EMPTY", 0
        if line[0] == '#':
            return "COMMENT", 0

        m = re_option.match(line)
        if m:
            return "OPTION", m.group(1)

        m = re_config.match(line)
        if m:
            return "CONFIG", m.groups()

        m = re_value3.match(line)
        if m:
            return "VALUE", m.groups()

        m = re_value2.match(line)
        if m:
            return "VALUE", m.groups()
        return "ERROR", 0

    " Parse symbol descrition "

    def parse(self):
        handler = open(self._path)
        data = handler.readlines()

        option = ''
        line_nr = 0

        for line in data:
            line_nr += 1
            # remove all line ending characters or white spaces
            line = line.strip('\n\r ')
            # parse line and check if more handeling has to be done
            line_value = self._parse_line(line)

            if line_value[0] == "ERROR":
                raise ParsingError("%d: %s" % (line_nr, line))
            if line_value[0] == "OPTION":
                option = line_value[1]

            if option == 'mapping left' and line_value[0] == "VALUE":
                x = list(line_value[1])
                x[0] = x[0].split(',')
                self._m_left.append(x)
            if option == 'mapping left' and line_value[0] == "EMPTY":
                self._m_left.append([])

            if option == 'mapping right' and line_value[0] == "VALUE":
                x = list(line_value[1])
                x[0] = x[0].split(',')
                self._m_right.append(x)
            if option == 'mapping right' and line_value[0] == "EMPTY":
                self._m_right.append([])
                # make a list ov variants
            if option == 'variants' and line_value[0] == "VALUE":
                self._variant_lines.append(line_value[1])

            # read description
            if option == 'description' and line_value[0] == "CONFIG":
                self._descriptions[line_value[1][0]] = line_value[1][1]

            # read options
            if option == 'option' and line_value[0] == "CONFIG":
                self._options[line_value[1][0]] = line_value[1][1]

        for idx, variant in enumerate(self._variant_lines):
            cnt = 0
            footprint = None
            if len(variant) > 2:
                footprint = variant[2]
            v = Variant(variant[0], variant[1], footprint)
            for pin in self._m_left:
                v.append_pin(Pin(pin, idx, Pin.Direction.left, cnt))
                cnt += 1
            cnt = 0
            for pin in self._m_right:
                v.append_pin(Pin(pin, idx, Pin.Direction.right, cnt))
                cnt += 1
            self._variants.append(v)

    @property
    def variants(self):
        """
        Property to access parses variants.

        Returns: list
            a list ov variants

        """
        return self._variants

    @property
    def descriptions(self):
        """
        Property to access parses variants.

        Returns: list
            a list ov variants

        """
        return self._descriptions

    @property
    def options(self):
        """
        Property to access parses variants.

        Returns: list
            a list ov variants

        """
        return self._options


