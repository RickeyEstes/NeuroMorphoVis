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

# Blender imports
import bpy
from bpy.props import EnumProperty
from bpy.props import IntProperty
from bpy.props import FloatProperty
from bpy.props import BoolProperty
from bpy.props import FloatVectorProperty
from mathutils import Vector

# Internal imports
import neuromorphovis as nmv
import neuromorphovis.bbox
import neuromorphovis.builders
import neuromorphovis.consts
import neuromorphovis.enums
import neuromorphovis.file
import neuromorphovis.interface
import neuromorphovis.shading
import neuromorphovis.scene
import neuromorphovis.skeleton
import neuromorphovis.rendering
import neuromorphovis.utilities


####################################################################################################
# @update_bounding_box_panel
####################################################################################################
def update_bounding_box_panel(current_scene, bbox):
    """Update the bounding box panel

    :param current_scene:
        Current scene.
    :param bbox:
        Bounding box.
    """

    # PMin
    current_scene.BBoxPMinX = bbox.p_min[0]
    current_scene.BBoxPMinY = bbox.p_min[1]
    current_scene.BBoxPMinZ = bbox.p_min[2]

    # PMax
    current_scene.BBoxPMaxX = bbox.p_max[0]
    current_scene.BBoxPMaxY = bbox.p_max[1]
    current_scene.BBoxPMaxZ = bbox.p_max[2]

    # Center
    current_scene.BBoxCenterX = bbox.center[0]
    current_scene.BBoxCenterY = bbox.center[1]
    current_scene.BBoxCenterZ = bbox.center[2]

    # Bounds
    current_scene.BoundsX = bbox.bounds[0]
    current_scene.BoundsY = bbox.bounds[1]
    current_scene.BoundsZ = bbox.bounds[2]


