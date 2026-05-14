from __future__ import annotations

from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = [
    {
        "path": ROOT / "parts" / "hair" / "main_hair.blend",
        "collection": "CHR_Hair_Main",
        "label": "Hair",
        "primitive": "uv_sphere",
        "location": (-1.2, 0.0, 1.7),
        "scale": (0.55, 0.35, 0.18),
        "color": (0.65, 0.22, 0.08, 1.0),
    },
    {
        "path": ROOT / "parts" / "body" / "base_body.blend",
        "collection": "CHR_Body_Base",
        "label": "Body",
        "primitive": "cube",
        "location": (0.0, 0.0, 0.7),
        "scale": (0.5, 0.28, 0.95),
        "color": (0.34, 0.55, 0.78, 1.0),
    },
    {
        "path": ROOT / "parts" / "face" / "main_face.blend",
        "collection": "CHR_Face_Main",
        "label": "Face",
        "primitive": "uv_sphere",
        "location": (0.0, -0.03, 1.55),
        "scale": (0.32, 0.25, 0.32),
        "color": (0.9, 0.66, 0.5, 1.0),
    },
    {
        "path": ROOT / "parts" / "accessories" / "glasses.blend",
        "collection": "CHR_ACC_Glasses",
        "label": "Accessories",
        "primitive": "torus",
        "location": (0.0, -0.32, 1.58),
        "scale": (0.38, 0.12, 0.06),
        "color": (0.08, 0.08, 0.08, 1.0),
    },
]


def main() -> None:
    for fixture in FIXTURES:
        create_part_file(fixture)
    create_integration_file()
    print("BLPVM_FIXTURES_CREATED")


def create_part_file(fixture: dict) -> None:
    reset_scene()
    collection = bpy.data.collections.new(fixture["collection"])
    bpy.context.scene.collection.children.link(collection)
    obj = add_primitive(fixture)
    obj.name = f"{fixture['collection']}_Marker"
    obj.data.name = f"{fixture['collection']}_Mesh"
    obj.data.materials.append(make_material(f"{fixture['collection']}_Material", fixture["color"]))
    move_to_collection(obj, collection)
    add_label(fixture["label"], fixture["location"])
    fixture["path"].parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(fixture["path"]))


def create_integration_file() -> None:
    reset_scene()
    for fixture in FIXTURES:
        with bpy.data.libraries.load(str(fixture["path"]), link=True) as (data_from, data_to):
            if fixture["collection"] not in data_from.collections:
                raise RuntimeError(f"Missing collection {fixture['collection']} in {fixture['path']}")
            data_to.collections = [fixture["collection"]]
        for collection in data_to.collections:
            if collection and collection.name not in bpy.context.scene.collection.children:
                bpy.context.scene.collection.children.link(collection)
    add_camera_and_light()
    integration_path = ROOT / "integration" / "character_integration.blend"
    integration_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(integration_path))


def reset_scene() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for collection in list(bpy.data.collections):
        if not collection.users:
            bpy.data.collections.remove(collection)
    for material in list(bpy.data.materials):
        bpy.data.materials.remove(material)


def add_primitive(fixture: dict):
    if fixture["primitive"] == "cube":
        bpy.ops.mesh.primitive_cube_add(size=1, location=fixture["location"])
    elif fixture["primitive"] == "torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=0.7, minor_radius=0.08, location=fixture["location"])
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=fixture["location"])
    obj = bpy.context.object
    obj.scale = fixture["scale"]
    return obj


def add_label(text: str, location: tuple[float, float, float]) -> None:
    bpy.ops.object.text_add(location=(location[0], location[1] - 0.65, location[2] + 0.25), rotation=(1.2, 0.0, 0.0))
    obj = bpy.context.object
    obj.name = f"Fixture_Label_{text}"
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.size = 0.18


def add_camera_and_light() -> None:
    bpy.ops.object.light_add(type="AREA", location=(0.0, -3.5, 4.0))
    light = bpy.context.object
    light.name = "Fixture_Area_Light"
    light.data.energy = 450
    light.data.size = 4
    bpy.ops.object.camera_add(location=(0.0, -5.0, 2.4), rotation=(1.2, 0.0, 0.0))
    bpy.context.scene.camera = bpy.context.object


def make_material(name: str, color: tuple[float, float, float, float]):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    return material


def move_to_collection(obj, collection) -> None:
    collection.objects.link(obj)
    for parent in list(obj.users_collection):
        if parent != collection:
            parent.objects.unlink(obj)


if __name__ == "__main__":
    main()
