# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
from sys import platform
from bpy.props import (IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       BoolProperty,
                       StringProperty,
                       PointerProperty,
                       CollectionProperty)

Scene = bpy.types.Scene


# set fileformat for image saving on same format as in YafaRay, both have default PNG
def call_update_fileformat(self, context):
    scene = context.scene
    render = scene.render
    if scene.img_output is not render.image_settings.file_format:
        render.image_settings.file_format = scene.img_output

class YafaRayProperties(bpy.types.PropertyGroup):
    pass
    
class YafaRayNoiseControlProperties(bpy.types.PropertyGroup):
    resampled_floor = FloatProperty(
        name="Resampled floor (%)",
        description=("Noise reduction: when resampled pixels go below this value (% of total pixels),"
                     " the AA threshold will automatically decrease before the next pass"),
        min=0.0, max=100.0, precision=1,
        default=0.0)

    sample_multiplier_factor = FloatProperty(
        name="AA sample multiplier factor",
        description="Factor to increase the AA samples multiplier for next AA pass",
        min=1.0, max=2.0, precision=2,
        default=1.0)

    light_sample_multiplier_factor = FloatProperty(
        name="Light sample multiplier factor",
        description="Factor to increase the light samples multiplier for next AA pass",
        min=1.0, max=2.0, precision=2,
        default=1.0)

    indirect_sample_multiplier_factor = FloatProperty(
        name="Indirect sample multiplier factor",
        description="Factor to increase the indirect samples (FG for example) multiplier for next AA pass",
        min=1.0, max=2.0, precision=2,
        default=1.0)

    detect_color_noise = BoolProperty(
        name="Color noise detection",
        description="Detect noise in RGB components in addidion to pixel brightness",
        default=False)
        
    dark_threshold_factor = FloatProperty(
        name="Dark areas noise detection factor",
        description=("Factor used to reduce the AA threshold in dark areas."
                     " It will reduce noise in dark areas, but noise in bright areas will take longer"),
        min=0.0, max=1.0, precision=3,
        default=0.0)

    variance_edge_size = IntProperty(
        name="Variance window",
        description="Window edge size for variance noise detection",
        min=4, max=20,
        default=10)

    variance_pixels = IntProperty(
        name="Variance threshold",
        description="Threshold (in pixels) for variance noise detection. 0 disables variance detection",
        min=0, max=10,
        default=0)

    clamp_samples = FloatProperty(
        name="Clamp samples",
        description="Clamp RGB values in all samples, less noise but less realism. 0.0 disables clamping",
        min=0.0, precision=1,
        default=0.0)

    clamp_indirect = FloatProperty(
        name="Clamp indirect",
        description="Clamp RGB values in the indirect light, less noise but less realism. 0.0 disables clamping",
        min=0.0, precision=1,
        default=0.0)

    
