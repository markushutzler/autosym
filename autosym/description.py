# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# autosym - Automatic generic schematic symbol generation
# Copyright (C) 2015  Markus Hutzler
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from enum import Enum

re_option = re.compile("^\[([A-Za-z ]+)\]?")
re_config = re.compile("^([\S ]+)=([\S ]+)?")


class ParsingError(Exception):

    line = ""
    line_nr = -1
    file = ""

    def __init__(self, file, line_nr, line):
        self.line = line
        self.line_nr = line_nr
        self.file = file

    def __str__(self):
        return repr(self.line)


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
        self._footprints = []
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

    def append_footprint(self, fp):
        self._footprints.append(fp)

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

    @property
    def footprints(self):
        return self._footprints

    def pins(self, direction=None):
        if direction:
            return filter(lambda x: x.direction == direction, self._pins)

        return self._pins


class Description(object):
    """ The symbol description parses and holds information for a symbol. Tis class provides information about the
    different variants op a symbol.
    
    Parameters
    ----------
    path: :class:`string`
        The path to the symbol description file.
    """

    def __init__(self, path):
        """ where does this go? """
        self._m_left = []
        self._m_right = []
        self._variant_lines = []
        self._variants = []
        self._descriptions = {}
        self._options = {}
        self._footprints = []
        self._path = path
        self._error = False

    @property
    def height(self):
        """ Amount of registered lines """
        return max(len(self._m_left), len(self._m_right))

    @staticmethod
    def _parse_line(line):
        line.strip(' \t\r\n')
        c = line.find('#')
        if c == 0:
            return "COMMENT", line[:c]

        if c > 0:
            # todo: handle comment without missing same line's contents
            # comment = line[c:]
            line = line[:c]

        if len(line) == 0:
            return "EMPTY", 0

        m = re_option.match(line)
        if m:
            return "OPTION", m.group(1)

        m = re_config.match(line)
        if m:
            return "CONFIG", map(str.strip, m.groups())

        grp = re.split(":?", line)
        if len(grp) > 1:
            return "VALUE", map(str.strip, grp)

        return "ERROR", 0

    def parse(self):
        """ Parse symbol descrition """

        handler = open(self._path)
        data = handler.readlines()

        option = ''
        line_nr = 0

        for line in data:
            line_nr += 1
            # remove all line white spaces
            line = line.strip('\n\r\t ')
            # parse line and check if more handling has to be done
            vtype, value = self._parse_line(line)
            if vtype == "ERROR":
                raise ParsingError(self._path, line_nr, line)
            if vtype == "OPTION":
                option = value

            if option == 'mapping left' and vtype == "VALUE":
                x = list(value)
                x[0] = x[0].split(',')
                self._m_left.append(x)
            if option == 'mapping left' and vtype == "EMPTY":
                self._m_left.append([])

            if option == 'mapping right' and vtype == "VALUE":
                x = list(value)
                x[0] = x[0].split(',')
                self._m_right.append(x)
            if option == 'mapping right' and vtype == "EMPTY":
                self._m_right.append([])
                # make a list ov variants
            if option == 'variants' and vtype == "VALUE":
                self._variant_lines.append(value)

            if option == 'footprints' and vtype == "VALUE":
                self._footprints.append(value)

            # read description
            if option == 'description' and vtype == "CONFIG":
                self._descriptions[value[0]] = value[1]

            # read options
            if option == 'option' and vtype == "CONFIG":
                self._options[value[0]] = value[1]

        symbol_type = 'box'
        if 'type' in self._options.keys():
            symbol_type = self._options['type']

        if symbol_type == 'box':
            for idx, variant in enumerate(self._variant_lines):
                v = Variant(variant[0], variant[1])
                for fp in self._footprints:
                    if len(fp) == 2 and fp[0] == variant[0]:
                        for f in map(str.strip, fp[1].split(',')):
                            v.append_footprint(f)

                cnt = 0
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
        List of variants. Variants contain the packaging information and pins of different versions
        of the same component.
        """
        return self._variants

    @property
    def descriptions(self):
        """
        Directory of descriptions. Descriptions are key / value pairs that describe the component. Some
        are placed into the symbol during rendering, others are used by the render to categorize the component.
        """
        return self._descriptions

    @property
    def options(self):
        """
        Directory of options. Options are key / value pairs that define rendering parameters.
        """
        return self._options
