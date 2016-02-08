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


from autosym.description import Pin

"""
Symbol class to generate symbol file
"""


class Symbol(object):
    """Symbol class for gschem.

    Parameters
    ----------
    desc: :class:`autosym.description.Description`
        The variant to be used.

    """

    _ALIGN_LEFT = 0
    _ALIGN_CENTER = 3
    _ALIGN_RIGHT = 6
    _ALIGN_TOP = 2
    _ALIGN_MIDDLE = 1
    _ALIGN_BOTTOM = 0

    _SHOW_NAME_VALUE = 0
    _SHOW_VALUE = 1
    _SHOW_NAME = 2

    def __init__(self, desc):
        self.description = desc
        self.data = 'v 20110115 2\n'

    def _set_description(self, variant_id, x, y):
        line_spacing = 200
        desc = self.description.descriptions
        variant = self.description.variants[variant_id]

        if 'refdes' in desc.keys():
            self.set_text('refdes', desc['refdes'], x, y)
        if 'device' in desc.keys():
            self.set_text('device', desc['device'], x, 0)

        hidden_attrs = ['description', 'comment', 'documentation', 'symversion', 'author', 'dist-license',
                        'use-license']

        main_set = False
        fp_cnt = len(variant.footprints)
        for footprint in variant.footprints:
            if not main_set:
                y += line_spacing
                self.set_text('footprint', footprint, x, y,
                          color=8, size=10, visibility=0, show=self._SHOW_NAME_VALUE)
                main_set = True
            else:
                fp_cnt -= 1
                y += line_spacing
                self.set_text('footprint_%d' % fp_cnt, footprint, x, y,
                          color=8, size=8, visibility=0, show=self._SHOW_NAME_VALUE)

        for attr in hidden_attrs[::-1]:
            y += line_spacing
            self.set_text(attr, desc.get(attr, ""), x, y,
                          color=8, size=8, visibility=0, show=self._SHOW_NAME_VALUE)

    def _generate_box(self, variant_id):
        options = self.description.options

        symbol_width = int(options.get('symbol_width', 1000))
        pin_length = int(options.get('pin_length', 300))
        pin_grid = int(options.get('pin_grid', 200))
        x_padding = pin_length + 200
        y_padding = 200
        box_width = symbol_width
        box_height = (self.description.height + 1) * pin_grid

        self.set_box(x_padding, y_padding, box_width, box_height)

        variant = self.description.variants[variant_id]
        for pin in variant.pins():
            y_pos = box_height - (pin.position + 1) * pin_grid + y_padding

            name = pin.name
            if name.startswith('!'):
                name = '\_' + name[1:]

            if pin.direction == Pin.Direction.left:
                self.set_pin(name, pin.number, pin.type, x_padding - pin_length, y_pos, pin_length, False)
            if pin.direction == Pin.Direction.right:
                self.set_pin(name, pin.number, pin.type, x_padding + box_width + pin_length, y_pos, pin_length, True)

        text_pos = y_padding + box_height + 100
        self._set_description(variant_id, x_padding, text_pos)

        return self.data

    def _generate_header(self, variant_id):
        options = self.description.options
        variant = self.description.variants[variant_id]

        pin_length = int(options.get('pin_length', 150))
        pin_grid = int(options.get('pin_grid', 200))
        rows = int(options.get('rows', 1))
        pin_geometry = options.get('pin_geometry', 'box')
        x_padding = pin_length + 200
        y_padding = 200
        y = y_padding + pin_grid * len(variant.pins())/rows
        self._set_description(variant_id, x_padding, y)
        y -= 100

        for pin in variant.pins():
            y_pin = y-(pin.position-1)*pin_grid
            if pin.direction == Pin.Direction.left:
                x = x_padding
                self.set_pin(pin.name, pin.number, pin.type, x - pin_length,
                             y_pin, pin_length, False, show_number=pin.show_number, label_padding=150)
                if pin_geometry in ['box', 'hole']:
                    self.set_box(x, y_pin-50, 100, 100, color=4, line_width=30)
                if pin_geometry in ['circle', 'hole']:
                    self.set_circle(x+50, y_pin, 50, color=4, line_width=30)

            if pin.direction == Pin.Direction.right:
                x = x_padding + 800
                self.set_pin(pin.name, pin.number, pin.type, x + pin_length,
                             y_pin, pin_length, True, show_number=pin.show_number, label_padding=150)
                if pin_geometry in ['box', 'hole']:
                    self.set_box(x-100, y_pin-50, 100, 100, color=4, line_width=30)
                if pin_geometry in ['circle', 'hole']:
                    self.set_circle(x-50, y_pin, 50, color=4, line_width=30)

        return self.data

    def generate(self, variant_id=0):
        """ Generate symbol data.

        Parameters
        ----------
        variant_id: :class:`int`
            The index of the variant to be used.

        Returns
        -------
        string
            Symbol content of the selected variant.
        """
        options = self.description.options
        symbol_type = options.get('type', 'box')
        if symbol_type == 'header':
            return self._generate_header(variant_id)
        return self._generate_box(variant_id)

    def filename(self, variant_id=0):
        """ Generate symbol file name.

        Parameters
        ----------
        variant_id: :class:`int`
            The index of the variant to be used.

        Returns
        -------
        (string, string)
           The (folder, filename) of the selected variant. Folder can be None.

        """
        desc = self.description.descriptions
        variant = self.description.variants[variant_id].package

        if variant == '-':
            variant = ''
        folder = desc.get('category', '')
        device = desc.get('device', '')
        if not device:
            raise KeyError('Device name is not defined.')
        if folder:
            return folder, "%s%s.sym" % (device, variant)
        return None, "%s%s.sym" % (device, variant)

    def set_text(self, name, value, x, y, color=8, size=10, visibility=1, show=_SHOW_VALUE, angle=0, alignment=0,
                 lines=1):
        """ Add text component to symbol

        Parameters
        ----------
        name: :class:`string`
            The text name.
        value: :class:`string`
            The text value.
        x: :class:`int`
            x coordinates
        y: :class:`int`
            y coordinates

        Other Parameters
        ----------------
        color: :class:`int`
            color of text
        size: :class:`int`
            size of text
        visibility: :class:`int`
            1 for visible, 0 for hidden
        show: :class:`int`
            what should be shown _SHOW_NAME_VALUE, _SHOW_VALUE or _SHOW_NAME
        angle: :class:`int`
            text direction 0, 90, 128 or 240
        alignment: :class:`int`
            text alignment
        lines: :class:`int`
            amount of lines
        """
        self.data += "T %d %d %d %d %d %d %d %d %d\n" % (x, y, color, size, visibility, show, angle, alignment, lines)
        self.data += "%s=%s\n" % (name, value)

    def set_pin(self, name, number, pin_type, x, y, length=300, mirror=False, show_number=1, show_name=1, label_padding=10):
        """ Add pin to symbol

        Parameters
        ----------
        name: :class:`string`
            The pin name.
        number: :class:`string`
            The pin number.
        pin_type: :class:`string`
            The pin type.

        Other Parameters
        ----------------
        length: :class:`int`
            The pin length
        mirror: :class:`bool`
            Set to true to mirror the pin.
        """
        align1 = self._ALIGN_MIDDLE + self._ALIGN_LEFT
        align2 = self._ALIGN_BOTTOM + self._ALIGN_RIGHT
        offset = 1
        if mirror:
            align1 = self._ALIGN_MIDDLE + self._ALIGN_RIGHT
            align2 = self._ALIGN_BOTTOM + self._ALIGN_LEFT
            offset = -1

        self.data += "P %d %d %d %d 1 0 0\n" % (x, y, x + length * offset, y)
        self.data += "{\n"
        self.set_text('pinnumber', number, x + (length - 50) * offset, y + 50, 5, 8, show_number, self._SHOW_VALUE, 0, align2, 1)
        self.set_text('pinseq', number, x + (length - 50) * offset, y + 50, 5, 8, 0, self._SHOW_VALUE, 0, align2, 1)
        self.set_text('pintype', pin_type, x + (length - 50) * offset, y + 50, 5, 8, 0, self._SHOW_VALUE, 0, align2, 1)

        self.set_text('pinlabel', name, x + (length + label_padding) * offset, y, 5, 10, show_name, self._SHOW_VALUE, 0, align1, 1)
        self.data += "}\n"

    def set_box(self, x, y, width, height, color=3, line_width=0):
        self.data += "B %d %d %d %d %d %d 0 0 -1 -1 0 -1 -1 -1 -1 -1\n" % (x, y, width, height, color, line_width)

    def set_circle(self, x, y, radius, color=3, line_width=0):
        self.data += "V %d %d %d %d %d 0 0 -1 -1 0 -1 -1 -1 -1 -1\n" % (x, y, radius, color, line_width)
if __name__ == '__main__':
    pass