class YafaRayRenderPassesProperties(bpy.types.PropertyGroup):
    pass_enable = BoolProperty(
        name="Enable render passes",
        default=False)

    pass_mask_obj_index = IntProperty(
        name="Mask Object Index",
        description="Object index used for masking in the Mask render passes",
        min=0,
        default=0)
        
    pass_mask_mat_index = IntProperty(
        name="Mask Material Index",
        description="Material index used for masking in the Mask render passes",
        min=0,
        default=0)    
        
    pass_mask_invert = BoolProperty(
        name="Invert Mask selection",
        description="Property to mask-in or mask-out the desired objects/materials in the Mask render passes",
        default=False)
    
    pass_mask_only = BoolProperty(
        name="Mask Only",
        description="Property to show the mask only instead of the masked rendered image",
        default=False)


    #The numbers here MUST NEVER CHANGE to keep backwards compatibility with older scenes. The numbers do not need to match the Core internal pass numbers.
    #The matching between these properties and the YafaRay Core internal passes is done via the first string, for example 'z-depth-abs'. They must match the list of strings for internal passes in the Core: include/core_api/color.h

    renderPassItemsDisabled=sorted((
            ('disabled', "Disabled", "Disable this pass", 999999),
        ), key=lambda index: index[1])

    renderPassItemsBasic=sorted((
            ('combined', "Basic: Combined image", "Basic: Combined standard image", 0),
            ('diffuse', "Basic: Diffuse", "Basic: Diffuse materials", 1),
            ('diffuse-noshadow', "Basic: Diffuse (no shadows)", "Basic: Diffuse materials (without shadows)", 2),
            ('shadow', "Basic: Shadow", "Basic: Shadows", 3),
            ('env', "Basic: Environment", "Basic: Environmental light", 4),
            ('indirect', "Basic: Indirect", "Basic: Indirect light (all, including caustics and diffuse)", 5),
            ('emit', "Basic: Emit", "Basic: Objects emitting light", 6),
            ('reflect', "Basic: Reflection", "Basic: Reflections (all, including perfect and glossy)", 7),
            ('refract', "Basic: Refraction", "Basic: Refractions (all, including perfect and sampled)", 8),
            ('mist', "Basic: Mist", "Basic: Mist", 9),
        ), key=lambda index: index[1])
        
    renderPassItemsDepth=sorted((
            ('z-depth-abs', "Z-Depth (absolute)", "Z-Depth (absolute values)", 101),
            ('z-depth-norm', "Z-Depth (normalized)", "Z-Depth (normalized values)", 102),
        ), key=lambda index: index[1])
                        
    renderPassItemsIndex=sorted((
            ('obj-index-abs', "Index-Object (absolute)", "Index-Object: Grayscale value = obj.index in the object properties (absolute values)", 201),
            ('obj-index-norm', "Index-Object (normalized)", "Index-Object: Grayscale value = obj.index in the object properties (normalized values)", 202),
            ('obj-index-auto', "Index-Object (auto)", "Index-Object: A color automatically generated for each object", 203),
            ('obj-index-mask', "Index-Object Mask", "Index-Object: Masking object based on obj.index.mask setting", 204),
            ('obj-index-mask-shadow', "Index-Object Mask Shadow", "Index-Object: Masking object shadow based on obj.index.mask setting", 205),
            ('obj-index-mask-all', "Index-Object Mask All (Object+Shadow)", "Index-Object: Masking object+shadow based on obj.index.mask setting", 206),
            ('mat-index-abs', "Index-Material (absolute)", "Index-Material: Grayscale value = mat.index in the material properties (absolute values)", 207),
            ('mat-index-norm', "Index-Material (normalized)", "Index-Material: Grayscale value = mat.index in the material properties (normalized values)", 208),
            ('mat-index-auto', "Index-Material (auto)", "Index-Material: A color automatically generated for each material", 209),
            ('mat-index-mask', "Index-Material Mask", "Index-Material: Masking material based on mat.index.mask setting", 210),
            ('mat-index-mask-shadow', "Index-Material Mask Shadow", "Index-Material: Masking material shadow based on mat.index.mask setting", 211),
            ('mat-index-mask-all', "Index-Material Mask All (Object+Shadow)", "Index-Material: Masking material+shadow based on mat.index.mask setting", 212)
        ), key=lambda index: index[1])
        
    renderPassItemsDebug=sorted((
            ('debug-aa-samples', "Debug: AA sample count", "Debug: Adaptative AA sample count (estimation), normalized", 301),
            ('debug-uv', "Debug: UV", "Debug: UV coordinates (black for objects with no UV mapping)", 302),
            ('debug-dsdv', "Debug: dSdV", "Debug: shading dSdV", 303),
            ('debug-dsdu', "Debug: dSdU", "Debug: shading dSdU", 304),
            ('debug-dpdv', "Debug: dPdV", "Debug: surface dPdV", 305),
            ('debug-dpdu', "Debug: dPdU", "Debug: surface dPdU", 306),
            ('debug-nv', "Debug: NV", "Debug - surface NV", 307),
            ('debug-nu', "Debug: NU", "Debug - surface NU", 308),
            ('debug-normal-geom', "Debug: Normals (geometric)", "Normals (geometric, no smoothness)", 309),
            ('debug-normal-smooth', "Debug: Normals (smooth)", "Normals (including smoothness)", 310),
        ), key=lambda index: index[1])

    renderInternalPassAdvanced=sorted((
            ('adv-reflect', "Adv: Reflection ", "Advanced: Reflections (perfect only)", 401),
            ('adv-refract', "Adv: Refraction", "Advanced: Refractions (perfect only)", 402),
            ('adv-radiance', "Adv: Photon Radiance map", "Advanced: Radiance map (only for photon mapping)", 403),
            ('adv-volume-transmittance', "Adv: Volume Transmittance", "Advanced: Volume Transmittance", 404),
            ('adv-volume-integration', "Adv: Volume integration", "Advanced: Volume integration", 405),
            ('adv-diffuse-indirect', "Adv: Diffuse Indirect", "Advanced: Diffuse Indirect light", 406),
            ('adv-diffuse-color', "Adv: Diffuse color", "Advanced: Diffuse color", 407),
            ('adv-glossy', "Adv: Glossy", "Advanced: Glossy materials", 408),
            ('adv-glossy-indirect', "Adv: Glossy Indirect", "Advanced: Glossy Indirect light", 409),
            ('adv-glossy-color', "Adv: Glossy color", "Advanced: Glossy color", 410),
            ('adv-trans', "Adv: Transmissive", "Advanced: Transmissive materials", 411),
            ('adv-trans-indirect', "Adv: Trans.Indirect", "Advanced: Transmissive Indirect light", 412),
            ('adv-trans-color', "Adv: Trans.color", "Advanced: Transmissive color", 413),
            ('adv-subsurface', "Adv: SubSurface", "Advanced: SubSurface materials", 414),
            ('adv-subsurface-indirect', "Adv: SubSurf.Indirect", "Advanced: SubSurface Indirect light", 415),
            ('adv-subsurface-color', "Adv: SubSurf.color", "Advanced: SubSurface color", 416),
            ('adv-indirect', "Adv: Indirect", "Adv: Indirect light (depends on the integrator but usually caustics only)", 417),
            ('adv-surface-integration', "Adv: Surface Integration", "Advanced: Surface Integration", 418),
        ), key=lambda index: index[1])

    renderPassItemsAO=sorted((
            ('ao', "AO", "Ambient Occlusion", 501),
            ('ao-clay', "AO clay", "Ambient Occlusion (clay)", 502),
        ), key=lambda index: index[1])

    renderPassAllItems = sorted(renderPassItemsBasic+renderInternalPassAdvanced+renderPassItemsIndex+renderPassItemsDebug+renderPassItemsDepth+renderPassItemsAO, key=lambda index: index[1])

    #This property is not currently used by YafaRay Core, as the combined external pass is always using the internal combined pass. 
    pass_Combined = EnumProperty(
        name="Combined",  #RGBA (4 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassItemsDisabled
        ),
        default="disabled")

    pass_Depth = EnumProperty(
        name="Depth",  #Gray (1 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassItemsDepth
        ),
        default="z-depth-norm")

    pass_Vector = EnumProperty(
        name="Vector",  #RGBA (4 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="obj-index-auto")

    pass_Normal = EnumProperty(
        name="Normal",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="debug-normal-smooth")
        
    pass_UV = EnumProperty(
        name="UV",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="debug-uv")

    pass_Color = EnumProperty(
        name="Color",  #RGBA (4 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="mat-index-auto")

    pass_Emit = EnumProperty(
        name="Emit",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="emit")
        
    pass_Mist = EnumProperty(
        name="Mist",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="mist")

    pass_Diffuse = EnumProperty(
        name="Diffuse",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="diffuse")
        
    pass_Spec = EnumProperty(
        name="Spec",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="adv-reflect")

    pass_AO = EnumProperty(
        name="AO",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassItemsAO
        ),
        default="ao")

    pass_Env = EnumProperty(
        name="Env",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="env")

    pass_Indirect = EnumProperty(
        name="Indirect",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="indirect")

    pass_Shadow = EnumProperty(
        name="Shadow",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="shadow")

    pass_Reflect = EnumProperty(
        name="Reflect",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="reflect")

    pass_Refract = EnumProperty(
        name="Refract",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="refract")

    pass_IndexOB = EnumProperty(
        name="Object Index",  #Gray (1 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassItemsIndex
        ),
        default="obj-index-norm")
        
    pass_IndexMA = EnumProperty(
        name="Material Index",  #Gray (1 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassItemsIndex
        ),
        default="mat-index-norm")

    pass_DiffDir = EnumProperty(
        name="Diff Dir",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="diffuse")
        
    pass_DiffInd = EnumProperty(
        name="Diff Ind",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="adv-diffuse-indirect")

    pass_DiffCol = EnumProperty(
        name="Diff Col",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="adv-diffuse-color")

    pass_GlossDir = EnumProperty(
        name="Gloss Dir",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="adv-glossy")
        
    pass_GlossInd = EnumProperty(
        name="Gloss Ind",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="adv-glossy-indirect")

    pass_GlossCol = EnumProperty(
        name="Gloss Col",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="adv-glossy-color")

    pass_TransDir = EnumProperty(
        name="Trans Dir",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="adv-trans")
        
    pass_TransInd = EnumProperty(
        name="Trans Ind",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="adv-trans-indirect")

    pass_TransCol = EnumProperty(
        name="Trans Col",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="adv-trans-color")

    pass_SubsurfaceDir = EnumProperty(
        name="SubSurface Dir",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="adv-subsurface")
        
    pass_SubsurfaceInd = EnumProperty(
        name="SubSurface Ind",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="adv-subsurface-indirect")

    pass_SubsurfaceCol = EnumProperty(
        name="SubSurface Col",  #RGB (3 x float)
        description="Select the type of image you want to be displayed in this pass",
        items=(renderPassAllItems
        ),
        default="adv-subsurface-color")