####################################################################################################
# @MorphologyPanel
####################################################################################################
class MorphologyPanel(bpy.types.Panel):
    """Morphology tools panel"""

    ################################################################################################
    # Panel parameters
    ################################################################################################
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Morphology Toolbox'
    bl_context = 'objectmode'
    bl_category = 'NeuroMorphoVis'

    ################################################################################################
    # Panel options
    ################################################################################################
    # Build soma
    bpy.types.Scene.BuildSoma = EnumProperty(
        items=[(nmv.enums.Soma.Representation.IGNORE,
                'Ignore',
                'Ignore soma reconstruction'),
               (nmv.enums.Soma.Representation.SPHERE,
                'Sphere',
                'Represent the soma by a sphere'),
               (nmv.enums.Soma.Representation.REALISTIC,
                'Profile',
                'Reconstruct a 3D profile of the soma')],
        name='Soma',
        default=nmv.enums.Soma.Representation.REALISTIC)

    # Build axon
    bpy.types.Scene.BuildAxon = BoolProperty(
        name="Build Axon",
        description="Select this flag to reconstruct the axon",
        default=True)

    # Axon branching order
    # Since the axon is so complicated, we will set its default branching order to 5
    bpy.types.Scene.AxonBranchingLevel = IntProperty(
        name="Branching Order",
        description="Branching order for the axon",
        default=100, min=1, max=5)

    # Build basal dendrites
    bpy.types.Scene.BuildBasalDendrites = BoolProperty(
        name="Build Basal Dendrites",
        description="Select this flag to reconstruct the basal dendrites",
        default=True)

    # Basal dendrites branching order
    bpy.types.Scene.BasalDendritesBranchingLevel = IntProperty(
        name="Branching Order",
        description="Branching order for the basal dendrites",
        default=100, min=1, max=100)

    # Build apical dendrite
    bpy.types.Scene.BuildApicalDendrite = BoolProperty(
        name="Build Apical Dendrites",
        description="Select this flag to reconstruct the apical dendrite (if exists)",
        default=True)

    # Apical dendrite branching order
    bpy.types.Scene.ApicalDendriteBranchingLevel = IntProperty(
        name="Branching Order",
        description="Branching order for the apical dendrite",
        default=100, min=1, max=100)

    # Draw bounding box
    bpy.types.Scene.DrawBoundingBox = BoolProperty(
        name="Draw Bounding Box",
        description="Draws the bounding box of the morphology",
        default=False)

    # Display bounding box info
    bpy.types.Scene.DisplayBoundingBox = BoolProperty(
        name="Display Bounding Box Info",
        description="Displays the bounding box of the morphology",
        default=False)

    # Bounding box data
    bpy.types.Scene.BBoxPMinX = FloatProperty(name="X", min=-1e10, max=1e10, subtype='FACTOR')
    bpy.types.Scene.BBoxPMinY = FloatProperty(name="Y", min=-1e10, max=1e10, subtype='FACTOR')
    bpy.types.Scene.BBoxPMinZ = FloatProperty(name="Z", min=-1e10, max=1e10, subtype='FACTOR')
    bpy.types.Scene.BBoxPMaxX = FloatProperty(name="X", min=-1e10, max=1e10, subtype='FACTOR')
    bpy.types.Scene.BBoxPMaxY = FloatProperty(name="Y", min=-1e10, max=1e10, subtype='FACTOR')
    bpy.types.Scene.BBoxPMaxZ = FloatProperty(name="Z", min=-1e10, max=1e10, subtype='FACTOR')
    bpy.types.Scene.BBoxCenterX = FloatProperty(name="X", min=-1e10, max=1e10, subtype='FACTOR')
    bpy.types.Scene.BBoxCenterY = FloatProperty(name="Y", min=-1e10, max=1e10, subtype='FACTOR')
    bpy.types.Scene.BBoxCenterZ = FloatProperty(name="Z", min=-1e10, max=1e10, subtype='FACTOR')
    bpy.types.Scene.BoundsX = FloatProperty(name="X", min=-1e10, max=1e10, subtype='FACTOR')
    bpy.types.Scene.BoundsY = FloatProperty(name="Y", min=-1e10, max=1e10, subtype='FACTOR')
    bpy.types.Scene.BoundsZ = FloatProperty(name="Z", min=-1e10, max=1e10, subtype='FACTOR')

    # Morphology material
    bpy.types.Scene.MorphologyMaterial = EnumProperty(
        items=nmv.enums.Shading.MATERIAL_ITEMS,
        name="Material",
        default=nmv.enums.Shading.FLAT)

    # Color arbor by part
    bpy.types.Scene.ColorArborByPart = BoolProperty(
        name="Color Arbor By Part",
        description="Each component of the arbor will be assigned a different color",
        default=False)

    # Color arbor using black and white alternatives
    bpy.types.Scene.ColorArborBlackAndWhite = BoolProperty(
        name="Black / White",
        description="Each component of the arbor will be assigned a either black or white",
        default=False)

    # Soma color
    bpy.types.Scene.SomaColor = FloatVectorProperty(
        name="Soma Color",
        subtype='COLOR', default=nmv.enums.Color.SOMA, min=0.0, max=1.0,
        description="The color of the reconstructed soma")

    # Axon color
    bpy.types.Scene.AxonColor = FloatVectorProperty(
        name="Axon Color",
        subtype='COLOR', default=nmv.enums.Color.AXONS, min=0.0, max=1.0,
        description="The color of the reconstructed axon")

    # Basal dendrites color
    bpy.types.Scene.BasalDendritesColor = FloatVectorProperty(
        name="Basal Dendrites  Color",
        subtype='COLOR', default=nmv.enums.Color.BASAL_DENDRITES, min=0.0, max=1.0,
        description="The color of the reconstructed basal dendrites")

    # Apical dendrite color
    bpy.types.Scene.ApicalDendriteColor = FloatVectorProperty(
        name="Apical Dendrite Color",
        subtype='COLOR', default=nmv.enums.Color.APICAL_DENDRITES, min=0.0, max=1.0,
        description="The color of the reconstructed apical dendrite")

    # Articulation color
    bpy.types.Scene.ArticulationColor = FloatVectorProperty(
        name="Articulation Color",
        subtype='COLOR', default=nmv.enums.Color.ARTICULATION, min=0.0, max=1.0,
        description="The color of the articulations in the Articulated Section mode")

    # Reconstruction method
    bpy.types.Scene.MorphologyReconstructionTechnique = EnumProperty(
        items=[(nmv.enums.Skeletonization.Method.DISCONNECTED_SKELETON_ORIGINAL,
                'Disconnected Skeleton (Original)',
                "The skeleton is disconnected at the branching points"),
               (nmv.enums.Skeletonization.Method.DISCONNECTED_SKELETON_REPAIRED,
                'Disconnected Skeleton (Resampled)',
                "The skeleton is disconnected at the branching points and resampled"),
               (nmv.enums.Skeletonization.Method.DISCONNECTED_SEGMENTS,
                'Disconnected Segments',
                "Each segment is an independent object (this approach is time consuming)"),
               (nmv.enums.Skeletonization.Method.DISCONNECTED_SECTIONS,
                'Disconnected Sections',
                "Each section is an independent object"),
               (nmv.enums.Skeletonization.Method.ARTICULATED_SECTIONS,
                'Articulated Sections',
                "Each section is an independent object, but connected with a pivot"),
               (nmv.enums.Skeletonization.Method.CONNECTED_SECTION_ORIGINAL,
                'Connected Sections (Original)',
                "The sections of a single arbor are connected together"),
               (nmv.enums.Skeletonization.Method.CONNECTED_SECTION_REPAIRED,
                'Connected Sections (Repaired)',
                "The morphology is repaired and fully reconstructed ")],
        name="Method",
        default=nmv.enums.Skeletonization.Method.CONNECTED_SECTION_REPAIRED)

    # Branching, is it based on angles or radii
    bpy.types.Scene.MorphologyBranching = EnumProperty(
        items=[(nmv.enums.Skeletonization.Branching.ANGLES,
                'Angles',
                'Make the branching based on the angles at branching points'),
               (nmv.enums.Skeletonization.Branching.RADII,
                'Radii',
                'Make the branching based on the radii of the children at the branching points')],
        name='Branching Style',
        default=nmv.enums.Skeletonization.Branching.ANGLES)

    # Connect to soma if the connected method is used
    bpy.types.Scene.ConnectToSoma = BoolProperty(
        name="Connect to Soma",
        description="Connect the arbors to the soma",
        default=True)

    # Arbor quality
    bpy.types.Scene.ArborQuality = IntProperty(
        name="Sides",
        description="Number of vertices of the cross-section of each segment along the arbor",
        default=16, min=4, max=128)

    # Section radius
    bpy.types.Scene.SectionsRadii = EnumProperty(
        items=[(nmv.enums.Skeletonization.ArborsRadii.AS_SPECIFIED,
                'As Specified in Morphology',
                "Use the cross-sectional radii reported in the morphology file"),
               (nmv.enums.Skeletonization.ArborsRadii.FIXED,
                'At a Fixed Diameter',
                "Set all the arbors to a fixed radius"),
               (nmv.enums.Skeletonization.ArborsRadii.SCALED,
                'With Scale Factor',
                "Scale all the arbors using a specified scale factor")],
        name="Sections Radii",
        default=nmv.enums.Skeletonization.ArborsRadii.AS_SPECIFIED)

    # Fixed section radius value
    bpy.types.Scene.FixedRadiusValue = FloatProperty(
        name="Value (micron)",
        description="The value of the radius in microns between (0.05 and 5.0) microns",
        default=1.0, min=0.05, max=5.0)

    # Global radius scale value
    bpy.types.Scene.RadiusScaleValue= FloatProperty(
        name="Scale",
        description="A scale factor for scaling the radii of the arbors between (0.01 and 5.0)",
        default=1.0, min=0.01, max=5.0)

    # Rendering type
    bpy.types.Scene.RenderingType= EnumProperty(
        items=[(nmv.enums.Skeletonization.Rendering.Resolution.FIXED_RESOLUTION,
                'Fixed Resolution',
                'Renders a full view of the morphology at a specified resolution'),
               (nmv.enums.Skeletonization.Rendering.Resolution.TO_SCALE,
                'To Scale',
                'Renders an image of the full view at the right scale in (um)')],
        name='Type',
        default=nmv.enums.Skeletonization.Rendering.Resolution.FIXED_RESOLUTION)

    # Rendering view
    bpy.types.Scene.RenderingView = EnumProperty(
        items=[(nmv.enums.Skeletonization.Rendering.View.CLOSE_UP_VIEW,
                'Close Up',
                'Renders a close up image the focuses on the soma'),
               (nmv.enums.Skeletonization.Rendering.View.WIDE_SHOT_VIEW,
                'Full View',
                'Renders an image of the full view')],
        name='View', default=nmv.enums.Skeletonization.Rendering.View.WIDE_SHOT_VIEW)

    """
    # Rendering extent
    bpy.types.Scene.RenderingExtent = EnumProperty(
        items=[(nmv.enums.Skeletonization.Rendering.FULL_MORPHOLOGY_EXTENT,
                'Whole Morphology',
                'Renders a view that considers all the morphology components'),
               (nmv.enums.Skeletonization.Rendering.SELECTED_ARBROS_EXTENT,
                'Selected Arbors',
                'Renders a view that considers only the selected arbors')],
        name='Extent',
        default=nmv.enums.Skeletonization.Rendering.FULL_MORPHOLOGY_EXTENT)
    """
    # Frame resolution
    bpy.types.Scene.MorphologyFrameResolution = IntProperty(
        name="Resolution", default=512, min=128, max=1024 * 10,
        description="The resolution of the image generated from rendering the morphology")

    # Frame scale factor 'for rendering to scale option '
    bpy.types.Scene.MorphologyFrameScaleFactor = FloatProperty(
        name="Scale", default=1.0, min=1.0, max=100.0,
        description="The scale factor for rendering a morphology to scale")

    # Morphology close up dimensions
    bpy.types.Scene.MorphologyCloseUpDimensions = FloatProperty(
        name="Dimensions",
        default=20, min=5, max=100,
        description="The dimensions of the view that will be rendered in microns")

    ################################################################################################
    # @draw
    ################################################################################################
    def draw(self, context):
        """
        Draws the panel.

        :param context: Panel context.
        """

        # Get a reference to the layout of the panel
        layout = self.layout

        # Get a reference to the scene
        current_scene = context.scene

        # Morphology skeleton options
        skeleton_row = layout.row()
        skeleton_row.label(text='Morphology Skeleton:', icon='POSE_DATA')

        # Build soma options
        build_soma_row = layout.row()
        build_soma_row.label('Soma:')
        build_soma_row.prop(current_scene, 'BuildSoma', expand=True)

        # Pass options from UI to system
        nmv.interface.ui_options.morphology.soma_representation = current_scene.BuildSoma

        # Build axon options
        axon_row = layout.row()
        axon_row.prop(current_scene, 'BuildAxon')
        axon_level_row = axon_row.column()
        axon_level_row.prop(current_scene, 'AxonBranchingLevel')
        if not current_scene.BuildAxon:
            axon_level_row.enabled = False
        else:
            axon_level_row.enabled = True

        # Pass options from UI to system
        nmv.interface.ui_options.morphology.ignore_axon = not current_scene.BuildAxon
        nmv.interface.ui_options.morphology.axon_branch_order = current_scene.AxonBranchingLevel

        # Build basal dendrites options
        basal_dendrites_row = layout.row()
        basal_dendrites_row.prop(current_scene, 'BuildBasalDendrites')
        basal_dendrites_level_row = basal_dendrites_row.column()
        basal_dendrites_level_row.prop(current_scene, 'BasalDendritesBranchingLevel')
        if not current_scene.BuildBasalDendrites:
            basal_dendrites_level_row.enabled = False
        else:
            basal_dendrites_level_row.enabled = True

        # Pass options from UI to system
        nmv.interface.ui_options.morphology.ignore_basal_dendrites = not current_scene.BuildBasalDendrites
        nmv.interface.ui_options.morphology.basal_dendrites_branch_order = \
            current_scene.BasalDendritesBranchingLevel

        # Build apical dendrite option
        apical_dendrite_row = layout.row()
        apical_dendrite_row.prop(current_scene, 'BuildApicalDendrite')
        apical_dendrite_level_row = apical_dendrite_row.column()
        apical_dendrite_level_row.prop(current_scene, 'ApicalDendriteBranchingLevel')
        if not current_scene.BuildApicalDendrite:
            apical_dendrite_level_row.enabled = False
        else:
            apical_dendrite_level_row.enabled = True

        # Pass options from UI to system
        nmv.interface.ui_options.morphology.ignore_apical_dendrite = \
            not current_scene.BuildApicalDendrite
        nmv.interface.ui_options.morphology.apical_dendrite_branch_order = \
            current_scene.ApicalDendriteBranchingLevel

        # Bounding box options
        bounding_box_row = layout.row()
        bounding_box_row.label(text='Morphology Bounding Box:', icon='BORDER_RECT')

        # Draw bounding box option
        draw_bounding_box_row = layout.row()
        draw_bounding_box_row.prop(current_scene, 'DrawBoundingBox')

        # Display bounding box option
        display_bounding_box_row = layout.row()
        display_bounding_box_row.prop(current_scene, 'DisplayBoundingBox')

        # if globals.objects.loaded_morphology_object is not None:
        # TODO: Fix globals
        if current_scene.DisplayBoundingBox:
            bounding_box_p_row = layout.row()
            bounding_box_p_min_row = bounding_box_p_row.column(align=True)
            bounding_box_p_min_row.label(text='PMin:')
            bounding_box_p_min_row.prop(current_scene, 'BBoxPMinX')
            bounding_box_p_min_row.prop(current_scene, 'BBoxPMinY')
            bounding_box_p_min_row.prop(current_scene, 'BBoxPMinZ')
            bounding_box_p_min_row.enabled = False

            bounding_box_p_max_row = bounding_box_p_row.column(align=True)
            bounding_box_p_max_row.label(text='PMax:')
            bounding_box_p_max_row.prop(current_scene, 'BBoxPMaxX')
            bounding_box_p_max_row.prop(current_scene, 'BBoxPMaxY')
            bounding_box_p_max_row.prop(current_scene, 'BBoxPMaxZ')
            bounding_box_p_max_row.enabled = False

            bounding_box_data_row = layout.row()
            bounding_box_center_row = bounding_box_data_row.column(align=True)
            bounding_box_center_row.label(text='Center:')
            bounding_box_center_row.prop(current_scene, 'BBoxCenterX')
            bounding_box_center_row.prop(current_scene, 'BBoxCenterY')
            bounding_box_center_row.prop(current_scene, 'BBoxCenterZ')
            bounding_box_center_row.enabled = False

            bounding_box_bounds_row = bounding_box_data_row.column(align=True)
            bounding_box_bounds_row.label(text='Bounds:')
            bounding_box_bounds_row.prop(current_scene, 'BoundsX')
            bounding_box_bounds_row.prop(current_scene, 'BoundsY')
            bounding_box_bounds_row.prop(current_scene, 'BoundsZ')
            bounding_box_bounds_row.enabled = False

        # Reconstruction options
        reconstruction_options_row = layout.row()
        reconstruction_options_row.label(text='Reconstruction Options:', icon='OUTLINER_OB_EMPTY')

        # Morphology reconstruction techniques option
        morphology_reconstruction_row = layout.row()
        morphology_reconstruction_row.prop(
            current_scene, 'MorphologyReconstructionTechnique', icon='FORCE_CURVE')

        # Pass options from UI to system
        nmv.interface.ui_options.morphology.reconstruction_method = \
            current_scene.MorphologyReconstructionTechnique

        # Reconstruction technique
        technique = current_scene.MorphologyReconstructionTechnique
        if technique == nmv.enums.Skeletonization.Method.CONNECTED_SECTION_REPAIRED \
            or technique == nmv.enums.Skeletonization.Method.CONNECTED_SECTION_ORIGINAL \
            or technique == nmv.enums.Skeletonization.Method.DISCONNECTED_SKELETON_REPAIRED \
            or technique == nmv.enums.Skeletonization.Method.DISCONNECTED_SKELETON_ORIGINAL:

            # Morphology branching
            branching_row = layout.row()
            branching_row.label('Branching:')
            branching_row.prop(current_scene, 'MorphologyBranching', expand=True)

            # Pass options from UI to system
            nmv.interface.ui_options.morphology.branching = current_scene.MorphologyBranching

            connect_to_soma_row = layout.row()
            connect_to_soma_row.prop(current_scene, 'ConnectToSoma')

            # Pass options from UI to system
            nmv.interface.ui_options.morphology.connect_to_soma = current_scene.ConnectToSoma

        # Arbor quality option
        arbor_quality_row = layout.row()
        arbor_quality_row.label(text='Arbor Quality:')
        arbor_quality_row.prop(current_scene, 'ArborQuality')

        # Pass options from UI to system
        nmv.interface.ui_options.morphology.bevel_object_sides = current_scene.ArborQuality

        # Sections diameters option
        sections_radii_row = layout.row()
        sections_radii_row.prop(current_scene, 'SectionsRadii', icon='SURFACE_NCURVE')

        # Radii as specified in the morphology file
        if current_scene.SectionsRadii == nmv.enums.Skeletonization.ArborsRadii.AS_SPECIFIED:

            # Pass options from UI to system
            nmv.interface.ui_options.morphology.scale_sections_radii = False
            nmv.interface.ui_options.morphology.unify_sections_radii = False
            nmv.interface.ui_options.morphology.sections_radii_scale = 1.0

        # Fixed diameter
        elif current_scene.SectionsRadii == nmv.enums.Skeletonization.ArborsRadii.FIXED:

            fixed_diameter_row = layout.row()
            fixed_diameter_row.label(text='Fixed Radius Value:')
            fixed_diameter_row.prop(current_scene, 'FixedRadiusValue')

            # Pass options from UI to system
            nmv.interface.ui_options.morphology.scale_sections_radii = False
            nmv.interface.ui_options.morphology.unify_sections_radii = True
            nmv.interface.ui_options.morphology.sections_fixed_radii_value = current_scene.FixedRadiusValue

        # Scaled diameter
        elif current_scene.SectionsRadii == nmv.enums.Skeletonization.ArborsRadii.SCALED:

            scaled_diameter_row = layout.row()
            scaled_diameter_row.label(text='Radius Scale Factor:')
            scaled_diameter_row.prop(current_scene, 'RadiusScaleValue')

            # Pass options from UI to system
            nmv.interface.ui_options.morphology.unify_sections_radii = False
            nmv.interface.ui_options.morphology.scale_sections_radii = True
            nmv.interface.ui_options.morphology.sections_radii_scale = current_scene.RadiusScaleValue

        else:
            nmv.logger.log('ERROR')

        # Color parameters
        arbors_colors_row = layout.row()
        arbors_colors_row.label(text='Morphology Colors:', icon='COLOR')

        # Morphology material
        morphology_material_row = layout.row()
        morphology_material_row.prop(current_scene, 'MorphologyMaterial')

        # Pass options from UI to system
        nmv.interface.ui_options.morphology.material = current_scene.MorphologyMaterial

        color_by_part_row = layout.row()
        color_by_part_row.prop(current_scene, 'ColorArborByPart')
        color_bw_row = color_by_part_row.column()
        color_bw_row.prop(current_scene, 'ColorArborBlackAndWhite')
        color_bw_row.enabled = False

        # Soma color option
        soma_color_row = layout.row()
        soma_color_row.prop(current_scene, 'SomaColor')
        if not current_scene.BuildSoma:
            soma_color_row.enabled = False

        # Pass options from UI to system
        soma_color_value = Vector((current_scene.SomaColor.r, current_scene.SomaColor.g, current_scene.SomaColor.b))
        nmv.interface.ui_options.morphology.soma_color = soma_color_value

        # Axon color option
        axon_color_row = layout.row()
        axon_color_row.prop(current_scene, 'AxonColor')
        if not current_scene.BuildAxon or current_scene.ColorArborByPart:
            axon_color_row.enabled = False

        # Pass options from UI to system
        axon_color_value = Vector((current_scene.AxonColor.r, current_scene.AxonColor.g, current_scene.AxonColor.b))
        nmv.interface.ui_options.morphology.axon_color = axon_color_value

        # Basal dendrites color option
        basal_dendrites_color_row = layout.row()
        basal_dendrites_color_row.prop(current_scene, 'BasalDendritesColor')
        if not current_scene.BuildBasalDendrites or current_scene.ColorArborByPart:
            basal_dendrites_color_row.enabled = False

        # Pass options from UI to system
        color = current_scene.BasalDendritesColor
        basal_dendrites_color_value = Vector((color.r, color.g, color.b))
        nmv.interface.ui_options.morphology.basal_dendrites_color = basal_dendrites_color_value

        # Apical dendrite color option
        apical_dendrites_color_row = layout.row()
        apical_dendrites_color_row.prop(current_scene, 'ApicalDendriteColor')
        if not current_scene.BuildApicalDendrite or current_scene.ColorArborByPart:
            apical_dendrites_color_row.enabled = False

        # Pass options from UI to system
        color = current_scene.ApicalDendriteColor
        apical_dendrites_color_value = Vector((color.r, color.g, color.b))
        nmv.interface.ui_options.morphology.apical_dendrites_color = apical_dendrites_color_value

        # Articulation color option
        technique = current_scene.MorphologyReconstructionTechnique
        if technique == nmv.enums.Skeletonization.Method.ARTICULATED_SECTIONS:
            articulation_color_row = layout.row()
            articulation_color_row.prop(current_scene, 'ArticulationColor')

            # Pass options from UI to system
            color = current_scene.ArticulationColor
            articulation_color_value = Vector((color.r, color.g, color.b))
            nmv.interface.ui_options.morphology.articulation_color = articulation_color_value

        if current_scene.ColorArborByPart:
            nmv.interface.ui_options.morphology.axon_color = Vector((-1, 0, 0))
            nmv.interface.ui_options.morphology.basal_dendrites_color = Vector((-1, 0, 0))
            nmv.interface.ui_options.morphology.apical_dendrites_color = Vector((-1, 0, 0))
            color_bw_row.enabled = True

            if current_scene.ColorArborBlackAndWhite:
                nmv.interface.ui_options.morphology.axon_color = Vector((0, -1, 0))
                nmv.interface.ui_options.morphology.basal_dendrites_color = Vector((0, -1, 0))
                nmv.interface.ui_options.morphology.apical_dendrites_color = Vector((0, -1, 0))

        # Morphology quick reconstruction options
        quick_reconstruction_row = layout.row()
        quick_reconstruction_row.label(text='Quick Reconstruction:', icon='PARTICLE_POINT')

        # Morphology reconstruction button
        reconstruct_morphology_button_row = layout.row()
        reconstruct_morphology_button_row.operator('reconstruct.morphology', icon='RNA_ADD')
        #if current_scene.InputSource == 'h5_swc_file' or current_scene.InputSource ==
        # 'circuit_gid':
        reconstruct_morphology_button_row.enabled = True
        #else:
        #    reconstruct_morphology_button_row.enabled = False

        # Quick rendering options
        quick_rendering_row = layout.row()
        quick_rendering_row.label(text='Quick Rendering Options:', icon='RENDER_STILL')

        # Rendering view
        rendering_view_row = layout.row()
        rendering_view_row.prop(current_scene, 'RenderingView', expand=True)

        # Close up view
        if current_scene.RenderingView == nmv.enums.Skeletonization.Rendering.View.CLOSE_UP_VIEW:

            # Rendering close up option
            render_close_up_row = layout.row()
            render_close_up_row.prop(current_scene, 'MorphologyCloseUpDimensions')

            # Frame resolution option
            frame_resolution_row = layout.row()
            frame_resolution_row.label(text='Frame Resolution:')
            frame_resolution_row.prop(current_scene, 'MorphologyFrameResolution')
            frame_resolution_row.enabled = True

        # Full morphology view
        else:

            # Rendering type
            rendering_type_row = layout.row()
            rendering_type_row.prop(current_scene, 'RenderingType', expand=True)

            # Rendering extent
            #rendering_extent_row = layout.row()
            #rendering_extent_row.prop(current_scene, 'RenderingExtent', expand=True)

            # Extent option
            #nmv.interface.ui_options.morphology.rendering_extent = current_scene.RenderingExtent

            # Render a frame using a user-defined base resolution
            if current_scene.RenderingType == \
                    nmv.enums.Skeletonization.Rendering.Resolution.FIXED_RESOLUTION:

                # Frame resolution option
                frame_resolution_row = layout.row()
                frame_resolution_row.label(text='Frame Resolution:')
                frame_resolution_row.prop(current_scene, 'MorphologyFrameResolution')
                frame_resolution_row.enabled = True

            # To scale
            else:

                # Scale factor option
                scale_factor_row = layout.row()
                scale_factor_row.label(text='Resolution Scale:')
                scale_factor_row.prop(current_scene, 'MorphologyFrameScaleFactor')
                scale_factor_row.enabled = True

        # Render view buttons
        render_view_row = layout.row()
        render_view_row.label(text='Render View:', icon='RESTRICT_RENDER_OFF')
        render_view_buttons_row = layout.row(align=True)
        render_view_buttons_row.operator('render_morphology.front', icon='AXIS_FRONT')
        render_view_buttons_row.operator('render_morphology.side', icon='AXIS_SIDE')
        render_view_buttons_row.operator('render_morphology.top', icon='AXIS_TOP')
        render_view_buttons_row.enabled = True

        # Render animations buttons
        render_animation_row = layout.row()
        render_animation_row.label(text='Render Animation:', icon='CAMERA_DATA')
        render_animations_buttons_row = layout.row(align=True)
        render_animations_buttons_row.operator('render_morphology.360', icon='FORCE_MAGNETIC')
        render_animations_buttons_row.operator('render_morphology.progressive', icon='FORCE_HARMONIC')
        render_animations_buttons_row.enabled = True

        # Saving morphology options
        save_morphology_row = layout.row()
        save_morphology_row.label(text='Save Morphology As:', icon='MESH_UVSPHERE')

        # Saving morphology buttons
        save_morphology_buttons_column = layout.column(align=True)
        save_morphology_buttons_column.operator('save_morphology.blend', icon='OUTLINER_OB_META')
        save_morphology_buttons_column.enabled = True


