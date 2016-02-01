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

import os
import sys
from autosym.render import gschem
from autosym.description import Description

if __name__ == '__main__':

    symd_path = sys.argv[1]
    output_path = sys.argv[2]

    file_list = []

    # find all symd files in input directory
    for r, d, f in os.walk(symd_path):
        for files in f:
            if files.endswith(".symx"):
                file_list.append(os.path.join(r, files))

    # generate symbols for symbol description files
    for f in file_list:
        print 'Processing file', f
        symd = Description(f)
        symd.parse()
        g = gschem.Symbol(symd)
        data = g.generate(0)

        #h = open("test.sch", 'w')
        h = open("test2.sch", 'w')
        h.write(data)
        h.close()

