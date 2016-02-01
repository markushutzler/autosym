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

from autosym.description import Description, Pin

"""
Symbol calss to generate symbol file
"""


class Symbol(object):
    """Symbol class for gschem.

    Parameters
    ----------
    desc: :class:`autosym.description.Description`
        The variant to be used.

    """
    _ALIGN_LEFT = 0  #: Text align left
    _ALIGN_CENTER = 3
    _ALIGN_RIGHT = 6

    _ALIGN_TOP = 2
    _ALIGN_MIDDLE = 1
    _ALIGN_BOTTOM = 0

    '''
    2 -- 5 -- 8
	|    |    |
	1 -- 4 -- 7
	|    |    |
	0 -- 3 -- 6
	'''

    _SHOW_NAME_VALUE = 0
    _SHOW_VALUE = 1
    _SHOW_NAME = 2

    def __init__(self, desc):
        self.description = desc
        self.data = 'v 20110115 2\n'

    def generate(self, variant_id=0):
        """
        Generates the symbol data.

        """
        # calculate distance and other parapeters


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


        print self.description.options
        print self.description.descriptions

        variant = self.description.variants[variant_id]
        print "generating variant: %s" % variant._name

        for pin in variant.pins():
            y_pos = box_height - (pin.position + 1) * pin_grid + y_padding

            name = pin.name
            if name.startswith('!'):
               name = '\_'+name[1:]

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

        for attr in hidden_attrs[::-1]:
            text_pos += line_spacing
            value = ""
            if attr in desc.keys():
                value = desc[attr]
            print attr, value
            self.set_text(attr, value, x_padding, text_pos, 8, 0, self._SHOW_NAME_VALUE)

        return self.data

    def set_text(self, name, value, x, y, color=8, size=10, visibility=1, show=_SHOW_VALUE, angle=0, alignment=0,
                 lines=1):
        """
        Set a text within the symbol.

         Parameters
        ----------
        name: :class:`string`
            The text name.
        value: :class:`string`
            The text value.
        x: :class:`int`
            x coordinates.
        y: :class:`int`
            y coordinates.
        color: :class:`int`
            y coordinates.
        size: :class:`int`
            y coordinates.
        visibility: :class:`int`
            y coordinates.
        show: :class:`int`
            y coordinates.
        angle: :class:`int`
            y coordinates.
        alignment: :class:`int`
            y coordinates.
        lines: :class:`int`
            y coordinates.

            
        Only name, value and position (x/y) need to be set.
        
        Returns None
        """
        # T x y color size visibility show name value angle alignment num lines
        self.data += "T %d %d %d %d %d %d %d %d %d\n" % (x, y, color, size, visibility, show, angle, alignment, lines)
        self.data += "%s=%s\n" % (name, value)

    """
    Add a pin to the symbol

    """

    def set_pin(self, name, number, pin_type, x, y, length=300, mirror=False):
        rotation = 180
        align1 = self._ALIGN_MIDDLE + self._ALIGN_LEFT
        align2 = self._ALIGN_BOTTOM + self._ALIGN_RIGHT
        offset = 1
        if mirror:
            rotation = 0
            align1 = self._ALIGN_MIDDLE + self._ALIGN_RIGHT
            align2 = self._ALIGN_BOTTOM + self._ALIGN_LEFT
            offset = -1

        self.data += "P %d %d %d %d 1 0 0\n" % (x, y, x + length * offset, y)
        self.data += "{\n"
        self.set_text('pinnumber', number, x + (length - 50) * offset, y + 50, 5, 8, 1, self._SHOW_VALUE, 0, align2, 1)
        self.set_text('pinseq', number, x + (length - 50) * offset, y + 50, 5, 8, 0, self._SHOW_VALUE, 0, align2, 1)
        self.set_text('pintype', pin_type, x + (length - 50) * offset, y + 50, 5, 8, 0, self._SHOW_VALUE, 0, align2, 1)

        self.set_text('pinlabel', name, x + (length+50) * offset, y, 5, 10, 1, self._SHOW_VALUE, 0, align1, 1)
        self.data += "}\n"

    """
    Add a pox to the symbol
    """

    def set_box(self, x, y, width, height):
        self.data += "B %d %d %d %d 3 0 0 0 -1 -1 0 -1 -1 -1 -1 -1\n" % (x, y, width, height)


if __name__ == '__main__':
    pass