####################################################################################################
# ReconstructMorphologyOperator
####################################################################################################
class ReconstructMorphologyOperator(bpy.types.Operator):
    """Morphology reconstruction operator"""

    # Operator parameters
    bl_idname = "reconstruct.morphology"
    bl_label = "Reconstruct Morphology"

    ################################################################################################
    # @load_morphology
    ################################################################################################
    def load_morphology(self, current_scene):
        """
        Loads the morphology from file.

        :param current_scene: Scene.
        """

        # Read the data from a given morphology file either in .h5 or .swc formats
        if bpy.context.scene.InputSource == nmv.enums.Input.H5_SWC_FILE:

            # Pass options from UI to system
            nmv.interface.ui_options.morphology.morphology_file_path = current_scene.MorphologyFile

            # Update the morphology label
            nmv.interface.ui_options.morphology.label = nmv.file.ops.get_file_name_from_path(
                current_scene.MorphologyFile)

            # Load the morphology from the file
            loading_flag, morphology_object = nmv.file.readers.read_morphology_from_file(
                options=nmv.interface.ui_options)

            # Verify the loading operation
            if loading_flag:

                # Update the morphology
                nmv.interface.ui_morphology = morphology_object

            # Otherwise, report an ERROR
            else:
                self.report({'ERROR'}, 'Invalid Morphology File')

        # Read the data from a specific gid in a given circuit
        elif bpy.context.scene.InputSource == nmv.enums.Input.CIRCUIT_GID:

            # Pass options from UI to system
            nmv.interface.ui_options.morphology.blue_config = current_scene.CircuitFile
            nmv.interface.ui_options.morphology.gid = current_scene.Gid

            # Update the morphology label
            nmv.interface.ui_options.morphology.label = 'neuron_' + str(current_scene.Gid)

            # Load the morphology from the circuit
            loading_flag, morphology_object = \
                nmv.file.readers.BBPReader.load_morphology_from_circuit(
                    blue_config=nmv.interface.ui_options.morphology.blue_config,
                    gid=nmv.interface.ui_options.morphology.gid)

            # Verify the loading operation
            if loading_flag:

                # Update the morphology
                nmv.interface.ui_morphology = morphology_object

            # Otherwise, report an ERROR
            else:

                self.report({'ERROR'}, 'Cannot Load Morphology from Circuit')

        else:

            # Report an invalid input source
            self.report({'ERROR'}, 'Invalid Input Source')

    ################################################################################################
    # @load_morphology
    ################################################################################################
    def execute(self,
                context):
        """
        Execute the operator.

        :param context: Context.
        :return: 'FINISHED'
        """

        # Clear the scene
        nmv.scene.ops.clear_scene()

        # Load the morphology
        self.load_morphology(current_scene=context.scene)

        # Create a skeletonizer object to build the morphology skeleton
        builder = nmv.builders.SkeletonBuilder(nmv.interface.ui_morphology, nmv.interface.ui_options)

        # Draw the morphology skeleton and return a list of all the reconstructed objects
        nmv.interface.ui_reconstructed_skeleton = builder.draw_morphology_skeleton()

        # Draw the bounding box of the morphology
        # if scene.DrawBoundingBox:
        #    bounding_box.draw_bounding_box(globals.objects.loaded_morphology_object.bounding_box,
        #                                   name='morphology_bounding_box')


        # Confirm operation done
        return {'FINISHED'}


