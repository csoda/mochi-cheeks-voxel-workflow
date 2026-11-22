"""Generate the small original orthographic test plates. Standard library only."""
from pathlib import Path
import argparse
import json
import math
import struct
import zlib

# World orientation: +X right, -Y front, +Z up. Only the red cap reaches z=33;
# the lowest foot surfaces share z=-2. Boxes are generated test shapes, not assets.
SHAPES = [
    ((-7,-3.0,-2),(7,4.0,2),(57,70,84)),
    ((-4,-2.4,1),(4,3.4,7),(80,109,115)),
    ((-8,-5,7),(8,5,18),(73,137,141)),
    ((-4,-5.5,9),(4,-4,15),(50,213,188)),
    ((-4,4.4,9),(4,5.4,15),(207,164,74)),
    ((-1,1.2,16),(4,5.9,23),(71,86,109)),
    ((-7.2,-3.4,18),(6.8,3.6,26),(116,148,150)),
    ((-5.5,-4,20),(4.8,-3.3,23),(210,231,194)),
    ((-1.8,-.6,26),(1.8,1.7,30),(90,119,138)),
    ((-2.4,-1.7,30),(2.1,2.1,33),(239,113,103)),
]
POSES = [
    ("000",112,104,2,56,89,0),
    ("045",151,144,3,75,127,math.sqrt(.125)),
    ("090",121,103,2,61,91,.5),
    ("135",168,142,3,82,130,math.sqrt(.125)),
    ("180",132,106,2,62,93,0),
    ("top",124,111,3,66,52,0),
]

def png(path,w,h,rows):
    def chunk(label,d):
        return struct.pack(">I",len(d))+label+d+struct.pack(">I",zlib.crc32(label+d))
    # PNG compression may vary between zlib versions; decoded pixels are deterministic.
    header=struct.pack(">IIBBBBB",w,h,8,6,0,0,0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",header)
                     +chunk(b"IDAT",zlib.compress(b"".join(b"\0"+r for r in rows),9))
                     +chunk(b"IEND",b""))

def pixel(position,eye):
    highest=(-math.inf,None,None)
    for lower,upper,color in SHAPES:
        dmin=-math.inf;dmax=math.inf;side=0
        for i,(p,d) in enumerate(zip(position,eye)):
            if abs(d)<1e-9:
                if not lower[i]<=p<upper[i]:
                    break
                continue
            a,b=sorted(((lower[i]-p)/d,(upper[i]-p)/d))
            dmin=max(dmin,a)
            if b<dmax:
                dmax,side=b,i
        else:
            if dmax>=dmin and dmax>highest[0]:
                highest=(dmax,color,side)
    _,color,axis=highest
    if not color:return (0,0,0,0)
    gain=(.80,.93,1.06)[axis]
    return (*(min(255,round(v*gain)) for v in color),255)

def draw(pose,path):
    key,w,h,ppu,midx,base,sole_world=pose
    if key=="top":
        right,up,eye=(1,0,0),(0,1,0),(0,0,1)
    else:
        a=math.radians(int(key))
        right,up,eye=(math.cos(a),math.sin(a),0),(0,0,1),(math.sin(a),-math.cos(a),0)
    rows=[]
    for y in range(h):
        v=(base-y-.5)/ppu+(-2 if key!="top" else 0)
        row=bytearray()
        for x in range(w):
            u=(x+.5-midx)/ppu+sole_world
            row+=bytes(pixel(tuple(a*u+b*v for a,b in zip(right,up)),eye))
        rows.append(row)
    png(path/f"{key}.png",w,h,rows)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path(__file__).resolve().parent)
    out=parser.parse_args().output
    out.mkdir(parents=True,exist_ok=True)
    settings={
        "schema_version":1,"scene_name":"Bolt bot - registration sample",
        "ground_z":-2,"standing_height":35,"plane_distance":48,"camera_span":50,"views":{}
    }
    for pose in POSES:
        key,_,_,ppu,x,sole,su=pose
        draw(pose,out)
        f=settings["views"]
        if key=="top":
            f[key]={"image":"top.png","front_direction":"down","anchor_px":[x,sole],
                    "anchor_world_xy":[0,0],"units_per_px":1/ppu,"camera_span":30}
        else:
            f[key]={"image":key+".png","top_y_px":sole-35*ppu,"sole_y_px":sole,
                    "sole_center_x_px":x,"sole_world_u":su}
    (out/"manifest.json").write_text(json.dumps(settings,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
