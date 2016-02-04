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

from autosym.description import Pin
from autosym.render import SymbolRender

"""
Symbol class to generate symbol file
"""


class Symbol(SymbolRender):
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

    '''
    def _generate_header(self, variant_id):
        options = self.description.options
        symbol_width = 1000
        if 'symbol_width' in options.keys():
            symbol_width = int(options['symbol_width'])

        pin_length = 300
        if 'pin_length' in options.keys():
            pin_length = int(options['pin_length'])

        pin_grid = 200
        if 'pin_grid' in options.keys():
            pin_grid = int(options['pin_grid'])

        numbering = 'Z'
        if 'numbering' in options.keys():
            numbering = options['numbering']

        pin_geomtry = 'box'
        if 'pin_length' in options.keys():
            pin_geomtry = options['pin_geomtry']

        return self.data
    '''

    def _generate_box(self, variant_id):
        options = self.description.options

        symbol_width = 1000
        if 'symbol_width' in options.keys():
            symbol_width = int(options['symbol_width'])

        pin_length = 300
        if 'pin_length' in options.keys():
            pin_length = int(options['pin_length'])

        pin_grid = 200
        if 'pin_grid' in options.keys():
            pin_grid = int(options['pin_grid'])

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
        line_spacing = 200
        desc = self.description.descriptions

        if 'refdes' in desc.keys():
            self.set_text('refdes', desc['refdes'], x_padding, text_pos)
        if 'device' in desc.keys():
            self.set_text('device', desc['device'], x_padding + box_width, text_pos, alignment=6)

        hidden_attrs = ['description', 'comment', 'documentation', 'symversion', 'author', 'dist-license',
                        'use-license']
        if variant.footprint:
            text_pos += line_spacing
            self.set_text('footprint', variant.footprint, x_padding, text_pos,
                          color=8, size=10, visibility=0, show=self._SHOW_NAME_VALUE)
        for attr in hidden_attrs[::-1]:
            text_pos += line_spacing
            value = ""
            if attr in desc.keys():
                value = desc[attr]
            self.set_text(attr, value, x_padding, text_pos,
                          color=8, size=8, visibility=0, show=self._SHOW_NAME_VALUE)
        return self.data

    def generate(self, variant_id=0):
        """ Generate symbol data.

        Parameters
        ----------
        variant_id: :class:`int`
            The index of the variant to be used.

        Returns
        -------
        The data string of the generated variant.
        """

        '''
        options = self.description.options
        if 'type' in options.keys():
            if options['type'] == 'header':
                return self._generate_header(variant_id)
        '''
        return self._generate_box(variant_id)

    def filename(self, variant_id=0):
        """ Generate symbol file name.

        Parameters
        ----------
        variant_id: :class:`int`
            The index of the variant to be used.

        Returns
        -------
        The (folder, filename) the variant. The folder can be None.
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
        """ Add text to file

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

        Only name, value and position (x/y) need to be set.
        
        Returns
        -------
        None
        """
        # T x y color size visibility show name value angle alignment num lines
        self.data += "T %d %d %d %d %d %d %d %d %d\n" % (x, y, color, size, visibility, show, angle, alignment, lines)
        self.data += "%s=%s\n" % (name, value)

    def set_pin(self, name, number, pin_type, x, y, length=300, mirror=False):
        align1 = self._ALIGN_MIDDLE + self._ALIGN_LEFT
        align2 = self._ALIGN_BOTTOM + self._ALIGN_RIGHT
        offset = 1
        if mirror:
            align1 = self._ALIGN_MIDDLE + self._ALIGN_RIGHT
            align2 = self._ALIGN_BOTTOM + self._ALIGN_LEFT
            offset = -1

        self.data += "P %d %d %d %d 1 0 0\n" % (x, y, x + length * offset, y)
        self.data += "{\n"
        self.set_text('pinnumber', number, x + (length - 50) * offset, y + 50, 5, 8, 1, self._SHOW_VALUE, 0, align2, 1)
        self.set_text('pinseq', number, x + (length - 50) * offset, y + 50, 5, 8, 0, self._SHOW_VALUE, 0, align2, 1)
        self.set_text('pintype', pin_type, x + (length - 50) * offset, y + 50, 5, 8, 0, self._SHOW_VALUE, 0, align2, 1)

        self.set_text('pinlabel', name, x + (length + 50) * offset, y, 5, 10, 1, self._SHOW_VALUE, 0, align1, 1)
        self.data += "}\n"

    def set_box(self, x, y, width, height):
        self.data += "B %d %d %d %d 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1\n" % (x, y, width, height)

if __name__ == '__main__':
    pass
