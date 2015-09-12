bl_info = {
    'name': 'Rock-o-Matic',
    'author': 'Klaus Silveira',
    'version': (0, 1, 0),
    'blender': (2, 69, 0),
    'location': 'View3D > Add > Mesh',
    'description': 'Generates rocks using various techniques.',
    'warning': '',
    'wiki_url': 'http://wiki.blender.org/index.php?title=Extensions:2.6/Py/Scripts/Add_Mesh/Rock_o_Matic',
    'tracker_url': 'https://github.com/klaussilveira/rock-o-matic/issues',
    'category': 'Add Mesh'
}

import bpy
import bmesh
import math
import mathutils
import random

class MeshBase():
    def get_mesh(self):
        mesh = bpy.data.meshes.new('Rock')
        self.bmesh.to_mesh(mesh)
        self.bmesh.free()
        return mesh

class CubeBase(MeshBase):
    def __init__(self, rock_size, rock_scale_vector, rock_scale_factor):
        self.bmesh = bmesh.new()
        scaleMatrix = mathutils.Matrix.Scale(rock_scale_factor, 4, rock_scale_vector)
        bmesh.ops.create_cube(self.bmesh, size=rock_size, matrix=scaleMatrix)

class IcosphereBase(MeshBase):
    def __init__(self, rock_size, rock_scale_vector, rock_scale_factor):
        self.bmesh = bmesh.new()
        scaleMatrix = mathutils.Matrix.Scale(rock_scale_factor, 4, rock_scale_vector)
        bmesh.ops.create_icosphere(self.bmesh, subdivisions=1, diameter=rock_size, matrix=scaleMatrix)

class UvSphereBase(MeshBase):
    def __init__(self, rock_size, rock_scale_vector, rock_scale_factor):
        self.bmesh = bmesh.new()
        scaleMatrix = mathutils.Matrix.Scale(rock_scale_factor, 4, rock_scale_vector)
        bmesh.ops.create_uvsphere(self.bmesh, u_segments=5, v_segments=5, diameter=rock_size, matrix=scaleMatrix)

base_factory = {
    'CubeBase': CubeBase,
    'IcosphereBase': IcosphereBase,
    'UvSphereBase': UvSphereBase,
}

class GenericRecipe():
    def make(self, obj):
        firstSmooth = obj.modifiers.new(name='Subdivide 1', type='SUBSURF')
        firstSmooth.levels = 2

        secondSmooth = obj.modifiers.new(name='Subdivide 2', type='SUBSURF')
        secondSmooth.levels = 4

        voronoiMap = bpy.data.textures.new('Basic voronoi', type='VORONOI')
        voronoiMap.color_mode = 'INTENSITY'
        voronoiMap.weight_2 = random.uniform(0.2, 0.8)
        voronoiMap.weight_3 = random.uniform(0, 1)
        voronoiMap.noise_intensity = 1.0
        voronoiMap.nabla = 0.3
        voronoiMap.noise_scale = random.uniform(1.0, 1.5)
        cell = obj.modifiers.new(name='Basic voronoi', type='DISPLACE')
        cell.texture = voronoiMap
        cell.strength = random.uniform(0.5, 1)

        cloudMap = bpy.data.textures.new('Basic simplex', type='CLOUDS')
        cloudMap.noise_depth = random.randint(6, 8)
        cloudMap.noise_scale = random.uniform(0.8, 1)
        cloud = obj.modifiers.new(name='Basic simplex', type='DISPLACE')
        cloud.texture = cloudMap
        cloud.strength = random.uniform(0.2, 0.4)

        noiseMap = bpy.data.textures.new('Noise', type='NOISE')
        noise = obj.modifiers.new(name='Noise', type='DISPLACE')
        noise.texture = noiseMap
        noise.strength = 0.01

        finalSmooth = obj.modifiers.new(name='Final smooth', type='SUBSURF')
        finalSmooth.levels = 2