def register():
    ########### YafaRays general settings properties #############
    Scene.gs_ray_depth = IntProperty(
        name="Ray depth",
        description="Maximum depth for recursive raytracing",
        min=0, max=64, default=2)

    Scene.gs_shadow_depth = IntProperty(
        name="Shadow depth",
        description="Max. depth for transparent shadows calculation (if enabled)",
        min=0, max=64, default=2)

    Scene.gs_threads = IntProperty(
        name="Threads",
        description="Number of threads to use for rendering",
        min=1, default=1)

    Scene.gs_gamma = FloatProperty(
        name="Gamma",
        description="Gamma correction applied to final output, inverse correction "
                    "of textures and colors is performed",
        min=0, max=5, default= 1.0)

    Scene.gs_gamma_input = FloatProperty(
        name="Gamma input",
        description="Gamma correction applied to input",
        min=0, max=5, default=1.0)

    Scene.gs_tile_size = IntProperty(
        name="Tile size",
        description="Size of the render buckets (tiles)",
        min=0, max=1024, default=32)

    Scene.gs_tile_order = EnumProperty(
        name="Tile order",
        description="Selects tiles order type",
        items=(
            ('linear', "Linear", ""),
            ('random', "Random", "")
        ),
        default='random')

    Scene.gs_auto_threads = BoolProperty(
        name="Auto threads",
        description="Activate thread number auto detection",
        default=True)

    Scene.gs_clay_render = BoolProperty(
        name="Render clay",
        description="Override all materials with a white diffuse material",
        default=False)

    Scene.gs_clay_render_keep_transparency = BoolProperty(
        name="Keep transparency",
        description="Keep transparency during clay render",
        default=False)

    Scene.gs_clay_render_keep_normals = BoolProperty(
        name="Keep normal/bump maps",
        description="Keep normal and bump maps during clay render",
        default=False)

    Scene.gs_clay_oren_nayar = BoolProperty(
        name="Oren-Nayar",
        description="Use Oren-Nayar shader for a more realistic diffuse clay render",
        default=True)

    Scene.gs_clay_sigma = FloatProperty(
        name="Sigma",
        description="Roughness of the clay surfaces when rendering with Clay-Oren Nayar",
        min=0.0, max=1.0,
        step=1, precision=5,
        soft_min=0.0, soft_max=1.0,
        default=0.30000)


    # added clay color property
    Scene.gs_clay_col = FloatVectorProperty(
        name="Clay color",
        description="Color of clay render material",
        subtype='COLOR',
        min=0.0, max=1.0,
        default=(0.5, 0.5, 0.5))

    Scene.gs_mask_render = BoolProperty(
        name="Render mask",
        description="Renders an object mask pass with different colors",
        default=False)

    Scene.gs_draw_params = BoolProperty(
        name="Draw parameters",
        description="Write the render parameters below the image",
        default=False)

    Scene.bg_transp = BoolProperty(
        name="Transp.background",
        description="Render the background as transparent",
        default=False)

    Scene.bg_transp_refract = BoolProperty(
        name="Materials transp. refraction",
        description="Materials refract the background as transparent",
        default=True)

    Scene.adv_auto_shadow_bias_enabled = BoolProperty(
        name="Shadow Bias Automatic",
        description="Shadow Bias Automatic Calculation (recommended). Disable ONLY if artifacts or black dots due to bad self-shadowing, otherwise LEAVE THIS ENABLED FOR NORMAL SCENES",
        default=True)

    Scene.adv_shadow_bias_value = FloatProperty(
        name="Shadow Bias Factor",
        description="Shadow Bias (default 0.0005). Change ONLY if artifacts or black dots due to bad self-shadowing. Increasing this value can led to artifacts and incorrect renders",
        min=0.00000001, max=10000, default=0.0005)

    Scene.adv_auto_min_raydist_enabled = BoolProperty(
        name="Min Ray Dist Automatic",
        description="Min Ray Dist Automatic Calculation (recommended), based on the Shadow Bias factor. Disable ONLY if artifacts or light leaks due to bad ray intersections, otherwise LEAVE THIS ENABLED FOR NORMAL SCENES",
        default=True)

    Scene.adv_min_raydist_value = FloatProperty(
        name="Min Ray Dist Factor",
        description="Min Ray Dist (default 0.00005). Change ONLY if artifacts or light leaks due to bad ray intersections. Increasing this value can led to artifacts and incorrect renders",
        min=0.00000001, max=10000, default=0.00005)

    Scene.gs_custom_string = StringProperty(
        name="Custom string",
        description="Custom string will be added to the info bar, "
                    "use it for CPU, RAM etc",
        default="")

    Scene.gs_premult = BoolProperty(
        name="Premultiply",
        description="Premultipy Alpha channel for renders with transparent background",
        default=True)

    Scene.gs_transp_shad = BoolProperty(
        name="Transparent shadows",
        description="Compute transparent shadows",
        default=False)

    Scene.gs_show_sam_pix = BoolProperty(
        name="Show sample pixels",
        description="Masks pixels marked for resampling during adaptive passes",
        default=True)
    
    Scene.gs_verbose = BoolProperty(
        name="Log info to console",
        description="Print YafaRay engine log messages in console window",
        default=True)

    Scene.gs_type_render = EnumProperty(
        name="Render",
        description="Choose the render output method",
        items=(
            ('file', "Image file", "Render the Scene and write it to an Image File when finished"),
            ('into_blender', "Into Blender", "Render the Scene into Blenders Renderbuffer"),
            ('xml', "XML file", "Export the Scene to a XML File")
        ),
        default='into_blender')

    Scene.gs_tex_optimization = EnumProperty(
        name="Textures optimization",
        description="Textures optimization to reduce RAM usage, can be overriden by per-texture setting",
        items=(
            ('compressed', "Compressed", "Lossy color compression, some color/transparency details will be lost, more RAM improvement"),
            ('optimized', "Optimized", "Lossless optimization, good RAM improvement"),
            ('none', "None", "No optimization, lossless and faster but high RAM usage")
        ),
        default='optimized')
        
    ######### YafaRays own image output property ############
    Scene.img_output = EnumProperty(
        name="Image File Type",
        description="Image will be saved in this file format",
        items=(
            ('PNG', " PNG (Portable Network Graphics)", ""),
            ('TARGA', " TGA (Truevision TARGA)", ""),
            ('JPEG', " JPEG (Joint Photographic Experts Group)", ""),
            ('TIFF', " TIFF (Tag Image File Format)", ""),
            ('OPEN_EXR', " EXR (IL&M OpenEXR)", ""),
            ('HDR', " HDR (Radiance RGBE)", "")
        ),
        default='PNG', update=call_update_fileformat)

    Scene.img_multilayer = BoolProperty(
        name="MultiLayer",
        description="Enable MultiLayer image export, only available in certain formats as EXR",
        default=False)

    ########### YafaRays integrator properties #############
    Scene.intg_light_method = EnumProperty(
        name="Lighting Method",
        items=(
            ('Direct Lighting', "Direct Lighting", ""),
            ('Photon Mapping', "Photon Mapping", ""),
            ('Pathtracing', "Pathtracing", ""),
            ('Debug', "Debug", ""),
            ('Bidirectional', "Bidirectional", ""),
            ('SPPM', "SPPM", "")
        ),
        default='Direct Lighting')

    Scene.intg_use_caustics = BoolProperty(
        name="Caustic Photons",
        description="Enable photon map for caustics only",
        default=False)

    Scene.intg_photons = IntProperty(
        name="Photons",
        description="Number of photons to be shot",
        min=1, max=100000000,
        default=500000)

    Scene.intg_caustic_mix = IntProperty(
        name="Caustic Mix",
        description="Max. number of photons to mix (blur)",
        min=1, max=10000,
        default=100)

    Scene.intg_caustic_depth = IntProperty(
        name="Caustic Depth",
        description="Max. number of scatter events for photons",
        min=0, max=50,
        default=10)

    Scene.intg_caustic_radius = FloatProperty(
        name="Caustic Radius",
        description="Max. radius to search for photons",
        min=0.0001, max=100.0,
        default=1.0)

    Scene.intg_use_AO = BoolProperty(
        name="Ambient Occlusion",
        description="Enable ambient occlusion",
        default=False)

    Scene.intg_AO_samples = IntProperty(
        name="Samples",
        description="Number of samples for ambient occlusion",
        min=1, max=1000,
        default=32)

    Scene.intg_AO_distance = FloatProperty(
        name="Distance",
        description=("Max. occlusion distance,"
                     " Surfaces further away do not occlude ambient light"),
        min=0.0, max=10000.0,
        default=1.0)

    Scene.intg_AO_color = FloatVectorProperty(
        name="AO Color",
        description="Color Settings", subtype='COLOR',
        min=0.0, max=1.0,
        default=(0.9, 0.9, 0.9))

    Scene.intg_bounces = IntProperty(
        name="Depth",
        description="",
        min=1,
        default=4)

    Scene.intg_diffuse_radius = FloatProperty(
        name="Search radius",
        description="Radius to search for diffuse photons",
        min=0.001,
        default=1.0)

    Scene.intg_cPhotons = IntProperty(
        name="Count",
        description="Number of caustic photons to be shot",
        min=1, default=500000)

    Scene.intg_search = IntProperty(
        name="Search count",
        description="Maximum number of diffuse photons to be filtered",
        min=1, max=10000,
        default=100)

    Scene.intg_final_gather = BoolProperty(
        name="Final Gather",
        description="Use final gathering (recommended)",
        default=True)

    Scene.intg_fg_bounces = IntProperty(
        name="Bounces",
        description="Allow gather rays to extend to paths of this length",
        min=1, max=20,
        default=3)

    Scene.intg_fg_samples = IntProperty(
        name="Samples",
        description="Number of samples for final gathering",
        min=1,
        default=16)

    Scene.intg_show_map = BoolProperty(
        name="Show radiance map",
        description="Directly show radiance map, useful to calibrate the photon map (disables final gathering step)",
        default=False)

    Scene.intg_caustic_method = EnumProperty(
        name="Caustic Method",
        items=(
            ('None', "None", ""),
            ('Path', "Path", ""),
            ('Path+Photon', "Path+Photon", ""),
            ('Photon', "Photon", "")),
        description="Choose caustic rendering method",
        default='None')

    Scene.intg_path_samples = IntProperty(
        name="Path Samples",
        description="Number of path samples per pixel sample",
        min=1,
        default=32)

    Scene.intg_no_recursion = BoolProperty(
        name="No Recursion",
        description="No recursive raytracing, only pure path tracing",
        default=False)

    Scene.intg_debug_type = EnumProperty(
        name="Debug type",
        items=(
            ('N', "N", ""),
            ('dPdU', "dPdU", ""),
            ('dPdV', "dPdV", ""),
            ('NU', "NU", ""),
            ('NV', "NV", ""),
            ('dSdU', "dSdU", ""),
            ('dSdV', "dSdV", "")),
        default='dSdV')

    Scene.intg_show_perturbed_normals = BoolProperty(
        name="Show perturbed normals",
        description="Show the normals perturbed by bump and normal maps",
        default=False)

    Scene.intg_pm_ire = BoolProperty(
        name="PM Initial Radius Estimate",
        default=False)

    Scene.intg_pass_num = IntProperty(
        name="Passes",
        min=1,
        default=1000)

    Scene.intg_times = FloatProperty(
        name="Radius factor",
        min=0.0,
        description= "Initial radius times",
        default=1.0)

    Scene.intg_photon_radius = FloatProperty(
        name="Search radius",
        min=0.0,
        default=1.0)

    ######### YafaRays anti-aliasing/noise properties ###########
    Scene.AA_min_samples = IntProperty(
        name="Samples",
        description="Number of samples for first AA pass",
        min=1,
        default=1)

    Scene.AA_inc_samples = IntProperty(
        name="Additional Samples",
        description="Number of samples for additional AA passes",
        min=1,
        default=1)

    Scene.AA_passes = IntProperty(
        name="Passes",
        description=("Number of anti-aliasing passes,"
                     " Adaptive sampling (passes > 1) uses different pattern"),
        min=1,
        default=1)

    Scene.AA_threshold = FloatProperty(
        name="Threshold",
        description="Color threshold for additional AA samples in next pass",
        min=0.0, max=1.0, precision=4,
        default=0.05)

    Scene.AA_pixelwidth = FloatProperty(
        name="Pixelwidth",
        description="AA filter size",
        min=1.0, max=20.0, precision=3,
        default=1.5)

    Scene.AA_filter_type = EnumProperty(
        name="Filter",
        items=(
            ('box', "Box", "AA filter type"),
            ('mitchell', "Mitchell", "AA filter type"),
            ('gauss', "Gauss", "AA filter type"),
            ('lanczos', "Lanczos", "AA filter type")
        ),
        default="gauss")
        
    bpy.utils.register_class(YafaRayProperties)
    bpy.types.Scene.yafaray = PointerProperty(type=YafaRayProperties)

    bpy.utils.register_class(YafaRayRenderPassesProperties)
    YafaRayProperties.passes = PointerProperty(type=YafaRayRenderPassesProperties)
    
    bpy.utils.register_class(YafaRayNoiseControlProperties)
    YafaRayProperties.noise_control = PointerProperty(type=YafaRayNoiseControlProperties)

