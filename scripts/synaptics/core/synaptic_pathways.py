####################################################################################################
# Copyright (c) 2020, EPFL / Blue Brain Project
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
import random
import os
import sys

# BBP imports
import bluepy
from bluepy.v2 import Circuit

# Blender imports
import bpy
from mathutils import Vector

# Internal imports
import nmv.builders
import nmv.geometry
import nmv.scene
import nmv.shading
import nmv.mesh
import nmv.enums
import nmv.options
import nmv.skeleton
import nmv.utilities

# Internal imports
import_paths = ['core']
for import_path in import_paths:
    sys.path.append(('%s/%s' % (os.path.dirname(os.path.realpath(__file__)), import_path)))

import circuit_data
import rendering


####################################################################################################
# @clear_lights
####################################################################################################
def clear_lights():
    """Clear all the lights in the scene.
    """

    # Iterate over all the objects in the scene, and remove the 'Cube', 'Lamp' and 'Camera' if exist
    for scene_object in bpy.context.scene.objects:

        # Object selection
        if 'LIGHT' == scene_object.type:
            nmv.scene.delete_object_in_scene(scene_object)


def clear_materials():

    # Select all the scene materials, unlink them and clear their data
    for scene_material in bpy.data.materials:
        bpy.data.materials.remove(scene_material, do_unlink=True)


####################################################################################################
# @create_neuron_mesh
####################################################################################################
def create_neuron_meshes_with_piecewise_builder(circuit,
                                                gid,
                                                with_axon=False):

    # Get the morphology file path from its GID
    # We must ensure that the GID is integer, that's why the cast is there
    h5_morphology_path = circuit.morph.get_filepath(gid)

    # Use the H5 morphology loader to load this file
    # Don't center the morphology, as it is assumed to be cleared and reviewed by the team
    h5_reader = nmv.file.H5Reader(h5_file=h5_morphology_path, center_morphology=False)
    morphology = h5_reader.read_file()

    # Adjust the label to be set according to the GID not the morphology label
    morphology.label = str(gid)

    # Create default NMV options
    nmv_options = nmv.options.NeuroMorphoVisOptions()
    if with_axon:
        nmv_options.morphology.axon_branch_order = 10000
    else:
        nmv_options.morphology.axon_branch_order = 1

    # Radii
    nmv_options.morphology.arbors_radii = nmv.enums.Skeleton.Radii.UNIFIED_PER_ARBOR_TYPE
    nmv_options.morphology.axon_samples_unified_radii_value = 1.0
    nmv_options.morphology.apical_dendrite_samples_unified_radii_value = 2.0
    nmv_options.morphology.basal_dendrites_samples_unified_radii_value = 2.0
    nmv_options.mesh.neuron_objects_connection = nmv.enums.Meshing.ObjectsConnection.DISCONNECTED
    nmv_options.mesh.soma_type = nmv.enums.Soma.Representation.META_BALLS

    # Create a meta balls meshing builder
    builder = nmv.builders.PiecewiseBuilder(morphology=morphology, options=nmv_options)

    # Create the neuron mesh
    builder.reconstruct_mesh()
    neuron_meshes = nmv.scene.get_list_of_meshes_in_scene()

    # Return a reference to the neuron mesh
    return neuron_meshes