class ErodedRecipe():
    def make(self, obj):
        firstSmooth = obj.modifiers.new(name='Subdivide 1', type='SUBSURF')
        firstSmooth.levels = 2

        secondSmooth = obj.modifiers.new(name='Subdivide 2', type='SUBSURF')
        secondSmooth.levels = 4

        algorithms = ['DISTANCE', 'DISTANCE_SQUARED', 'MINKOVSKY_FOUR']
        cellMap = bpy.data.textures.new('Cellular shape', type='VORONOI')
        cellMap.distance_metric = random.choice(algorithms)
        cellMap.noise_intensity = random.uniform(0.8, 1)
        cellMap.noise_scale = random.uniform(0.7, 1)
        cell = obj.modifiers.new(name='Cellular shape', type='DISPLACE')
        cell.texture = cellMap
        cell.strength = 0.2
        cell.mid_level = 0.5

        algorithms = ['VORONOI_F1', 'VORONOI_F2', 'BLENDER_ORIGINAL', 'IMPROVED_PERLIN']
        noiseMap = bpy.data.textures.new('Base noise', type='CLOUDS')
        noiseMap.noise_basis = random.choice(algorithms)
        noiseMap.noise_depth = 2
        noiseMap.noise_scale = 0.2
        noise = obj.modifiers.new(name='Base noise', type='DISPLACE')
        noise.texture = noiseMap
        noise.strength = 0.02

        crackMap = bpy.data.textures.new('Cracks', type='VORONOI')
        crackMap.distance_metric = 'MINKOVSKY_FOUR'
        crackMap.noise_intensity = 0.8
        crackMap.noise_scale = random.uniform(0.8, 1.0)
        cracks = obj.modifiers.new(name='Cracks', type='DISPLACE')
        cracks.texture = crackMap
        cracks.strength = 0.1

        finalSmooth = obj.modifiers.new(name='Final smooth', type='SUBSURF')
        finalSmooth.levels = 2

class BoulderRecipe():
    def make(self, obj):
        firstSmooth = obj.modifiers.new(name='Subdivide 1', type='SUBSURF')
        firstSmooth.levels = 2

        secondSmooth = obj.modifiers.new(name='Subdivide 2', type='SUBSURF')
        secondSmooth.levels = 4

        cellMap = bpy.data.textures.new('Cellular shape', type='VORONOI')
        cellMap.distance_metric = 'DISTANCE_SQUARED'
        cellMap.weight_1 = 2
        cellMap.weight_2 = 2
        cellMap.weight_3 = 2
        cellMap.weight_4 = 2
        cellMap.noise_intensity = 1
        cellMap.noise_scale = 1
        cell = obj.modifiers.new(name='Cellular shape', type='DISPLACE')
        cell.texture = cellMap
        cell.strength = random.uniform(0.5, 0.7)
        cell.mid_level = random.uniform(0.6, 0.8)

        crackMap = bpy.data.textures.new('Cracks', type='MUSGRAVE')
        crackMap.octaves = 2
        crackMap.lacunarity = 2
        crackMap.dimension_max = 1
        crackMap.offset = 1.2
        crackMap.musgrave_type = 'HETERO_TERRAIN'
        crackMap.noise_basis = 'VORONOI_CRACKLE'
        crackMap.noise_scale = 7
        cracks = obj.modifiers.new(name='Cracks', type='DISPLACE')
        cracks.texture = crackMap
        cracks.strength = 0.05

        cloudMap = bpy.data.textures.new('Detailing', type='CLOUDS')
        cloudMap.noise_type = 'HARD_NOISE'
        cloudMap.noise_basis = 'IMPROVED_PERLIN'
        cloudMap.noise_depth = 2
        cloudMap.noise_scale = random.uniform(0.4, 0.5)
        cloud = obj.modifiers.new(name='Detailing', type='DISPLACE')
        cloud.texture = cloudMap
        cloud.strength = 0.05
        cloud.mid_level = 0.5

        finalSmooth = obj.modifiers.new(name='Final smooth', type='SUBSURF')
        finalSmooth.levels = 2

class ToonRecipe():
    def make(self, obj):
        firstSmooth = obj.modifiers.new(name='Subdivide 1', type='SUBSURF')
        firstSmooth.levels = 2

        secondSmooth = obj.modifiers.new(name='Subdivide 2', type='SUBSURF')
        secondSmooth.levels = 4

        cellMap = bpy.data.textures.new('Cellular shape', type='VORONOI')
        cellMap.distance_metric = 'DISTANCE_SQUARED'
        cellMap.noise_intensity = random.uniform(1, 1.2)
        cellMap.noise_scale = 1
        cell = obj.modifiers.new(name='Cellular shape', type='DISPLACE')
        cell.texture = cellMap
        cell.strength = 0.2
        cell.mid_level = 0.5

        finalSmooth = obj.modifiers.new(name='Final smooth', type='SUBSURF')
        finalSmooth.levels = 2

recipe_factory = {
    'GenericRecipe': GenericRecipe,
    'ErodedRecipe': ErodedRecipe,
    'BoulderRecipe': BoulderRecipe,
    'ToonRecipe': ToonRecipe,
}

