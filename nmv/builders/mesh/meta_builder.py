####################################################################################################
# Copyright (c) 2016 - 2018, EPFL / Blue Brain Project
#               Marwan Abdellah <marwan.abdellah@epfl.ch>
#
# This file is part of NeuroMorphoVis <https://github.com/BlueBrain/NeuroMorphoVis>
#
# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, version 3 of the License.
#
# This Blender-based tool is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <http://www.gnu.org/licenses/>.
####################################################################################################


# System imports
import copy

# Blender imports
import bpy, mathutils

# Internal modules
import nmv
import nmv.builders
import nmv.enums
import nmv.mesh
import nmv.shading
import nmv.skeleton
import nmv.utilities
import nmv.scene


####################################################################################################
# @MetaBuilder
####################################################################################################
class MetaBuilder:
    """Mesh builder that creates high quality meshes with nice bifurcations based on meta objects"""

    ################################################################################################
    # @__init__
    ################################################################################################
    def __init__(self,
                 morphology,
                 options):
        """Constructor

        :param morphology:
            A given morphology skeleton to create the mesh for.
        :param options:
            Loaded options from NeuroMorphoVis.
        """

        # Morphology
        self.morphology = morphology

        # Loaded options from NeuroMorphoVis
        self.options = options

        # A list of the colors/materials of the soma
        self.soma_materials = None

        # A list of the colors/materials of the axon
        self.axon_materials = None

        # A list of the colors/materials of the basal dendrites
        self.basal_dendrites_materials = None

        # A list of the colors/materials of the apical dendrite
        self.apical_dendrite_materials = None

        # A list of the colors/materials of the spines
        self.spines_materials = None

        # A reference to the reconstructed soma mesh
        self.reconstructed_soma_mesh = None

        # A reference to the reconstructed spines mesh
        self.spines_mesh = None

        # A parameter to track the current branching order on each arbor
        # NOTE: This parameter must get reset when you start working on a new arbor
        self.branching_order = 0

        # A list of all the meshes that are reconstructed on a piecewise basis and correspond to
        # the different components of the neuron including soma, arbors and the spines as well
        self.reconstructed_neuron_meshes = list()

        # Meta object skeleton, used to build the skeleton of the morphology
        self.meta_skeleton = None

        # Meta object mesh, used to build the mesh of the morphology
        self.meta_mesh = None

        # A scale factor that was figured out by trial and error to correct the scaling of the radii
        self.magic_scale_factor = 1.575

        # The smallest detected radius while building the model, to be used for meta-ball resolution
        self.smallest_radius = 10.0

    ################################################################################################
    # @verify_and_repair_morphology
    ################################################################################################
    def verify_and_repair_morphology(self):
        """Verifies and repairs the morphology if the contain any artifacts that would potentially
        affect the reconstruction quality of the mesh.
        """

        # Remove the internal samples, or the samples that intersect the soma at the first
        # section and each arbor
        nmv.skeleton.ops.apply_operation_to_morphology(
            *[self.morphology, nmv.skeleton.ops.remove_samples_inside_soma])

        # Verify the connectivity of the arbors to the soma to filter the disconnected arbors,
        # for example, an axon that is emanating from a dendrite or two intersecting dendrites
        nmv.skeleton.ops.update_arbors_connection_to_soma(self.morphology)

        # Label the primary and secondary sections based on angles
        nmv.skeleton.ops.apply_operation_to_morphology(
            *[self.morphology,
              nmv.skeleton.ops.label_primary_and_secondary_sections_based_on_angles])


    ################################################################################################
    # @create_meta_segment
    ################################################################################################
    def create_meta_segment(self, p1, p2, r1, r2):
        """Constructs a segment that is composed of two points with a meta object.

        :param p1:
            First point coordinate.
        :param p2:
            Second point coordinate.
        :param r1:
            First point radius.
        :param r2:
            Second point radius.
        """

        # Segment vector
        segment = p2 - p1
        segment_length = segment.length

        # Make sure that the segment length is not zero
        # TODO: Verify this when the radii are greater than the distance
        if segment_length < 0.001:
            return

        # Verify the radii, or fix them
        if r1 < 0.001 * segment_length:
            r1 = 0.001 * segment_length
        if r2 < 0.001 * segment_length:
            r2 = 0.001 * segment_length

        # Compute the deltas between the first and last points along the segments
        dr = r2 - r1
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dz = p2[2] - p1[2]

        # Keep track on the distance traveled along the segment while building, initially 0
        travelled_distance = 0.0

        # Local points, initially at the first point
        r = r1
        x = p1[0]
        y = p1[1]
        z = p1[2]

        # Construct the meta elements along the segment
        while travelled_distance < segment_length:

            # Make a meta ball (or sphere) at this point
            meta_element = self.meta_skeleton.elements.new()

            # Set its radius
            # TODO: Find a solution to compensate the connection points
            meta_element.radius = r

            # Update its coordinates
            meta_element.co = (x, y, z)

            # Proceed to the second point
            travelled_distance += r / 2

            r = r1 + (travelled_distance * dr / segment_length)

            # Get the next point
            x = p1[0] + (travelled_distance * dx / segment_length)
            y = p1[1] + (travelled_distance * dy / segment_length)
            z = p1[2] + (travelled_distance * dz / segment_length)

    ################################################################################################
    # @create_meta_section
    ################################################################################################
    def create_meta_section(self,
                            section):
        """Create a section with meta objects.

        :param section:
            A given section to extrude a mesh around it.
        """

        # Get the list of samples
        samples = section.samples

        # Ensure that the section has at least two samples, otherwise it will give an error
        if len(samples) < 2:
            return

        # Proceed segment by segment
        for i in range(len(samples) - 1):

            if samples[i].radius < self.smallest_radius:
                self.smallest_radius = samples[i].radius

            # Create the meta segment
            self.create_meta_segment(
                p1=samples[i].point,
                p2=samples[i + 1].point,
                r1=samples[i].radius * self.magic_scale_factor,
                r2=samples[i + 1].radius * self.magic_scale_factor)


    def create_meta_poly_line(self,
                              poly_line_data):

        # Ensure that the poly-line has at least two samples, otherwise it will give an error
        if len(poly_line_data) < 2:
            return

        # Proceed segment by segment
        for i in range(len(poly_line_data) - 1):

            #print(poly_line_data[i][0][0])

            point_1 = poly_line_data[i]
            point_2 = poly_line_data[i + 1]

            if poly_line_data[i][1] < self.smallest_radius:
                self.smallest_radius = poly_line_data[i][1]

            p1 = mathutils.Vector((point_1[0][0], point_1[0][1], point_1[0][2]))
            r1 = point_1[1]
            p2 = mathutils.Vector((point_2[0][0], point_2[0][1], point_2[0][2]))
            r2 = point_2[1]

            # Create the meta segment
            self.create_meta_segment(
                p1=p1, p2=p2, r1=r1 * self.magic_scale_factor, r2=r2 * self.magic_scale_factor)

    def create_meta_arbor_depth_first(self,
                          root,
                          max_branching_order):

        # A list that will contain all the poly-lines gathered from traversing the arbor tree with
        # depth-first traversal
        poly_lines_data = list()

        # Construct the poly-lines
        nmv.skeleton.ops.get_connected_sections_poly_line_recursively(
            section=root, poly_lines_data=poly_lines_data, max_branching_level=max_branching_order)

        # For each poly-line in the list, draw it
        for poly_line_data in poly_lines_data:
            self.create_meta_poly_line(poly_line_data[0])



    ################################################################################################
    # @create_meta_arbor
    ################################################################################################
    def create_meta_arbor(self,
                          root,
                          max_branching_order):
        """Extrude the given arbor section by section recursively using meta objects.

        :param root:
            The root of a given section.
        :param max_branching_order:
            The maximum branching order set by the user to terminate the recursive call.
        """

        # Do not proceed if the branching order limit is hit
        if root.branching_order > max_branching_order:
            return

        # Create the section
        self.create_meta_section(root)

        # Create the children sections recursively
        for child in root.children:
            self.create_meta_arbor(child, max_branching_order)

    ################################################################################################
    # @build_arbors
    ################################################################################################
    def build_arbors(self):
        """Builds the arbors of the neuron as tubes and AT THE END converts them into meshes.
        If you convert them during the building, the scene is getting crowded and the process is
        getting exponentially slower.

        :return:
            A list of all the individual meshes of the arbors.
        """

        # Header
        nmv.logger.header('Building Arbors')

        # Draw the apical dendrite, if exists
        if not self.options.morphology.ignore_apical_dendrite:
            nmv.logger.info('Apical dendrite')

            # Create the apical dendrite mesh
            if self.morphology.apical_dendrite is not None:

                self.create_meta_arbor(
                    root=self.morphology.apical_dendrite,
                    max_branching_order=self.options.morphology.apical_dendrite_branch_order)

                #self.create_meta_arbor_depth_first(root=self.morphology.apical_dendrite,
                #    max_branching_order=self.options.morphology.apical_dendrite_branch_order)

                return
        # Draw the basal dendrites
        if not self.options.morphology.ignore_basal_dendrites:

            # Do it dendrite by dendrite
            for i, basal_dendrite in enumerate(self.morphology.dendrites):

                # Create the basal dendrite meshes
                nmv.logger.info('Dendrite [%d]' % i)
                self.create_meta_arbor(
                    root=basal_dendrite,
                    max_branching_order=self.options.morphology.basal_dendrites_branch_order)

        # Draw the axon as a set connected sections
        if not self.options.morphology.ignore_axon:
            nmv.logger.info('Axon')

            # Create the apical dendrite mesh
            if self.morphology.axon is not None:

                # Create the axon mesh
                self.create_meta_arbor(
                    root=self.morphology.axon,
                    max_branching_order=self.options.morphology.axon_branch_order)

    ################################################################################################
    # @initialize_meta_object
    ################################################################################################
    def initialize_meta_object(self,
                               name):
        """Constructs and initialize a new meta object that will be the basis of the mesh.

        :param name:
            Meta-object name.
        :return:
            A reference to the meta object
        """

        # Create a new meta skeleton that will be used to reconstruct the skeleton frame
        self.meta_skeleton = bpy.data.metaballs.new(name)

        # Create a new meta object that reflects the reconstructed mesh at the end of the operation
        self.meta_mesh = bpy.data.objects.new(name, self.meta_skeleton)

        # Get a reference to the scene
        scene = bpy.context.scene

        # Link the meta object to the scene
        scene.objects.link(self.meta_mesh)

        # Initial resolution of the meta skeleton, this will get updated later in the finalization
        self.meta_skeleton.resolution = 1.0

    ################################################################################################
    # @emanate_soma_towards_arbor
    ################################################################################################
    def emanate_soma_towards_arbor(self,
                                   arbor):
        """Extends the space of the soma towards the given arbor to make a shape that is not sphere.

        :param arbor:
            A given arbor to emanate the soma towards.
        """

        # Assume that from the soma center towards the first point along the arbor is a segment
        self.create_meta_segment(
            p1=self.morphology.soma.centroid,
            p2=arbor.samples[0].point,
            r1=self.morphology.soma.mean_radius,
            r2=arbor.samples[0].radius * self.magic_scale_factor)

    ################################################################################################
    # @build_soma_from_meta_objects
    ################################################################################################
    def build_soma_from_meta_objects(self):

        # Header
        nmv.logger.header('Building Soma from Meta Objects')

        # Emanate towards the apical dendrite, if exists
        if not self.options.morphology.ignore_apical_dendrite:
            nmv.logger.info('Apical dendrite')

            # The apical dendrite must be valid
            if self.morphology.apical_dendrite is not None:
                self.emanate_soma_towards_arbor(arbor=self.morphology.apical_dendrite)

        # Emanate towards basal dendrites
        if not self.options.morphology.ignore_basal_dendrites:

            # Do it dendrite by dendrite
            for i, basal_dendrite in enumerate(self.morphology.dendrites):

                # Basal dendrites
                nmv.logger.info('Dendrite [%d]' % i)
                self.emanate_soma_towards_arbor(arbor=basal_dendrite)

        # Emanate towards the axon, if exists
        if not self.options.morphology.ignore_apical_dendrite:
            nmv.logger.info('Axon')

            # The axon must be valid
            if self.morphology.axon is not None:
                self.emanate_soma_towards_arbor(arbor=self.morphology.axon)

    ################################################################################################
    # @finalize_meta_object
    ################################################################################################
    def finalize_meta_object(self):
        """Converts the meta object to a mesh and get it ready for export or visualization.

        :return:
        """

        # Header
        nmv.logger.header('Meshing the Meta Object')

        # Deselect all objects
        nmv.scene.ops.deselect_all()

        # Update the resolution
        self.meta_skeleton.resolution = self.smallest_radius

        # Select the mesh
        self.meta_mesh = bpy.context.scene.objects[self.morphology.label]
        self.meta_mesh.select = True

        bpy.context.scene.objects.active = self.meta_mesh

        # Convert it to a mesh from meta-balls
        bpy.ops.object.convert(target='MESH')

        self.meta_mesh = bpy.context.scene.objects[self.morphology.label + '.001']
        self.meta_mesh.name = self.morphology.label

        # Re-select it again to be able to perform post-processing operations in it
        self.meta_mesh.select = True

        bpy.context.scene.objects.active = self.meta_mesh

    ################################################################################################
    # @assign_material_to_mesh
    ################################################################################################
    def assign_material_to_mesh(self):

        # Deselect all objects
        nmv.scene.ops.deselect_all()

        # Activate the mesh object
        bpy.context.scene.objects.active = self.meta_mesh

        # Adjusting the texture space, before assigning the material
        bpy.context.object.data.use_auto_texspace = False
        bpy.context.object.data.texspace_size[0] = 5
        bpy.context.object.data.texspace_size[1] = 5
        bpy.context.object.data.texspace_size[2] = 5

        # Assign the material to the selected mesh
        nmv.shading.set_material_to_object(self.meta_mesh, self.soma_materials[0])

        # Activate the mesh object
        self.meta_mesh.select = True
        bpy.context.scene.objects.active = self.meta_mesh

    ################################################################################################
    # @reconstruct_mesh
    ################################################################################################
    def reconstruct_mesh(self):
        """Reconstructs the neuronal mesh using meta objects.
        """

        # Apply skeleton-based operation, if required, to slightly modify the skeleton
        nmv.builders.common.modify_morphology_skeleton(builder=self)

        # Initialize the meta object
        self.initialize_meta_object(name=self.options.morphology.label)

        # Build the soma
        self.build_soma_from_meta_objects()

        # Build the arbors
        self.build_arbors()

        # Finalize the meta object and construct a solid object
        self.finalize_meta_object()

        # NOTE: Before drawing the skeleton, create the materials once and for all to improve the
        # performance since this is way better than creating a new material per section or segment
        nmv.builders.common.create_skeleton_materials(builder=self)

        # Assign the material to the mesh
        self.assign_material_to_mesh()

        # Mission done
        nmv.logger.header('Done!')