'''
def make_sym(self, path):
        if self.error:
            return None
        #print 'm_left',self._m_left
        #print 'm_right',self._m_right
        #print 'variants',variants
        #print 'descriptions', descriptions
        #print 'options', options

        min_width = 400
        if 'min_width' in self.options.keys():
            min_width = int(self.options['min_width'])

        pin_length = 300
        if 'pin_length' in self.options.keys():
            pin_length = int(self.options['pin_length'])

        pin_grid = 200
        if 'pin_grid' in self.options.keys():
            pin_grid = int(self.options['pin_grid'])

        box_width = int((self.width()/5.4+200)/100)
        box_width = 100*(box_width+1)
        box_width = max(box_width,min_width)

        sym = symbol.Symbol()

        x = 0
        y = 0
        height = (max(len(self._m_left),len(self._m_right))-1)*pin_grid+200
        ht_x = box_width+pin_length+pin_length+200
        ht_y = 0

        category = ''
        if 'category' in self.descriptions.keys():
            category = self.descriptions['category']

        if 'refdes' in self.descriptions.keys():
            sym._set_text('refdes',self.descriptions['refdes'],x+pin_length , y+height+200)
        if 'device' in self.descriptions.keys():
            sym._set_text('device',self.descriptions['device'],x+box_width+pin_length , y+height+200, alignment=6)

        if 'dist-license' in self.descriptions.keys():
            sym._set_text('dist-license',self.descriptions['dist-license'], ht_x , ht_y, visibility=0, show=sym.SHOW_NAME_VALUE)
            ht_y+=200

        if 'use-license'  in self.descriptions.keys():
            sym._set_text('use-license',self.descriptions['use-license'],ht_x ,ht_y, visibility=0, show=sym.SHOW_NAME_VALUE)
            ht_y+=200

        if 'comment' in self.descriptions.keys():
            sym._set_text('comment',self.descriptions['comment'], ht_x, ht_y, visibility=0, show=sym.SHOW_NAME_VALUE)
            ht_y+=200

        if 'documentation' in self.descriptions.keys():
            sym._set_text('documentation',self.descriptions['documentation'], ht_x, ht_y, visibility=0, show=sym.SHOW_NAME_VALUE)
            ht_y+=200

        if 'symversion' in self.descriptions.keys():
            sym._set_text('symversion',self.descriptions['symversion'], ht_x, ht_y, visibility=0, show=sym.SHOW_NAME_VALUE)
            ht_y+=200

        if 'author' in self.descriptions.keys():
            sym._set_text('author',self.descriptions['author'], ht_x, ht_y, visibility=0, show=sym.SHOW_NAME_VALUE)
            ht_y+=200


        sym.set_box(x+pin_length, y, box_width, height+100)

        header_data = sym.data

        variant_nr = 0
        for variant in self._variant_lines:
            sym.data = header_data

            if 'description' in self.descriptions.keys():
                sym._set_text('description',self.descriptions['description']+', '+variant[1], ht_x, ht_y, visibility=0, show=sym.SHOW_NAME_VALUE)


            y = height-100
            x = 0

            first_pin = y
            for pin in self._m_left:
                if len(pin):
                    numbers = pin[0]
                    if len(numbers) > variant_nr:
                        name = pin[1].strip(' ')
                        #print "LEFT:",name, variant_nr, pin
                        if name.startswith('!'):
                            name = '\_'+name[1:]
                        try:
                            sym._set_text(name, int(numbers[variant_nr]), pin[2].strip(' '), x, y, length=pin_length)
                        except ValueError:
                            pass

                y-=pin_grid

            x += box_width+pin_length+pin_length
            y = first_pin
            for pin in self._m_right:
                if len(pin):
                    numbers = pin[0]
                    if len(numbers) > variant_nr:
                        name = pin[1].strip(' ')
                        #print "Right:",name, variant_nr, pin
                        if name.startswith('!'):
                            name = '\_'+name[1:]
                        try:
                            sym._set_text(name, int(numbers[variant_nr]), pin[2].strip(' '), x, y,length=pin_length, mirror=True)
                        except ValueError:
                            pass
                y-=pin_grid


            #print sym.data
            file_path = path+'/'+category+'/'
            file_name = file_path+self.descriptions['device']+variant[0]+'.sym'

            if not os.path.isdir(file_path):
                os.mkdir(file_path)
            print "Generating %s package: %s"%(variant[0],file_name)
            h = open(file_name,'w')
            h.write(sym.data)
            h.close()

            variant_nr += 1
        print
'''