####################################################################################################
# @RenderMorphologyFront
####################################################################################################
class RenderMorphologyFront(bpy.types.Operator):
    """Render front view of the reconstructed morphology"""

    # Operator parameters
    bl_idname = "render_morphology.front"
    bl_label = "Front"

    ################################################################################################
    # @execute
    ################################################################################################
    def execute(self,
                context):
        """Execute the operator.

        :param context:
            Rendering Context.
        :return:
            'FINISHED'.
        """

        # Ensure that there is a valid directory where the images will be written to
        if nmv.interface.ui_options.io.output_directory is None:
            self.report({'ERROR'}, nmv.consts.Messages.PATH_NOT_SET)
            return {'FINISHED'}

        if not nmv.file.ops.path_exists(context.scene.OutputDirectory):
            self.report({'ERROR'}, nmv.consts.Messages.INVALID_OUTPUT_PATH)
            return {'FINISHED'}

        # Create the images directory if it does not exist
        if not nmv.file.ops.path_exists(nmv.interface.ui_options.io.images_directory):
            nmv.file.ops.clean_and_create_directory(nmv.interface.ui_options.io.images_directory)

        # Report the process starting in the UI
        self.report({'INFO'}, 'Morphology Rendering ... Wait')

        # A reference to the bounding box that will be used for the rendering
        bounding_box = None

        # Rendering a close up view
        if context.scene.RenderingView == nmv.enums.Skeletonization.Rendering.View.CLOSE_UP_VIEW:

            # Compute the bounding box for a close up view
            bounding_box = nmv.bbox.compute_unified_extent_bounding_box(
                extent=context.scene.MorphologyCloseUpDimensions)

        # Render the whole morphology view
        elif context.scene.RenderingView == nmv.enums.Skeletonization.Rendering.View.WIDE_SHOT_VIEW:
            pass
            """
            if context.scene.RenderingExtent == \
                    nmv.enums.Skeletonization.Rendering.FULL_MORPHOLOGY_EXTENT:

                # Compute the full morphology bounding box
                bounding_box = nmv.skeleton.compute_full_morphology_bounding_box(
                    morphology=nmv.interface.ui_morphology)

            elif context.scene.RenderingExtent == \
                    nmv.enums.Skeletonization.Rendering.SELECTED_ARBROS_EXTENT:

                # Compute the bounding box for the available curves only
                bounding_box = nmv.bbox.compute_scene_bounding_box_for_curves()

            else:
                self.report({'ERROR'}, 'Invalid Rendering Extent')
                return {'FINISHED'}
            """
        nmv.rendering.NeuronSkeletonRenderer.render(
            bounding_box=bounding_box,
            camera_view=nmv.enums.Camera.View.FRONT,
            image_resolution=context.scene.MorphologyFrameResolution,
            image_name='MORPHOLOGY_FRONT_%s' % nmv.interface.ui_options.morphology.label,
            image_directory=nmv.interface.ui_options.io.images_directory,
            keep_camera_in_scene=context.scene.KeepSomaCameras)

        # Report the process termination in the UI
        self.report({'INFO'}, 'Rendering Morphology Done')

        # Confirm operation done
        return {'FINISHED'}


