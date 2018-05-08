####################################################################################################
# Copyright (c) 2016 - 2018, EPFL / Blue Brain Project
#               Marwan Abdellah <marwan.abdellah@epfl.ch>
#
# This file is part of NeuroMorphoVis <https://github.com/BlueBrain/NeuroMorphoVis>
#
# This library is free software; you can redistribute it and/or modify it under the terms of the
# GNU Lesser General Public License version 3.0 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with this library;
# if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA.
####################################################################################################

__author__ = "Marwan Abdellah"
__copyright__ = "Copyright (c) 2016 - 2018, Blue Brain Project / EPFL"
__credits__ = ["Ahmet Bilgili", "Juan Hernando", "Stefan Eilemann"]
__version__ = "1.0.0"
__maintainer__ = "Marwan Abdellah"
__email__ = "marwan.abdellah@epfl.ch"
__status__ = "Production"

# Blender imports
from mathutils import Vector


####################################################################################################
# Math
####################################################################################################
class Color:
    """Color constants
    """

    ################################################################################################
    # @__init__
    ################################################################################################
    def __init__(self):
        pass

    # Red
    RED = Vector((1.0, 0.0, 0.0))

    # Green
    GREEN = Vector((0.0, 1.0, 0.0))

    # Blue
    BLUE = Vector((0.0, 0.0, 1.0))

    # White
    WHITE = Vector((1.0, 1.0, 1.0))

    # Gray
    GRAY = Vector((0.5, 0.5, 0.5))

    # Black
    BLACK = Vector((0.0, 0.0, 0.0))