class RockOMatic(bpy.types.Operator):
    bl_idname = 'mesh.rockomatic'
    bl_label = 'Rock-o-Matic'
    bl_options = {'REGISTER', 'UNDO'}

    rock_recipe = bpy.props.EnumProperty \
    (
        name = 'Recipe',
        description = 'Choose the rock generation recipe',
        items = [
            ('GenericRecipe', 'Generic', 'Generates generic rock forms', 1),
            ('ErodedRecipe', 'Eroded', 'Generates eroded rocks', 2),
            ('BoulderRecipe', 'Boulder', 'Generates boulder rocks', 3),
            ('ToonRecipe', 'Toon', 'Generates simplistic rocks with hard edges', 4),
        ],
        default = 'GenericRecipe'
    )

    rock_base = bpy.props.EnumProperty \
    (
        name = 'Base geometry',
        description = 'Choose the base geometry to generate the rock on',
        items = [
            ('CubeBase', 'Cube', 'Use cube as base', 1),
            ('IcosphereBase', 'Icosphere', 'Use iscosphere as base', 2),
            ('UvSphereBase', 'UvSphere', 'Use UV sphere as base', 3),
        ],
        default = 'CubeBase'
    )

    rock_size = bpy.props.FloatProperty \
    (
        name = 'Overall size',
        description = 'Overall size of the rock to generate'
    )

    rock_scale_vector = bpy.props.FloatVectorProperty \
    (
        name = 'Direction',
        description = 'Direction to apply the scaling',
        subtype = 'XYZ',
        unit = 'LENGTH'
    )

    rock_scale_factor = bpy.props.FloatProperty \
    (
        name = 'Factor',
        description = 'Amount of scaling to apply in the determined direction'
    )

    generate_lowpoly = bpy.props.BoolProperty \
    (
        name = 'Generate low-poly?',
        description = 'Allow the creation of a low-poly mesh for map baking',
        default = False
    )

    def execute(self, context):
        self.generate_rock(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.generate_rock(context)
        return {'FINISHED'}

    def draw(self, context):
        column = self.layout.column(align=True)
        column.operator('mesh.rockomatic', text='Regenerate')

        column.separator()
        column.prop(self, 'rock_recipe')
        column.prop(self, 'rock_base')
        column.prop(self, 'generate_lowpoly')

        column.label('Proportions')
        column.prop(self, 'rock_size')
        column.prop(self, 'rock_scale_vector')
        column.prop(self, 'rock_scale_factor')

    def set_defaults(self):
        if self.rock_size == 0:
            self.rock_size = random.uniform(1, 5)

        if not any(self.rock_scale_vector):
            self.rock_scale_vector = (random.uniform(1, 3), random.uniform(1, 3), random.uniform(1, 3))

        if self.rock_scale_factor == 0:
            self.rock_scale_factor = random.uniform(0.3, 3)

    def clear_rocks(self):
        rock_list = [item.name for item in bpy.data.objects if item.name.startswith('Rock')]

        for old_rock in rock_list:
            if bpy.data.objects[old_rock].hide:
                bpy.data.objects[old_rock].hide = False
            bpy.data.objects[old_rock].select = True
        bpy.ops.object.delete()

    def generate_rock(self, context):
        self.clear_rocks()
        self.set_defaults()

        # generate mesh and apply recipe
        rock = base_factory[self.rock_base](self.rock_size, self.rock_scale_vector, self.rock_scale_factor)
        obj = bpy.data.objects.new('Rock', rock.get_mesh())
        recipe = recipe_factory[self.rock_recipe]()
        recipe.make(obj)

        # add to scene and select
        context.scene.objects.link(obj)
        context.scene.objects.active = obj
        obj.select = True

        if self.generate_lowpoly:
            lowpoly_obj = obj.copy()
            lowpoly_obj.data = obj.data.copy()
            lowpoly_obj.scale = obj.scale
            lowpoly_obj.location = obj.location
            lowpoly_obj.name = 'Rock_LowPoly'
            lowpoly_obj.hide = True

            for modifier in lowpoly_obj.modifiers:
                if (modifier.name == 'Final smooth'):
                    lowpoly_obj.modifiers.remove(modifier)

            decimate = lowpoly_obj.modifiers.new(name='Decimation', type='DECIMATE')
            decimate.ratio = 0.01
            decimate.use_collapse_triangulate = True

            context.scene.objects.link(lowpoly_obj)


def add_to_menu(self, context):
    self.layout.operator('mesh.rockomatic', icon='PLUGIN')


def register():
    bpy.utils.register_class(RockOMatic)
    bpy.types.INFO_MT_mesh_add.append(add_to_menu)


def unregister():
    bpy.utils.unregister_class(RockOMatic)
    bpy.types.INFO_MT_mesh_add.remove(add_to_menu)

if __name__ == '__main__':
    register()
