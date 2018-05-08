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

__author__      = "Marwan Abdellah"
__copyright__   = "Copyright (c) 2016 - 2018, Blue Brain Project / EPFL"
__credits__     = ["Ahmet Bilgili", "Juan Hernando", "Stefan Eilemann"]
__version__     = "1.0.0"
__maintainer__  = "Marwan Abdellah"
__email__       = "marwan.abdellah@epfl.ch"
__status__      = "Production"


# System imports
import os, sys, copy, random, math, numpy

# Blender imports
import bpy
from mathutils import Vector, Matrix

# Append the internal modules into the system paths
sys.path.append("%s/../modules" % os.path.dirname(os.path.realpath(__file__)))

# Internal imports
from morphology_analysis_ops import *
from morphology_connection_ops import *
from morphology_drawing_ops import *
from morphology_geometry_ops import *
from morphology_intersection_ops import *
from morphology_polyline_ops import *
from morphology_repair_ops import *
from morphology_resampling_ops import *
from morphology_verification_ops import *


####################################################################################################
# @apply_operation_to_arbor
####################################################################################################
def apply_operation_to_arbor(*args):
    """
    Apply a given function/filter/operation to a given arbor recursively.

    :param args:
        Arguments list, where the first argument is always the root section of the arbor and the
        second argument is the function of the operation/filter that will be applied
        and the rest of the arguments are those that will be passed to the function itself.
    """

    # The section is the first argument
    section = args[0]

    # The operation is the second argument
    operation = args[1]

    # Construct the root section arguments list, add the section and ignore the operation
    section_args = [section]
    for i in range(2, len(args)):
        section_args.append(args[i])

    # Apply the operation/filter to the first section of the arbor
    operation(*section_args)

    # Apply the operation/filter to the children of the arbors
    for child in section.children:

        # Construct the child section arguments list, add the child and add the operation
        section_args = [child]
        for i in range(1, len(args)):
            section_args.append(args[i])

        # Validate the rest of the skeleton of the arbor
        apply_operation_to_arbor(*section_args)


####################################################################################################
# @apply_operation_to_morphology
####################################################################################################
def apply_operation_to_morphology(*args):
    """
    Apply a given function/filter/operation to a given morphology object including all of its
    arbors recursively.

    :param args:
        Arguments list, where the first argument is always the morphology and the second argument
        is the function of the operation/filter that will be applied and the rest of the arguments
        are those that will be passed to the function.
    """

    # The morphology is the first argument
    morphology=args[0]

    # Apical dendrite
    if morphology.apical_dendrite is not None:

        # Construct arbor arguments list
        arbor_args = [morphology.apical_dendrite]
        for i in range(1, len(args)):
            arbor_args.append(args[i])

        # Apply the operation/filter to the arbor
        apply_operation_to_arbor(*arbor_args)

    # Basal dendrites
    if morphology.dendrites is not None:

        # Dendrite by dendrite
        for dendrite in morphology.dendrites:

            # Construct arbor arguments list
            arbor_args = [dendrite]
            for i in range(1, len(args)):
                arbor_args.append(args[i])

            # Apply the operation/filter to the arbor
            apply_operation_to_arbor(*arbor_args)

    # Axon
    if morphology.axon is not None:

        # Construct arbor arguments list
        arbor_args = [morphology.axon]
        for i in range(1, len(args)):
            arbor_args.append(args[i])

        # Apply the operation/filter to the arbor
        apply_operation_to_arbor(*arbor_args)