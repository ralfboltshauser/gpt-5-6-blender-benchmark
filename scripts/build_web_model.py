"""Build the browser-ready, baked-lighting Sol Ultra diorama.

Run with:
    blender --background gpt-5.6-sol-ultra/cozy_forest_cabin.blend \
      --python scripts/build_web_model.py

The benchmark source remains untouched. The derivative web asset evaluates all
modifiers, consolidates the scene into subject and environment meshes, creates
unique UV atlases, and bakes the authored lighting with Cycles. The exported
materials are unlit, so the browser does not need a real-time light or shadow
rig to reproduce the scene's depth.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "site" / "assets" / "models"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GLB_PATH = OUTPUT_DIR / "sol-ultra-diorama.glb"
REPORT_PATH = OUTPUT_DIR / "sol-ultra-diorama.json"

ATLAS_SIZE = 1024
BAKE_SAMPLES = 128
BAKE_MARGIN = 4

SUBJECT_COLLECTIONS = {"CABIN", "ROOF", "PORCH", "PROPS", "DETAILS"}
ENVIRONMENT_COLLECTIONS = {"TERRAIN", "BACKGROUND", "VEGETATION"}

# The sky card and volume only work from the authored camera. The two crop trees
# are also omitted so the cabin stays readable across the bounded web orbit.
EXCLUDED_PREFIXES = (
    "Peach sunset sky",
    "Subtle atmospheric volume",
    "Near left crop pine",
    "Near right crop pine",
)


def source_groups() -> dict[str, list[bpy.types.Object]]:
    groups = {"subject": [], "environment": []}
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.name.startswith(EXCLUDED_PREFIXES):
            continue
        collections = {collection.name for collection in obj.users_collection}
        if collections & SUBJECT_COLLECTIONS:
            groups["subject"].append(obj)
        elif collections & ENVIRONMENT_COLLECTIONS:
            groups["environment"].append(obj)
    return groups


def combine_evaluated_meshes(
    name: str,
    objects: list[bpy.types.Object],
    depsgraph,
    export_collection: bpy.types.Collection,
) -> tuple[bpy.types.Object, list[str]]:
    vertices = []
    faces = []
    face_materials = []
    materials = {}

    for source in objects:
        evaluated = source.evaluated_get(depsgraph)
        mesh = bpy.data.meshes.new_from_object(
            evaluated,
            preserve_all_data_layers=False,
            depsgraph=depsgraph,
        )
        offset = len(vertices)
        vertices.extend(tuple(evaluated.matrix_world @ vertex.co) for vertex in mesh.vertices)
        slots = [slot.material for slot in source.material_slots]
        for polygon in mesh.polygons:
            if not slots:
                continue
            material = slots[min(polygon.material_index, len(slots) - 1)]
            if material is None:
                continue
            materials[material.name] = material
            faces.append(tuple(offset + index for index in polygon.vertices))
            face_materials.append(material.name)
        bpy.data.meshes.remove(mesh)

    material_names = sorted(materials)
    material_indices = {material_name: index for index, material_name in enumerate(material_names)}
    mesh = bpy.data.meshes.new(f"Sol Ultra {name} baked mesh")
    mesh.from_pydata(vertices, [], faces)
    for material_name in material_names:
        mesh.materials.append(materials[material_name])
    for polygon, material_name in zip(mesh.polygons, face_materials):
        polygon.material_index = material_indices[material_name]
        polygon.use_smooth = False
    mesh.validate(clean_customdata=False)
    mesh.update(calc_edges=True)

    obj = bpy.data.objects.new(f"Sol Ultra baked {name}", mesh)
    obj["source"] = "GPT-5.6 Sol Ultra benchmark"
    obj["web_optimization"] = "Cycles-baked lighting and consolidated geometry"
    export_collection.objects.link(obj)
    return obj, material_names


def unwrap_for_bake(obj: bpy.types.Object) -> str:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(
        angle_limit=math.radians(66.0),
        margin_method="SCALED",
        island_margin=max(0.001, BAKE_MARGIN / ATLAS_SIZE),
        area_weight=0.25,
        correct_aspect=True,
        scale_to_bounds=True,
    )
    bpy.ops.object.mode_set(mode="OBJECT")
    uv_layer = obj.data.uv_layers.active
    uv_layer.name = "Baked UV"
    uv_layer.active_render = True
    return uv_layer.name


def add_bake_target_nodes(obj: bpy.types.Object, image: bpy.types.Image, node_name: str) -> None:
    for material in obj.data.materials:
        if material is None:
            continue
        material.use_nodes = True
        nodes = material.node_tree.nodes
        for node in nodes:
            node.select = False
        target = nodes.get(node_name) or nodes.new("ShaderNodeTexImage")
        target.name = node_name
        target.label = "Web combined-lighting bake target"
        target.image = image
        target.select = True
        nodes.active = target


def make_unlit_material(name: str, image: bpy.types.Image) -> bpy.types.Material:
    material = bpy.data.materials.new(f"Sol Ultra baked {name} lighting")
    material.use_nodes = True
    material.use_backface_culling = False
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    background = nodes.new("ShaderNodeBackground")
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = image
    texture.interpolation = "Linear"
    texture.extension = "EXTEND"
    links.new(texture.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])
    return material


def configure_cycles(scene: bpy.types.Scene) -> None:
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = BAKE_SAMPLES
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.03
    scene.cycles.use_denoising = False
    scene.render.bake.use_pass_direct = True
    scene.render.bake.use_pass_indirect = True
    scene.render.bake.use_pass_color = True
    scene.render.bake.margin = BAKE_MARGIN
    scene.render.bake.margin_type = "EXTEND"


started = time.perf_counter()
groups = source_groups()
sources = [obj for group in groups.values() for obj in group]
for source in sources:
    source.hide_render = True
for obj in bpy.context.scene.objects:
    if obj.type == "MESH" and obj.name.startswith(EXCLUDED_PREFIXES):
        obj.hide_render = True

export_collection = bpy.data.collections.get("WEB_BAKED_EXPORT")
if export_collection:
    for existing in list(export_collection.objects):
        bpy.data.objects.remove(existing, do_unlink=True)
else:
    export_collection = bpy.data.collections.new("WEB_BAKED_EXPORT")
    bpy.context.scene.collection.children.link(export_collection)

depsgraph = bpy.context.evaluated_depsgraph_get()
targets = {}
source_material_names = set()
combine_seconds = {}
unwrap_seconds = {}
uv_layers = {}

for name, objects in groups.items():
    tick = time.perf_counter()
    target, material_names = combine_evaluated_meshes(name, objects, depsgraph, export_collection)
    combine_seconds[name] = round(time.perf_counter() - tick, 3)
    targets[name] = target
    source_material_names.update(material_names)

    tick = time.perf_counter()
    uv_layers[name] = unwrap_for_bake(target)
    unwrap_seconds[name] = round(time.perf_counter() - tick, 3)

scene = bpy.context.scene
configure_cycles(scene)

images = {}
bake_seconds = {}
png_bytes = {}
for name, target in targets.items():
    image = bpy.data.images.new(
        f"Sol Ultra {name} combined-lighting bake",
        width=ATLAS_SIZE,
        height=ATLAS_SIZE,
        alpha=False,
        float_buffer=False,
    )
    image.generated_color = (0.03, 0.03, 0.03, 1.0)
    image.colorspace_settings.name = "sRGB"
    add_bake_target_nodes(target, image, f"SOL_ULTRA_{name.upper()}_BAKE_TARGET")

    bpy.ops.object.select_all(action="DESELECT")
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    tick = time.perf_counter()
    bpy.ops.object.bake(
        type="COMBINED",
        pass_filter={
            "DIRECT",
            "INDIRECT",
            "COLOR",
            "DIFFUSE",
            "GLOSSY",
            "TRANSMISSION",
            "EMIT",
        },
        margin=BAKE_MARGIN,
        use_clear=True,
        target="IMAGE_TEXTURES",
        save_mode="INTERNAL",
        uv_layer=uv_layers[name],
    )
    bake_seconds[name] = round(time.perf_counter() - tick, 3)

    png_path = OUTPUT_DIR / f"sol-ultra-baked-{name}.png"
    image.filepath_raw = str(png_path)
    image.file_format = "PNG"
    image.save()
    image.pack()
    png_bytes[name] = png_path.stat().st_size
    images[name] = image

for name, target in targets.items():
    target.data.materials.clear()
    target.data.materials.append(make_unlit_material(name, images[name]))
    for polygon in target.data.polygons:
        polygon.material_index = 0

bpy.ops.object.select_all(action="DESELECT")
for target in targets.values():
    target.hide_render = False
    target.hide_set(False)
    target.select_set(True)
bpy.context.view_layer.objects.active = targets["subject"]

export_tick = time.perf_counter()
bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_cameras=False,
    export_lights=False,
    export_materials="EXPORT",
    export_texcoords=True,
    export_normals=False,
    export_tangents=False,
    export_attributes=False,
    export_extras=True,
    export_yup=True,
)
export_seconds = round(time.perf_counter() - export_tick, 3)

report = {
    "source_file": "gpt-5.6-sol-ultra/cozy_forest_cabin.blend",
    "source_mesh_objects": len(sources),
    "source_materials_used": len(source_material_names),
    "web_meshes": len(targets),
    "web_polygons_by_group": {
        name: len(target.data.polygons) for name, target in targets.items()
    },
    "baked_textures": {
        name: {
            "file": f"sol-ultra-baked-{name}.png",
            "size": [ATLAS_SIZE, ATLAS_SIZE],
            "png_bytes": png_bytes[name],
        }
        for name in targets
    },
    "bake_samples": BAKE_SAMPLES,
    "bake_margin": BAKE_MARGIN,
    "excluded": list(EXCLUDED_PREFIXES),
    "raw_glb_bytes": GLB_PATH.stat().st_size,
    "seconds": {
        "combine": combine_seconds,
        "unwrap": unwrap_seconds,
        "bake": bake_seconds,
        "export": export_seconds,
        "total": round(time.perf_counter() - started, 3),
    },
}
REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

print("WEB_MODEL_REPORT", json.dumps(report, sort_keys=True))
