"""Build the browser-ready Sol Ultra diorama.

Run with:
    blender --background gpt-5.6-sol-ultra/cozy_forest_cabin.blend \
      --python scripts/build_web_model.py

The benchmark source scene stays untouched. This exporter evaluates modifiers,
combines hundreds of small objects into four draw-call groups, maps every face
to a compact palette atlas, and exports a single glTF Binary file.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "site" / "assets" / "models"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ATLAS_PATH = OUTPUT_DIR / "sol-ultra-palette.png"
GLB_PATH = OUTPUT_DIR / "sol-ultra-diorama.glb"
REPORT_PATH = OUTPUT_DIR / "sol-ultra-diorama.json"

INCLUDED_COLLECTIONS = {
    "TERRAIN",
    "BACKGROUND",
    "CABIN",
    "ROOF",
    "PORCH",
    "PROPS",
    "VEGETATION",
    "DETAILS",
}

# These two trees were deliberately placed to crop the original camera frame.
# Removing them from the derivative viewer keeps the cabin readable while the
# user orbits. They remain unchanged in the benchmark .blend and final render.
EXCLUDED_PREFIXES = (
    "Peach sunset sky",
    "Subtle atmospheric volume",
    "Near left crop pine",
    "Near right crop pine",
)

EMISSIVE_MATERIALS = {"Window Glow", "Window Core"}
WATER_MATERIALS = {"Distant Water"}

ATLAS_SIZE = 256
ATLAS_COLUMNS = 8


def material_base_color(material: bpy.types.Material) -> tuple[float, float, float, float]:
    """Read the authored Principled color, with a diffuse-color fallback."""
    if material and material.use_nodes and material.node_tree:
        principled = material.node_tree.nodes.get("Principled BSDF")
        if principled:
            socket = principled.inputs.get("Base Color")
            if socket:
                return tuple(float(value) for value in socket.default_value)
    if material:
        return tuple(float(value) for value in material.diffuse_color)
    return (0.5, 0.5, 0.5, 1.0)


def material_group(material: bpy.types.Material) -> str:
    if material.name in EMISSIVE_MATERIALS:
        return "emissive"
    if material.name in WATER_MATERIALS:
        return "water"
    if material.use_nodes and material.node_tree:
        principled = material.node_tree.nodes.get("Principled BSDF")
        if principled:
            metallic = principled.inputs.get("Metallic")
            if metallic and float(metallic.default_value) > 0.1:
                return "metal"
    return "matte"


def source_objects() -> list[bpy.types.Object]:
    selected = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        if not any(collection.name in INCLUDED_COLLECTIONS for collection in obj.users_collection):
            continue
        if obj.name.startswith(EXCLUDED_PREFIXES):
            continue
        selected.append(obj)
    return selected


def used_materials(objects: list[bpy.types.Object]) -> list[bpy.types.Material]:
    materials = {}
    for obj in objects:
        for slot in obj.material_slots:
            if slot.material:
                materials[slot.material.name] = slot.material
    return [materials[name] for name in sorted(materials)]


def build_palette(materials: list[bpy.types.Material]):
    rows = math.ceil(len(materials) / ATLAS_COLUMNS)
    cell_width = ATLAS_SIZE // ATLAS_COLUMNS
    cell_height = ATLAS_SIZE // rows
    pixels = [0.0] * (ATLAS_SIZE * ATLAS_SIZE * 4)
    uv_by_material = {}

    for index, material in enumerate(materials):
        column = index % ATLAS_COLUMNS
        row = index // ATLAS_COLUMNS
        color = material_base_color(material)
        start_x = column * cell_width
        end_x = ATLAS_SIZE if column == ATLAS_COLUMNS - 1 else (column + 1) * cell_width
        start_y = row * cell_height
        end_y = ATLAS_SIZE if row == rows - 1 else (row + 1) * cell_height
        for y in range(start_y, end_y):
            row_offset = y * ATLAS_SIZE * 4
            for x in range(start_x, end_x):
                offset = row_offset + x * 4
                pixels[offset:offset + 4] = color
        uv_by_material[material.name] = (
            (start_x + (end_x - start_x) * 0.5) / ATLAS_SIZE,
            (start_y + (end_y - start_y) * 0.5) / ATLAS_SIZE,
        )

    image = bpy.data.images.get("Sol Ultra web palette")
    if image:
        bpy.data.images.remove(image)
    image = bpy.data.images.new(
        "Sol Ultra web palette",
        width=ATLAS_SIZE,
        height=ATLAS_SIZE,
        alpha=True,
        float_buffer=False,
    )
    image.colorspace_settings.name = "sRGB"
    image.pixels.foreach_set(pixels)
    image.filepath_raw = str(ATLAS_PATH)
    image.file_format = "PNG"
    image.save()
    image.pack()
    return image, uv_by_material, rows


def make_atlas_material(name: str, image: bpy.types.Image, group: str) -> bpy.types.Material:
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (420, 0)
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    principled.location = (100, 0)
    texture = nodes.new("ShaderNodeTexImage")
    texture.location = (-260, 40)
    texture.image = image
    texture.interpolation = "Closest"
    texture.extension = "CLIP"

    links.new(texture.outputs["Color"], principled.inputs["Base Color"])
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])

    principled.inputs["Roughness"].default_value = 0.76
    if group == "metal":
        principled.inputs["Metallic"].default_value = 0.5
        principled.inputs["Roughness"].default_value = 0.44
    elif group == "water":
        principled.inputs["Metallic"].default_value = 0.08
        principled.inputs["Roughness"].default_value = 0.28
    elif group == "emissive":
        links.new(texture.outputs["Color"], principled.inputs["Emission Color"])
        principled.inputs["Emission Strength"].default_value = 2.8
        principled.inputs["Roughness"].default_value = 0.26

    material.diffuse_color = (0.5, 0.5, 0.5, 1.0)
    return material


def evaluated_mesh(obj: bpy.types.Object, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(
        evaluated,
        preserve_all_data_layers=False,
        depsgraph=depsgraph,
    )
    return evaluated, mesh


def combine_group(
    name: str,
    group: str,
    objects: list[bpy.types.Object],
    atlas_material: bpy.types.Material,
    uv_by_material: dict[str, tuple[float, float]],
    depsgraph,
) -> tuple[bpy.types.Object | None, int]:
    vertices = []
    faces = []
    face_materials = []

    for source in objects:
        evaluated, mesh = evaluated_mesh(source, depsgraph)
        matrix = evaluated.matrix_world
        vertex_offset = len(vertices)
        vertices.extend(tuple(matrix @ vertex.co) for vertex in mesh.vertices)

        slots = [slot.material for slot in source.material_slots]
        for polygon in mesh.polygons:
            if slots:
                slot_index = min(polygon.material_index, len(slots) - 1)
                source_material = slots[slot_index]
            else:
                source_material = None
            if not source_material or material_group(source_material) != group:
                continue
            faces.append(tuple(vertex_offset + index for index in polygon.vertices))
            face_materials.append(source_material.name)
        bpy.data.meshes.remove(mesh)

    if not faces:
        return None, 0

    mesh = bpy.data.meshes.new(f"{name} mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(atlas_material)
    mesh.validate(clean_customdata=False)
    mesh.update(calc_edges=True)
    uv_layer = mesh.uv_layers.new(name="Palette UV")
    for polygon, material_name in zip(mesh.polygons, face_materials):
        polygon.use_smooth = False
        uv = uv_by_material[material_name]
        for loop_index in polygon.loop_indices:
            uv_layer.data[loop_index].uv = uv

    obj = bpy.data.objects.new(name, mesh)
    export_collection.objects.link(obj)
    obj["source"] = "GPT-5.6 Sol Ultra benchmark"
    obj["web_optimization"] = "palette-atlased and draw-call merged"
    return obj, len(mesh.polygons)


objects = source_objects()
materials = used_materials(objects)
palette_image, palette_uvs, atlas_rows = build_palette(materials)

export_collection = bpy.data.collections.get("WEB_EXPORT")
if export_collection:
    for existing in list(export_collection.objects):
        bpy.data.objects.remove(existing, do_unlink=True)
else:
    export_collection = bpy.data.collections.new("WEB_EXPORT")
    bpy.context.scene.collection.children.link(export_collection)

atlas_materials = {
    group: make_atlas_material(f"Web {group.title()}", palette_image, group)
    for group in ("matte", "metal", "water", "emissive")
}

depsgraph = bpy.context.evaluated_depsgraph_get()
objects_by_group = {group: [] for group in atlas_materials}
for obj in objects:
    groups = {
        material_group(slot.material)
        for slot in obj.material_slots
        if slot.material
    }
    for group in groups:
        objects_by_group[group].append(obj)

created = []
polygon_counts = {}
for group, group_objects in objects_by_group.items():
    combined, polygon_count = combine_group(
        f"Sol Ultra {group.title()}",
        group,
        group_objects,
        atlas_materials[group],
        palette_uvs,
        depsgraph,
    )
    if combined:
        created.append(combined)
        polygon_counts[group] = polygon_count

bpy.ops.object.select_all(action="DESELECT")
for obj in created:
    obj.select_set(True)
    obj.hide_render = False
    obj.hide_set(False)
bpy.context.view_layer.objects.active = created[0]

bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_cameras=False,
    export_lights=False,
    export_materials="EXPORT",
    export_texcoords=True,
    export_normals=True,
    export_tangents=False,
    export_attributes=False,
    export_extras=True,
    export_yup=True,
)

report = {
    "source_file": "gpt-5.6-sol-ultra/cozy_forest_cabin.blend",
    "source_mesh_objects": len(objects),
    "source_materials_used": len(materials),
    "web_meshes": len(created),
    "web_polygons_by_group": polygon_counts,
    "palette": {
        "file": ATLAS_PATH.name,
        "size": [ATLAS_SIZE, ATLAS_SIZE],
        "columns": ATLAS_COLUMNS,
        "rows": atlas_rows,
    },
    "excluded": list(EXCLUDED_PREFIXES),
    "unoptimized_glb_bytes": GLB_PATH.stat().st_size,
}
REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

print("WEB_MODEL_REPORT", json.dumps(report, sort_keys=True))