####################################################################################################
# @create_neuron_mesh
####################################################################################################
def create_neuron_mesh(circuit,
                       gid,
                       with_axon=False):

    # Get the morphology file path from its GID
    # We must ensure that the GID is integer, that's why the cast is there
    h5_morphology_path = circuit.morph.get_filepath(gid)

    # Use the H5 morphology loader to load this file
    # Don't center the morphology, as it is assumed to be cleared and reviewed by the team
    h5_reader = nmv.file.H5Reader(h5_file=h5_morphology_path, center_morphology=False)
    morphology = h5_reader.read_file()

    # Adjust the label to be set according to the GID not the morphology label
    morphology.label = str(gid)

    # Create default NMV options
    nmv_options = nmv.options.NeuroMorphoVisOptions()
    if with_axon:
        nmv_options.morphology.axon_branch_order = 10000
    else:
        nmv_options.morphology.axon_branch_order = 1

    # Radii
    nmv_options.morphology.arbors_radii = nmv.enums.Skeleton.Radii.UNIFIED_PER_ARBOR_TYPE
    nmv_options.morphology.axon_samples_unified_radii_value = 1.0
    nmv_options.morphology.apical_dendrite_samples_unified_radii_value = 2.0
    nmv_options.morphology.basal_dendrites_samples_unified_radii_value = 2.0
    nmv_options.mesh.neuron_objects_connection = nmv.enums.Meshing.ObjectsConnection.DISCONNECTED
    nmv_options.mesh.soma_type = nmv.enums.Soma.Representation.META_BALLS

    # Create a meta balls meshing builder
    builder = nmv.builders.PiecewiseBuilder(morphology=morphology, options=nmv_options)

    # Create the neuron mesh
    builder.reconstruct_mesh()
    neuron_meshes = nmv.scene.get_list_of_meshes_in_scene()
    neuron_mesh = nmv.mesh.join_mesh_objects(mesh_list=neuron_meshes, name='neuron')
    neuron_mesh.name = str(gid)

    # material = nmv.shading.create_flat_material(color=color, name='%d' % gid)
    # nmv.shading.set_material_to_object(mesh_object=neuron_mesh, material_reference=material)

    # Return a reference to the neuron mesh
    return neuron_mesh



def create_neuron_meshes_with_skinning(circuit,
                                       gid,
                                       with_axon):
    # Get the morphology file path from its GID
    # We must ensure that the GID is integer, that's why the cast is there
    h5_morphology_path = circuit.morph.get_filepath(gid)

    # Use the H5 morphology loader to load this file
    # Don't center the morphology, as it is assumed to be cleared and reviewed by the team
    h5_reader = nmv.file.H5Reader(h5_file=h5_morphology_path, center_morphology=False)
    morphology = h5_reader.read_file()

    # Adjust the label to be set according to the GID not the morphology label
    morphology.label = str(gid)

    # Create default NMV options
    nmv_options = nmv.options.NeuroMorphoVisOptions()
    if with_axon:
        nmv_options.morphology.axon_branch_order = 10000
    else:
        nmv_options.morphology.axon_branch_order = 1

    # Radii
    nmv_options.morphology.arbors_radii = nmv.enums.Skeleton.Radii.UNIFIED_PER_ARBOR_TYPE
    nmv_options.morphology.axon_samples_unified_radii_value = 1.0
    nmv_options.morphology.apical_dendrite_samples_unified_radii_value = 2.0
    nmv_options.morphology.basal_dendrites_samples_unified_radii_value = 2.0
    nmv_options.mesh.neuron_objects_connection = nmv.enums.Meshing.ObjectsConnection.DISCONNECTED
    nmv_options.mesh.soma_type = nmv.enums.Soma.Representation.META_BALLS

    # Create a meta balls meshing builder
    builder = nmv.builders.SkinningBuilder(morphology=morphology, options=nmv_options)

    # Create the neuron mesh
    builder.reconstruct_mesh()
    neuron_meshes = nmv.scene.get_list_of_meshes_in_scene()

    return neuron_meshes


####################################################################################################
# @create_synapses_material
####################################################################################################
def create_synapses_material():
    # Load the material from the shaders gallery
    material = nmv.shading.create_principled_shader(name='synapse_material')
    node = material.node_tree.nodes["Principled BSDF"]

    # Set the parameters that were given by Caitlin
    node.inputs[0].default_value = (1.0, 0.6, 0, 1)
    node.inputs[3].default_value = (1.0, 0.6, 0, 1)
    node.inputs[10].default_value = 0.05
    node.inputs[13].default_value = 0
    node.inputs[17].default_value = (1.0, 0.6, 0, 1)

    # Return a reference to the material
    return material