####################################################################################################
# @RenderMorphologySide
####################################################################################################
class RenderMorphologySide(bpy.types.Operator):
    """Render side view of the reconstructed morphology"""

    # Operator parameters
    bl_idname = "render_morphology.side"
    bl_label = "Side"

    ################################################################################################
    # @execute
    ################################################################################################
    def execute(self, context):
        """Execute the operator.

        :param context:
            Rendering context.
        :return:
            'FINISHED'.
        """

        # Ensure that there is a valid directory where the images will be written to
        if nmv.interface.ui_options.io.output_directory is None:
            self.report({'ERROR'}, nmv.consts.Messages.PATH_NOT_SET)
            return {'FINISHED'}

        if not nmv.file.ops.path_exists(context.scene.OutputDirectory):
            self.report({'ERROR'}, nmv.consts.Messages.INVALID_OUTPUT_PATH)
            return {'FINISHED'}

        # Create the images directory if it does not exist
        if not nmv.file.ops.path_exists(nmv.interface.ui_options.io.images_directory):
            nmv.file.ops.clean_and_create_directory(nmv.interface.ui_options.io.images_directory)

        # Report the process starting in the UI
        self.report({'INFO'}, 'Morphology Rendering ... Wait')

        # A reference to the bounding box that will be used for the rendering
        bounding_box = None
        """
        # Rendering a close up view
        if context.scene.RenderingView == nmv.enums.Skeletonization.Rendering.CLOSE_UP_VIEW:

            # Compute the bounding box for a close up view
            bounding_box = nmv.bbox.compute_unified_extent_bounding_box(
                extent=context.scene.MorphologyCloseUpDimensions)

        # Render the whole morphology view
        elif context.scene.RenderingView == nmv.enums.Skeletonization.Rendering.FULL_VIEW:

            if context.scene.RenderingExtent == \
                    nmv.enums.Skeletonization.Rendering.FULL_MORPHOLOGY_EXTENT:

                # Compute the full morphology bounding box
                bounding_box = nmv.skeleton.compute_full_morphology_bounding_box(
                    morphology=nmv.interface.ui_morphology)

            elif context.scene.RenderingExtent == \
                    nmv.enums.Skeletonization.Rendering.SELECTED_ARBROS_EXTENT:

                # Compute the bounding box for the available curves only
                bounding_box = nmv.bbox.compute_scene_bounding_box_for_curves()

            else:
                self.report({'ERROR'}, 'Invalid Rendering Extent')
                return {'FINISHED'}
        """
        nmv.rendering.NeuronSkeletonRenderer.render(
            bounding_box=bounding_box,
            camera_view=nmv.enums.Camera.View.SIDE,
            image_resolution=context.scene.MorphologyFrameResolution,
            image_name='MORPHOLOGY_SIDE_%s' % nmv.interface.ui_options.morphology.label,
            image_directory=nmv.interface.ui_options.io.images_directory,
            keep_camera_in_scene=context.scene.KeepSomaCameras)

        # Report the process termination in the UI
        self.report({'INFO'}, 'Rendering Morphology Done')

        # Confirm operation done
        return {'FINISHED'}


