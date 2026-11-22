"""Create a Blender reference scene from six already cropped PNGs. No modeling."""
from pathlib import Path
import argparse
import json
import math
import sys

import bpy
from mathutils import Matrix, Vector

ANGLES = ("000", "045", "090", "135", "180")
VIEWS = (*ANGLES, "top")


def number(obj, label, *, lo=None, hi=None):
    if isinstance(obj, bool) or not isinstance(obj, (int, float)) or not math.isfinite(obj):
        raise ValueError(f"{label}: expected a finite number")
    if (lo is not None and obj < lo) or (hi is not None and obj > hi):
        raise ValueError(f"{label}: number outside [{lo}, {hi}]")
    return float(obj)


def pair(obj, label):
    if not isinstance(obj, list) or len(obj) != 2:
        raise ValueError(f"{label}: expected [x, y]")
    return tuple(number(value, label) for value in obj)


def image_path(manifest, relative, name):
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError(f"{name}: image path is required")
    p = Path(relative)
    if not p.is_absolute():
        p = manifest.parent / p
    if p.suffix.lower() != ".png" or not p.is_file():
        raise ValueError(f"{name}: expected a readable PNG: {p}")
    return p.resolve()


def positive(value, label):
    return number(value, label, lo=1e-6)


def validate(manifest):
    m = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(m, dict) or type(m.get("schema_version")) is not int or m["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    views = m.get("views")
    if not isinstance(views, dict) or set(views) != set(VIEWS):
        raise ValueError("views must have exactly 000, 045, 090, 135, 180, top")
    height = positive(m.get("standing_height"), "standing_height")
    ground = number(m.get("ground_z", 0), "ground_z")
    distance = positive(m.get("plane_distance", 1.2 * height), "plane_distance")
    span = positive(m.get("camera_span", 1.3 * height), "camera_span")
    result = {}
    side_center = number(m.get("side_camera_center_u", 0), "side_camera_center_u")
    for key in VIEWS:
        u = views[key]
        if not isinstance(u, dict):
            raise ValueError(f"views.{key} must be an object")
        src = image_path(manifest, u.get("image"), key)
        if key == "top":
            if u.get("front_direction") != "down":
                raise ValueError("top.front_direction must be 'down'; rotate the source before registration")
            px = pair(u.get("anchor_px"), "top.anchor_px")
            xy = pair(u.get("anchor_world_xy"), "top.anchor_world_xy")
            unit = positive(u.get("units_per_px"), "top.units_per_px")
            bottom = number(u.get("plane_z", ground - height * 0.1), "top.plane_z")
            if bottom >= ground:
                raise ValueError("top.plane_z must be below the ground to act as an underneath guide")
            top_center = pair(u.get("camera_center_xy", list(xy)), "top.camera_center_xy")
            top_span = positive(u.get("camera_span", span), "top.camera_span")
            result[key] = dict(path=src, px=px, xy=xy, unit=unit, plane_z=bottom,
                               camera_center=top_center, camera_span=top_span)
        else:
            head = number(u.get("top_y_px"), f"{key}.top_y_px", lo=0)
            sole = number(u.get("sole_y_px"), f"{key}.sole_y_px", lo=0)
            foot = number(u.get("sole_center_x_px"), f"{key}.sole_center_x_px", lo=0)
            sole_world = number(u.get("sole_world_u", 0), f"{key}.sole_world_u")
            if sole <= head:
                raise ValueError(f"{key}: top_y_px must be above sole_y_px")
            result[key] = dict(path=src, head=head, sole=sole, foot=foot, sole_world=sole_world)
    name = m.get("scene_name", "Voxel reference studio")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("scene_name must be a nonempty string")
    return name, height, ground, distance, span, side_center, result


def link_collection(parent, name):
    c = bpy.data.collections.new(name)
    parent.children.link(c)
    return c


def reference_material(image):
    material = bpy.data.materials.new(f"Reference • {image.name}")
    material.use_nodes = True
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "DITHERED"
    elif hasattr(material, "blend_method"):
        material.blend_method = "HASHED"
    tree = material.node_tree
    tree.nodes.clear()
    image_node = tree.nodes.new("ShaderNodeTexImage")
    image_node.image = image
    image_node.extension = "CLIP"
    image_node.interpolation = "Linear"
    emission = tree.nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 1
    transparent = tree.nodes.new("ShaderNodeBsdfTransparent")
    mix = tree.nodes.new("ShaderNodeMixShader")
    output = tree.nodes.new("ShaderNodeOutputMaterial")
    tree.links.new(image_node.outputs["Color"], emission.inputs["Color"])
    tree.links.new(image_node.outputs["Alpha"], mix.inputs[0])
    tree.links.new(transparent.outputs[0], mix.inputs[1])
    tree.links.new(emission.outputs[0], mix.inputs[2])
    tree.links.new(mix.outputs[0], output.inputs[0])
    return material


def axes(key):
    if key == "top":
        return Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    t = math.radians(int(key))
    return (Vector((math.cos(t), math.sin(t), 0)), Vector((0, 0, 1)),
            Vector((math.sin(t), -math.cos(t), 0)))


def basis(right, up, eye, unit=1.0):
    return Matrix((right * unit, up * unit, eye)).transposed().to_4x4()


def record_matrix(m):
    return [list(row) for row in m]


def create(manifest, out):
    if out.suffix.lower() != ".blend":
        raise ValueError("output name must end in .blend")
    if out.exists() or out.is_symlink():
        raise FileExistsError(f"refusing to overwrite: {out}")
    if not out.parent.is_dir():
        raise ValueError(f"output parent does not exist: {out.parent}")
    name, height, ground, distance, span, camera_u, specs = validate(manifest)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = name
    scene.render.resolution_x = scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "Standard"
    scene["coordinate_axes"] = "+X right; -Y front; +Z up. Pixels use top-left image edges."
    scene["standing_height"] = height
    scene["ground_z"] = ground
    scene["guide_usage"] = "Show one reference at a time in the Outliner. Use Material Preview to see PNG colors."
    refs = link_collection(scene.collection, "01 · REFERENCE PLANES")
    cameras = link_collection(scene.collection, "02 · ORTHOGRAPHIC CAMERAS")
    info = {}
    for key, spec in specs.items():
        r, u, n = axes(key)
        image = bpy.data.images.load(str(spec["path"]), check_existing=False)
        w, h = map(int, image.size)
        if min(w, h) <= 0:
            raise ValueError(f"{key}: Blender could not decode image")
        image.name = f"GUIDE {key}"
        image.pack()
        if not image.packed_file:
            raise RuntimeError(f"{key}: could not pack image")
        # The source can disappear when the .blend travels; do not bake an external absolute path.
        image.filepath = f"//GUIDE-{key}.png"
        if image.channels < 4:
            print(f"{key}: opaque input; check reference overlap in the viewport.", flush=True)
        if key == "top":
            px, py = spec["px"]
            number(px, "top.anchor_px.x", lo=0, hi=w)
            number(py, "top.anchor_px.y", lo=0, hi=h)
            unit = spec["unit"]
            ax, ay = spec["xy"]
            anchor = Vector((ax, ay, spec["plane_z"]))
            lower_left = anchor - r * (px * unit) - u * ((h - py) * unit)
            c0 = Vector((*spec["camera_center"], ground + height / 2))
            cspan = spec["camera_span"]
        else:
            foot, sole, head = spec["foot"], spec["sole"], spec["head"]
            number(foot, f"{key}.sole_center_x_px", lo=0, hi=w)
            number(sole, f"{key}.sole_y_px", lo=0, hi=h)
            number(head, f"{key}.top_y_px", lo=0, hi=h)
            unit = height / (sole - head)
            anchor = r * spec["sole_world"] + u * ground - n * distance
            lower_left = anchor - r * (foot * unit) - u * ((h - sole) * unit)
            c0 = r * camera_u + u * (ground + height / 2)
            cspan = span
        matrix = basis(r, u, n, unit)
        matrix.translation = lower_left

        sub = link_collection(refs, f"REF {key}")
        mesh = bpy.data.meshes.new(f"Ref plane {key}")
        mesh.from_pydata([(0, 0, 0), (w, 0, 0), (w, h, 0), (0, h, 0)], [], [(0, 1, 2, 3)])
        mesh.update()
        uv = mesh.uv_layers.new(name="Image UV")
        for loop_index, uv_xy in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
            uv.data[loop_index].uv = uv_xy
        ref = bpy.data.objects.new(f"REF {key}", mesh)
        sub.objects.link(ref)
        ref.matrix_world = matrix
        mesh.materials.append(reference_material(image))
        ref["units_per_px"] = unit
        ref["image_size_px"] = [w, h]
        ref["guide_only"] = key == "top"
        ref.hide_set(key != "000")
        ref.hide_render = key != "000"

        data = bpy.data.cameras.new(f"ORTHO {key}")
        data.type = "ORTHO"
        data.ortho_scale = cspan
        data.clip_end = max(1000, (height + distance) * 8)
        cam = bpy.data.objects.new(f"ORTHO {key}", data)
        cameras.objects.link(cam)
        mcam = basis(r, u, n)
        mcam.translation = c0 + n * (distance + 2*height)
        cam.matrix_world = mcam
        if key == "000":
            scene.camera = cam
        info[key] = dict(size_px=[w, h], units_per_px=unit,
                         pixel_bottom_left_to_world=record_matrix(matrix),
                         front_approximate=(key == "top"))

    scene.world = bpy.data.worlds.new("Dim studio")
    scene.world.color = (0.09, 0.10, 0.13)
    guide = bpy.data.texts.new("READ ME · reference setup")
    guide.write("Model geometry is not created by this utility. The six packed image planes "
                "are construction guides. Use the matching camera and show only the matching REF "
                "object; viewport eye and render camera toggles are independent. "
                "Top alignment is an approximate guide, not calibrated orthographic ground truth.\n\n"
                + json.dumps(info, indent=2))
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                sp = area.spaces.active
                sp.region_3d.view_perspective = "CAMERA"
                sp.shading.type = "MATERIAL"
                sp.clip_end = max(1000, (height + distance)*8)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
    print(f"REGISTERED {len(info)} packed reference planes into {out}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output_blend", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    create(args.manifest.resolve(), args.output_blend.absolute())


if __name__ == "__main__":
    main()