####################################################################################################
# @create_shared_synapses_mesh
####################################################################################################
def create_shared_synapses_mesh(circuit,
                                pre_gid,
                                post_gid,
                                synapse_color,
                                synapse_size=4.0,
                                shader=nmv.enums.Shader.FLAT):

    material = create_synapses_material()

    # Get the IDs of the afferent synapses of a given GID
    afferent_synapses_ids = circuit.connectome.afferent_synapses(post_gid)

    # Get the GIDs of the pre-synaptic cells
    pre_gids = circuit.connectome.synapse_properties(
        afferent_synapses_ids, [bluepy.v2.enums.Synapse.PRE_GID]).values
    pre_gids = [gid[0] for gid in pre_gids]

    # A list that will contain all the synapse meshes
    synapse_objects = list()

    # Get the positions of the incoming synapses at the post synaptic side
    post_synaptic_positions = circuit.connectome.synapse_positions(
        afferent_synapses_ids, 'post', 'center').values.tolist()
    pre_synaptic_positions = circuit.connectome.synapse_positions(
        afferent_synapses_ids, 'pre', 'contour').values.tolist()

    # Do it for all the synapses
    for i in range(len(pre_gids)):

        # Get only the shared synapses with the pre-synaptic gid
        if pre_gid == int(pre_gids[i]):

            # Synapse position is the mid-way between the pre- and post-synaptic centers
            post_synaptic_position = Vector((post_synaptic_positions[i][0],
                                             post_synaptic_positions[i][1],
                                             post_synaptic_positions[i][2]))

            pre_synaptic_position = Vector((pre_synaptic_positions[i][0],
                                            pre_synaptic_positions[i][1],
                                            pre_synaptic_positions[i][2]))

            position = 0.5 * (post_synaptic_position + pre_synaptic_position)

            # A synapse sphere object
            synapse_sphere = nmv.geometry.create_ico_sphere(
                radius=synapse_size, location=position, subdivisions=3, name='synapse_%d' % i)

            # Add the sphere to the group
            synapse_objects.append(synapse_sphere)

            # Material
            nmv.shading.set_material_to_object(mesh_object=synapse_sphere,
                                               material_reference=material)

    # Join the meshes into a group
    synapse_group = nmv.mesh.join_mesh_objects(mesh_list=synapse_objects, name='synapses')

    return synapse_group


####################################################################################################
# @create_pre_synaptic_neuron_material
####################################################################################################
def create_pre_synaptic_neuron_material():

    # Load the material from the shaders gallery
    material = nmv.shading.create_principled_shader(name='pre_synaptic_material')
    node = material.node_tree.nodes["Principled BSDF"]

    # Set the parameters that were given by Caitlin
    node.inputs[0].default_value = (1, 0.319934, 0.110362, 1)
    node.inputs[3].default_value = (1, 0.616414, 0.310381, 1)
    node.inputs[10].default_value = 0.05
    node.inputs[13].default_value = 0

    # Return a reference to the material
    return material


####################################################################################################
# @create_post_synaptic_neuron_material
####################################################################################################
def create_post_synaptic_neuron_material():
    # Load the material from the shaders gallery
    material = nmv.shading.create_principled_shader(name='pre_synaptic_material')
    node = material.node_tree.nodes["Principled BSDF"]

    # Set the parameters that were given by Caitlin
    node.inputs[0].default_value = (0.37715, 0.427243, 1, 1)
    node.inputs[3].default_value = (0.163552, 0.423125, 1, 1)
    node.inputs[10].default_value = 0.05
    node.inputs[13].default_value = 0

    # Return a reference to the material
    return material


