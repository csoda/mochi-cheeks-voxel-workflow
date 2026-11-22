"""Exercise the public registration command and reopen a real Blender file."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile

FILE=Path(__file__).resolve()
ROOT=FILE.parents[1]
EXAMPLE=ROOT/"examples"/"bolt-bot"
HELPER=ROOT/"skills"/"voxel-character-workflow"/"scripts"/"register_blender_refs.py"
EPS=2e-5


def ensure(condition,label):
    if not condition:raise AssertionError(label)


def verify(manifest):
    import bpy
    from mathutils import Vector

    with manifest.open(encoding="utf-8") as f:
        m=json.load(f)
    settings=m["views"]
    scene=bpy.context.scene
    guide=bpy.data.collections["01 · REFERENCE PLANES"]
    ensure(len(guide.children)==6,"expected six separate reference collections")
    ensure(len([o for o in scene.objects if o.type=="CAMERA"])==6,"six cameras")
    ensure(len([o for o in scene.objects if o.type=="MESH"])==6,"six planes, no other geometry")
    ensure(scene.camera.name=="ORTHO 000","active front camera")
    sizes=set()
    for key,view in settings.items():
        ensure(not (manifest.parent/view["image"]).exists(),"fixture PNG removed before reopen")
        p=bpy.data.objects[f"REF {key}"]
        cam=bpy.data.objects[f"ORTHO {key}"]
        ensure(cam.data.type=="ORTHO","orthographic camera")
        ensure(p.hide_get()==(key!="000") and p.hide_render==(key!="000"),"independent view visibility")
        material=p.data.materials[0]
        img=next(n.image for n in material.node_tree.nodes if n.type=="TEX_IMAGE")
        ensure(img.packed_file and img.filepath==f"//GUIDE-{key}.png","portable embedded image")
        w,h=img.size
        sizes.add((w,h))
        rows=img.pixels[:][3::4]
        ys=[i//w for i,pix in enumerate(rows) if pix>.5]
        ensure(ys and max(ys)>min(ys),"loaded real nonempty alpha data from packed PNG")
        ensure(len(ys)<w*h,"transparent background exists")
        q=p.matrix_world
        project=lambda x,y:q@Vector((x,h-y,0))  # manifest uses a top-left origin
        if key=="top":
            ensure(abs(img.pixels[(int(view["anchor_px"][0])+w*(h-1-int(view["anchor_px"][1])))*4+3]-1)<EPS,
                   "top anchor goes through visible test geometry")
            axis=((1,0,0),(0,1,0),(0,0,1))
            u=project(*view["anchor_px"])
            ensure((u.xy-Vector(view["anchor_world_xy"])).length<EPS and u.z<m["ground_z"],
                   "top anchor below ground points down to front")
            ensure(abs(p["units_per_px"]-view["units_per_px"])<EPS,"top image uniform scale")
        else:
            a=math.radians(int(key))
            axis=((math.cos(a),math.sin(a),0),(0,0,1),(math.sin(a),-math.cos(a),0))
            sole=project(view["sole_center_x_px"],view["sole_y_px"])
            head=project(view["sole_center_x_px"],view["top_y_px"])
            ensure(abs(sole.dot(Vector(axis[0]))-view["sole_world_u"])<EPS,"projected midpoint anchor")
            ensure(abs(sole.z-m["ground_z"])<EPS,"common foot floor")
            ensure(abs(head.z-sole.z-m["standing_height"])<EPS,"common crown-to-sole height")
            expected_y=(h-1-max(ys),h-min(ys))
            ensure(expected_y==(view["top_y_px"],view["sole_y_px"]),"actual image extrema match landmarks")
        for i,v in enumerate(axis):
            ensure((q.col[i].to_3d().normalized()-Vector(v)).length<EPS,"real plane orientation")
            ensure((cam.matrix_world.col[i].to_3d()-Vector(v)).length<EPS,"matching camera orientation")
        want=view.get("camera_span",m["camera_span"])
        ensure(abs(cam.data.ortho_scale-want)<EPS,"camera span")
    ensure(len(sizes)==6,"example mixed image sizes")
    print("Blender reopen passed: six embedded PNGs, transforms, floor, crown, visibility, no generated model.")


def run(argv,expect=0,contains=None):
    code=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
    if code.returncode!=expect or (contains and contains not in code.stdout):
        print(code.stdout)
        raise SystemExit(f"Unexpected Blender result: exit {code.returncode}, wanted {expect}")
    return code.stdout


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def smoke():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--blender",default="blender",help="Blender executable path")
    args=ap.parse_args()
    if not shutil.which(args.blender):
        raise SystemExit("Blender executable not found. Provide --blender /path/to/blender.")
    with tempfile.TemporaryDirectory(prefix="voxel-reference-smoke-") as tmp:
        d=Path(tmp)
        ex=d/"plates"
        shutil.copytree(EXAMPLE,ex)
        manifest=ex/"manifest.json"
        blend=d/"example.blend"
        cmd=[args.blender,"--background","--python-exit-code","1","--python",str(HELPER),"--"]
        print(run(cmd+[str(manifest),str(blend)],contains="REGISTERED 6 packed reference planes").strip())
        original=digest(blend)
        run(cmd+[str(manifest),str(blend)],expect=1,contains="refusing to overwrite")
        ensure(digest(blend)==original,"existing output unchanged")
        m=json.loads(manifest.read_text(encoding="utf-8"))
        m["views"]["top"]["front_direction"]="left"
        bad=ex/"bad.json"
        bad.write_text(json.dumps(m),encoding="utf-8")
        bad_out=d/"bad.blend"
        run(cmd+[str(bad),str(bad_out)],expect=1,contains="front_direction must be 'down'")
        ensure(not bad_out.exists(),"bad manifest did not create output")
        for p in ex.glob("*.png"):
            p.unlink()
        confirm=[args.blender,"--background",str(blend),"--python-exit-code","1",
                 "--python",str(FILE),"--","--verify",str(manifest)]
        print(run(confirm,contains="Blender reopen passed").strip())
    print("Smoke test passed; no output files retained.")


if __name__=="__main__":
    # Blender can add its own CLI arguments ahead of the separator.
    if "--" in sys.argv and "--verify" in sys.argv:
        verify(Path(sys.argv[sys.argv.index("--verify")+1]))
    else:
        smoke()