####################################################################################################
# @RenderMorphologyTop
####################################################################################################
class RenderMorphologyTop(bpy.types.Operator):
    """Render top view of the reconstructed morphology"""

    # Operator parameters
    bl_idname = "render_morphology.top"
    bl_label = "Top"

    ################################################################################################
    # @execute
    ################################################################################################
    def execute(self, context):
        """Execute the operator.

        :param context:
            Rendering context.
        :return:
            'FINISHED'.
        """

        # Ensure that there is a valid directory where the images will be written to
        if nmv.interface.ui_options.io.output_directory is None:
            self.report({'ERROR'}, nmv.consts.Messages.PATH_NOT_SET)
            return {'FINISHED'}

        if not nmv.file.ops.path_exists(context.scene.OutputDirectory):
            self.report({'ERROR'}, nmv.consts.Messages.INVALID_OUTPUT_PATH)
            return {'FINISHED'}

        # Create the images directory if it does not exist
        if not nmv.file.ops.path_exists(nmv.interface.ui_options.io.images_directory):
            nmv.file.ops.clean_and_create_directory(nmv.interface.ui_options.io.images_directory)

        # Report the process starting in the UI
        self.report({'INFO'}, 'Morphology Rendering ... Wait')

        # A reference to the bounding box that will be used for the rendering
        bounding_box = None
        """
        # Rendering a close up view
        if context.scene.RenderingView == nmv.enums.Skeletonization.Rendering.CLOSE_UP_VIEW:

            # Compute the bounding box for a close up view
            bounding_box = nmv.bbox.compute_unified_extent_bounding_box(
                extent=context.scene.MorphologyCloseUpDimensions)

        # Render the whole morphology view
        elif context.scene.RenderingView == nmv.enums.Skeletonization.Rendering.FULL_VIEW:

            if context.scene.RenderingExtent == \
                    nmv.enums.Skeletonization.Rendering.FULL_MORPHOLOGY_EXTENT:

                # Compute the full morphology bounding box
                bounding_box = nmv.skeleton.compute_full_morphology_bounding_box(
                    morphology=nmv.interface.ui_morphology)

            elif context.scene.RenderingExtent == \
                    nmv.enums.Skeletonization.Rendering.SELECTED_ARBROS_EXTENT:

                # Compute the bounding box for the available curves only
                bounding_box = nmv.bbox.compute_scene_bounding_box_for_curves()

            else:
                self.report({'ERROR'}, 'Invalid Rendering Extent')
                return {'FINISHED'}
        """
        nmv.rendering.NeuronSkeletonRenderer.render(
            bounding_box=bounding_box,
            camera_view=nmv.enums.Camera.View.TOP,
            image_resolution=context.scene.MorphologyFrameResolution,
            image_name='MORPHOLOGY_TOP_%s' % nmv.interface.ui_options.morphology.label,
            image_directory=nmv.interface.ui_options.io.images_directory,
            keep_camera_in_scene=context.scene.KeepSomaCameras)

        # Report the process termination in the UI
        self.report({'INFO'}, 'Rendering Morphology Done')

        # Confirm operation done
        return {'FINISHED'}