def unregister():
    Scene.gs_ray_depth
    Scene.gs_shadow_depth
    Scene.gs_threads
    Scene.gs_gamma
    Scene.gs_gamma_input
    Scene.gs_tile_size
    Scene.gs_tile_order
    Scene.gs_auto_threads
    Scene.gs_clay_render
    Scene.gs_clay_render_keep_transparency
    Scene.gs_clay_render_keep_normals
    Scene.gs_clay_oren_nayar
    Scene.gs_clay_sigma
    Scene.gs_clay_col
    Scene.gs_mask_render
    Scene.gs_draw_params
    Scene.bg_transp
    Scene.bg_transp_refract
    Scene.adv_auto_shadow_bias_enabled
    Scene.adv_shadow_bias_value
    Scene.adv_auto_min_raydist_enabled
    Scene.adv_min_raydist_value
    Scene.gs_custom_string
    Scene.gs_premult
    Scene.gs_transp_shad
    Scene.gs_show_sam_pix
    Scene.gs_verbose
    Scene.gs_type_render
    Scene.gs_tex_optimization

    Scene.img_output
    Scene.img_multilayer

    Scene.intg_light_method
    Scene.intg_use_caustics
    Scene.intg_photons
    Scene.intg_caustic_mix
    Scene.intg_caustic_depth
    Scene.intg_caustic_radius
    Scene.intg_use_AO
    Scene.intg_AO_samples
    Scene.intg_AO_distance
    Scene.intg_AO_color
    Scene.intg_bounces
    Scene.intg_diffuse_radius
    Scene.intg_cPhotons
    Scene.intg_search
    Scene.intg_final_gather
    Scene.intg_fg_bounces
    Scene.intg_fg_samples
    Scene.intg_show_map
    Scene.intg_caustic_method
    Scene.intg_path_samples
    Scene.intg_no_recursion
    Scene.intg_debug_type
    Scene.intg_show_perturbed_normals
    Scene.intg_pm_ire
    Scene.intg_pass_num
    Scene.intg_times
    Scene.intg_photon_radius

    Scene.AA_min_samples
    Scene.AA_inc_samples
    Scene.AA_passes
    Scene.AA_threshold
    Scene.AA_pixelwidth
    Scene.AA_filter_type

    bpy.utils.unregister_class(YafaRayNoiseControlProperties)
    bpy.utils.unregister_class(YafaRayRenderPassesProperties)
    bpy.utils.unregister_class(YafaRayProperties)