####################################################################################################
# @create_synaptic_pathway_scene
####################################################################################################
def create_synaptic_pathway_scene(circuit_config,
                                  pre_gid,
                                  post_gid,
                                  output_directory,
                                  synapses_color=Vector((255, 255, 0)),
                                  synapse_size=4.0,
                                  shader=nmv.enums.Shader.FLAT):
    # Loading a circuit
    circuit = Circuit(circuit_config)

    # Clear the scene
    nmv.scene.clear_scene()

    # Create the pre-synaptic mesh
    pre_mesh = create_neuron_mesh(circuit=circuit, gid=pre_gid, with_axon=True)

    # Adjust the transformation
    pre_transformation = circuit_data.get_cell_transformation(circuit, pre_gid)
    pre_mesh.matrix_world = pre_transformation

    # Clear all the lights
    clear_lights()

    # Export the scene into a blend file
    nmv.file.export_scene_to_blend_file(output_directory, str(pre_gid))

    # Clear the scene in Blender
    nmv.scene.clear_scene()

    # Create the post-synaptic mesh
    post_mesh = create_neuron_mesh(circuit=circuit, gid=post_gid)

    # Adjust the neuron transformation
    post_transformation = circuit_data.get_cell_transformation(circuit, post_gid)
    post_mesh.matrix_world = post_transformation

    # Clear all the lights
    clear_lights()

    # Export the scene into a blend file
    nmv.file.export_scene_to_blend_file(output_directory, str(post_gid))

    # For consistency, export the pair into a pre-pair blend file
    nmv.file.export_scene_to_blend_file(output_directory, '%d_%d' % (pre_gid, post_gid))

    # Clear the scene again
    nmv.scene.clear_scene()

    # Import both meshes
    nmv.file.import_object_from_blend_file(output_directory, str(pre_gid) + '.blend')
    nmv.file.import_object_from_blend_file(output_directory, str(post_gid) + '.blend')

    # Create the synapse material
    synapses_mesh = create_shared_synapses_mesh(circuit, pre_gid, post_gid,
                                                synapses_color, synapse_size, shader)

    # Select the pre-synaptic mesh to assign the material
    pre_synaptic_mesh = nmv.scene.get_object_by_name(str(pre_gid))
    pre_material = create_pre_synaptic_neuron_material()

    nmv.shading.set_material_to_object(mesh_object=pre_synaptic_mesh,
                                       material_reference=pre_material)

    # Select the post-synaptic mesh to assign the color
    post_synaptic_mesh = nmv.scene.get_object_by_name(str(post_gid))
    post_material = create_post_synaptic_neuron_material()
    nmv.shading.set_material_to_object(mesh_object=post_synaptic_mesh,
                                       material_reference=post_material)

    # Create sun light
    bpy.ops.object.light_add(type='SUN', radius=2.5, location=(0, 0, 0))

    # Save
    nmv.file.export_scene_to_blend_file(output_directory, str('All'))