####################################################################################################
# @RenderMorphology360
####################################################################################################
class RenderMorphology360(bpy.types.Operator):
    """Render a 360 view of the reconstructed morphology"""

    # Operator parameters
    bl_idname = "render_morphology.360"
    bl_label = "360"

    # Timer parameters
    event_timer = None
    timer_limits = bpy.props.IntProperty(default=0)

    # Output data
    output_directory = None

    ################################################################################################
    # @modal
    ################################################################################################
    def modal(self, context, event):
        """
        Threading and non-blocking handling.

        :param context: Panel context.
        :param event: A given event for the panel.
        """

        # Get a reference to the scene
        scene = context.scene

        # Cancelling event, if using right click or exceeding the time limit of the simulation
        if event.type in {'RIGHTMOUSE', 'ESC'} or self.timer_limits > 360:

            # Reset the timer limits
            self.timer_limits = 0

            # Refresh the panel context
            self.cancel(context)

            # Done
            return {'FINISHED'}

        # Timer event, where the function is executed here on a per-frame basis
        if event.type == 'TIMER':

            # Set the frame name
            image_name = '%s/frame_%s' % (
                self.output_directory, '{0:05d}'.format(self.timer_limits))

            # A reference to the bounding box that will be used for the rendering
            bounding_box = None
            """
            # Rendering a close up view
            if context.scene.RenderingView == nmv.enums.Skeletonization.Rendering.CLOSE_UP_VIEW:

                # Compute the bounding box for a close up view
                bounding_box = nmv.bbox.compute_unified_extent_bounding_box(
                    extent=context.scene.MorphologyCloseUpDimensions)

            # Render the whole morphology view
            elif context.scene.RenderingView == nmv.enums.Skeletonization.Rendering.FULL_VIEW:

                if context.scene.RenderingExtent == \
                        nmv.enums.Skeletonization.Rendering.FULL_MORPHOLOGY_EXTENT:

                    # Compute the full morphology bounding box
                    bounding_box = nmv.skeleton.compute_full_morphology_bounding_box(
                        morphology=nmv.interface.ui_morphology)

                elif context.scene.RenderingExtent == \
                        nmv.enums.Skeletonization.Rendering.SELECTED_ARBROS_EXTENT:

                    # Compute the bounding box for the available curves only
                    bounding_box = nmv.bbox.compute_scene_bounding_box_for_curves()

                else:
                    self.report({'ERROR'}, 'Invalid Rendering Extent')
                    return {'FINISHED'}
            """
            # Render a frame
            nmv.rendering.NeuronSkeletonRenderer.render_at_angle(
                morphology_objects=nmv.interface.ui_reconstructed_skeleton,
                angle=self.timer_limits,
                bounding_box=bounding_box,
                camera_view=nmv.enums.Camera.View.FRONT,
                image_resolution=context.scene.MorphologyFrameResolution,
                image_name=image_name)

            # Update the progress shell
            nmv.utilities.show_progress('Rendering', self.timer_limits, 360)

            # Update the progress bar
            #TODO FIX
            context.scene.SomaRenderingProgress = int(100 * self.timer_limits / 360.0)

            # Upgrade the timer limits
            self.timer_limits += 1

        # Next frame
        return {'PASS_THROUGH'}

    ################################################################################################
    # @execute
    ################################################################################################
    def execute(self, context):
        """
        Execute the operator.

        :param context: Panel context.
        """

        # Ensure that there is a valid directory where the images will be written to
        if nmv.interface.ui_options.io.output_directory is None:
            self.report({'ERROR'}, nmv.consts.Messages.PATH_NOT_SET)
            return {'FINISHED'}

        if not nmv.file.ops.path_exists(context.scene.OutputDirectory):
            self.report({'ERROR'}, nmv.consts.Messages.INVALID_OUTPUT_PATH)
            return {'FINISHED'}

        # Create the sequences directory if it does not exist
        if not nmv.file.ops.path_exists(nmv.interface.ui_options.io.sequences_directory):
            nmv.file.ops.clean_and_create_directory(
                nmv.interface.ui_options.io.sequences_directory)

        # Create a specific directory for this mesh
        self.output_directory = '%s/%s_morphology_360' % \
                                (nmv.interface.ui_options.io.sequences_directory,
                                 nmv.interface.ui_options.morphology.label)
        nmv.file.ops.clean_and_create_directory(self.output_directory)

        # Use the event timer to update the UI during the soma building
        wm = context.window_manager
        self.event_timer = wm.event_timer_add(time_step=0.01, window=context.window)
        wm.modal_handler_add(self)

        # Done
        return {'RUNNING_MODAL'}

    ################################################################################################
    # @cancel
    ################################################################################################
    def cancel(self, context):
        """
        Cancel the panel processing and return to the interaction mode.

        :param context: Panel context.
        """

        # Multi-threading
        wm = context.window_manager
        wm.event_timer_remove(self.event_timer)

        # Report the process termination in the UI
        self.report({'INFO'}, 'Morphology Rendering Done')

        # Confirm operation done
        return {'FINISHED'}


