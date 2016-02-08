#!/usr/bin/env python
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


import os
import errno
from optparse import OptionParser
from autosym.render import gschem
from autosym.description import Description, ParsingError

if __name__ == '__main__':
    usage = "usage: %prog [options] library-path output-path"
    parser = OptionParser(usage=usage, version="%prog 0.1")
    parser.add_option("-q", "",
                      default=False, action="store_true", dest="quiet", help="don't print status messages to stdout")
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.error("incorrect number of arguments")
    symd_path = args[0]
    output_path = args[1]

    if not os.path.isdir(symd_path):
        parser.error("input path is not a directory")

    try:
        os.makedirs(output_path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
    if not os.path.isdir(output_path):
        parser.error("output path is not a directory")

    file_list = []

    # find all symd files in input directory
    for r, d, f in os.walk(symd_path):
        for files in f:
            if files.endswith(".symv"):
                file_list.append(os.path.join(r, files))
            if files.endswith(".symd"):
                file_list.append(os.path.join(r, files))

    # generate symbols for symbol description files
    for f in file_list:
        if not options.quiet:
            print f, ">>",
        symd = Description(f)
        try:
            symd.parse()
            for index, variant in enumerate(symd.variants):
                g = gschem.Symbol(symd)
                data = g.generate(index)
                subfolder, filename = g.filename(index)
                if subfolder:
                    subfolder = output_path+'/'+subfolder+'/'
                else:
                    subfolder = output_path+'/'

                try:
                    os.makedirs(subfolder)
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise
                if not options.quiet:
                    print subfolder+filename,
                h = open(subfolder+filename, 'w')
                h.write(data)
                h.close()
            if not options.quiet:
                print
            
        except ParsingError, e:
            print 'Parsing error in %s line %d:\n%s' % (e.file, e.line_nr, e.line)