####################################################################################################
# @create_synaptic_pathway_scene
####################################################################################################
def create_synaptic_pathway_scene_with_mesh_components(circuit_config,
                                                       pre_gid,
                                                       post_gid,
                                                       output_directory,
                                                       synapses_color=Vector((255, 255, 0)),
                                                       synapse_size=4.0,
                                                       shader=nmv.enums.Shader.FLAT):

    # Loading a circuit
    circuit = Circuit(circuit_config)

    # Clear the scene
    nmv.scene.clear_scene()

    pre_meshes_list = create_neuron_meshes_with_piecewise_builder(
        circuit=circuit, gid=pre_gid, with_axon=True)

    # Adjust the transformation
    pre_transformation = circuit_data.get_cell_transformation(circuit, pre_gid)
    for mesh in pre_meshes_list:
        mesh.matrix_world = pre_transformation

    # Clear all the lights
    clear_lights()

    # Clear all materials
    clear_materials()

    # Export the scene into a blend file
    nmv.file.export_scene_to_blend_file(output_directory, str(pre_gid))
    nmv.file.export_mesh_objects_to_file(mesh_objects=pre_meshes_list,
                                         output_directory=output_directory,
                                         output_file_name=str(pre_gid),
                                         file_format=nmv.enums.Meshing.ExportFormat.OBJ,
                                         export_individual_meshes=True)

    # Clear the scene in Blender
    nmv.scene.clear_scene()

    # Create the post-synaptic mesh
    post_meshes_list = create_neuron_meshes_with_piecewise_builder(circuit=circuit, gid=post_gid)

    # Adjust the neuron transformation
    post_transformation = circuit_data.get_cell_transformation(circuit, post_gid)
    for mesh in post_meshes_list:
        mesh.matrix_world = post_transformation

    # Clear all the lights
    clear_lights()

    # Clear all materials
    clear_materials()

    # Export the scene into a blend file
    nmv.file.export_scene_to_blend_file(output_directory, str(post_gid))
    nmv.file.export_mesh_objects_to_file(mesh_objects=post_meshes_list,
                                         output_directory=output_directory,
                                         output_file_name=str(post_gid),
                                         file_format=nmv.enums.Meshing.ExportFormat.OBJ,
                                         export_individual_meshes=True)

    # For consistency, export the pair into a pre-pair blend file
    nmv.file.export_scene_to_blend_file(output_directory, '%d_%d' % (pre_gid, post_gid))

    # Clear the scene again
    nmv.scene.clear_scene()

    # Import both meshes
    # nmv.file.import_object_from_blend_file(output_directory, str(pre_gid) + '.blend')
    # nmv.file.import_object_from_blend_file(output_directory, str(post_gid) + '.blend')

    # Create the synapse material
    synapses_mesh = create_shared_synapses_mesh(circuit, pre_gid, post_gid,
                                                synapses_color, synapse_size, shader)

    # Import the pre-synaptic meshes
    pre_synaptic_neuron_meshes_directory = '%s/%s' % (output_directory, str(pre_gid))
    pre_mesh_files = nmv.file.get_files_in_directory(directory=pre_synaptic_neuron_meshes_directory,
                                                     file_extension='obj')
    pre_meshes_list = list()
    for mesh_file in pre_mesh_files:
        pre_component = nmv.file.import_obj_file(
            input_directory=pre_synaptic_neuron_meshes_directory, input_file_name=mesh_file)
        pre_component.name = str(pre_gid) + '_' + pre_component.name
        pre_component.rotation_euler[0] = 0
        pre_meshes_list.append(pre_component)

    # Import the post-synaptic meshes
    post_synaptic_neuron_meshes_directory = '%s/%s' % (output_directory, str(post_gid))
    post_mesh_files = nmv.file.get_files_in_directory(
        directory=post_synaptic_neuron_meshes_directory,
        file_extension='obj')

    post_meshes_list = list()
    for mesh_file in post_mesh_files:
        post_component = nmv.file.import_obj_file(
            input_directory=post_synaptic_neuron_meshes_directory, input_file_name=mesh_file)
        post_component.name = str(post_gid) + '_' + post_component.name
        post_component.rotation_euler[0] = 0
        post_meshes_list.append(post_component)

    pre_material = create_pre_synaptic_neuron_material()
    for mesh_component in pre_meshes_list:
        nmv.shading.set_material_to_object(mesh_object=mesh_component,
                                           material_reference=pre_material)

    # Select the post-synaptic mesh to assign the color
    post_material = create_post_synaptic_neuron_material()
    for mesh_component in post_meshes_list:
        nmv.shading.set_material_to_object(mesh_object=mesh_component,
                                           material_reference=post_material)

    # Create sun light
    bpy.ops.object.light_add(type='SUN', radius=1.0, location=(0, 0, 0))

    # For consistency, export the pair into a pre-pair blend file
    nmv.file.export_scene_to_blend_file(output_directory, '%d_%d' % (pre_gid, post_gid))

    # Return a reference to the synapse mesh, for the close up rendering
    return synapses_mesh