####################################################################################################
# @RenderMorphologyProgressive
####################################################################################################
class RenderMorphologyProgressive(bpy.types.Operator):
    """Render a progressive sequence of the reconstruction procedure (time-consuming)"""

    # Operator parameters
    bl_idname = "render_morphology.progressive"
    bl_label = "Progressive"

    ################################################################################################
    # @execute
    ################################################################################################
    def execute(self, context):
        """
        Execute the operator.

        :param context: Context.
        :return: 'FINISHED'
        """

        # Get a reference to the scene
        scene = context.scene

        # Ensure that there is a valid directory where the images will be written to
        if nmv.interface.ui_options.output.output_directory is None:
            self.report({'ERROR'}, nmv.consts.Messages.PATH_NOT_SET)
            return {'FINISHED'}

        if not file_ops.path_exists(context.scene.OutputDirectory):
            self.report({'ERROR'}, nmv.consts.Messages.INVALID_OUTPUT_PATH)
            return {'FINISHED'}

        # Create the sequences directory if it does not exist
        if not file_ops.path_exists(nmv.interface.ui_options.output.sequences_directory):
            file_ops.clean_and_create_directory(nmv.interface.ui_options.output.sequences_directory)

        # Clear the scene
        nmv.scene.ops.clear_scene()

        # NOTE: To render a progressive reconstruction sequence, this requires setting the
        # morphology progressive rendering flag to True and then passing the nmv.interface.ui_options
        # to the morphology builder and disabling it after the rendering
        nmv.interface.ui_options.morphology.render_progressive = True

        # Create a skeleton builder object
        morphology_builder = skeleton_builder.SkeletonBuilder(
            ui_interface.morphology, nmv.interface.ui_options)

        # Reconstruct the morphology
        morphology_skeleton_objects = morphology_builder.draw_morphology_skeleton()

        # Setting the progressive rendering flag to False (default value)
        nmv.interface.ui_options.morphology.render_progressive = False

        # Report the process termination in the UI
        self.report({'INFO'}, 'Morphology Rendering Done')

        # Confirm operation done
        return {'FINISHED'}


####################################################################################################
# @SaveSomaMeshBlend
####################################################################################################
class SaveMorphologyBLEND(bpy.types.Operator):
    """Save the reconstructed morphology in a blender file"""

    # Operator parameters
    bl_idname = "save_morphology.blend"
    bl_label = "Blender Format (.blend)"

    ################################################################################################
    # @execute
    ################################################################################################
    def execute(self,
                context):
        """
        Executes the operator.

        :param context: Operator context.
        :return: {'FINISHED'}
        """

        # Ensure that there is a valid directory where the meshes will be written to
        if nmv.interface.ui_options.output.output_directory is None:
            self.report({'ERROR'}, nmv.consts.Messages.PATH_NOT_SET)
            return {'FINISHED'}

        if not file_ops.path_exists(context.scene.OutputDirectory):
            self.report({'ERROR'}, nmv.consts.Messages.INVALID_OUTPUT_PATH)
            return {'FINISHED'}

        # Create the meshes directory if it does not exist
        if not file_ops.path_exists(nmv.interface.ui_options.output.meshes_directory):
            file_ops.clean_and_create_directory(nmv.interface.ui_options.output.meshes_directory)

        # Export the reconstructed morphology as an .blend file
        # NOTE: Since we don't have meshes, then the mesh_object argument will be set to None and
        # the exported blender file will contain all the morphology objects.
        exporters.export_object_to_blend_file(mesh_object=None,
            output_directory=nmv.interface.ui_options.output.meshes_directory,
            output_file_name=ui_interface.morphology.label)

        return {'FINISHED'}


####################################################################################################
# @register_panel
####################################################################################################
def register_panel():
    """Registers all the classes in this panel"""

    # Soma reconstruction panel
    bpy.utils.register_class(MorphologyPanel)

    # Soma reconstruction operator
    bpy.utils.register_class(ReconstructMorphologyOperator)

    # Morphology rendering
    bpy.utils.register_class(RenderMorphologyFront)
    bpy.utils.register_class(RenderMorphologySide)
    bpy.utils.register_class(RenderMorphologyTop)
    bpy.utils.register_class(RenderMorphology360)
    bpy.utils.register_class(RenderMorphologyProgressive)

    # Saving morphology
    bpy.utils.register_class(SaveMorphologyBLEND)


####################################################################################################
# @unregister_panel
####################################################################################################
def unregister_panel():
    """Un-registers all the classes in this panel"""

    # Morphology reconstruction panel
    bpy.utils.unregister_class(MorphologyPanel)

    # Morphology reconstruction operator
    bpy.utils.unregister_class(ReconstructMorphologyOperator)

    # Morphology rendering
    bpy.utils.unregister_class(RenderMorphologyTop)
    bpy.utils.unregister_class(RenderMorphologySide)
    bpy.utils.unregister_class(RenderMorphologyFront)
    bpy.utils.unregister_class(RenderMorphology360)
    bpy.utils.unregister_class(RenderMorphologyProgressive)

    # Saving morphology
    bpy.utils.unregister_class(SaveMorphologyBLEND)