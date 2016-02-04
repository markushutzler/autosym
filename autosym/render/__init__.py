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


class SymbolRender(object):
    """Symbol rendering abstract class.

    Parameters
    ----------
    desc: :class:`autosym.description.Description`
        The variant to be used.

    """

    def __init__(self, desc):
        self.description = desc

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