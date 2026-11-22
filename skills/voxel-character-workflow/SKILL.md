---
name: voxel-character-workflow
description: Build or revise an original character as a solid editable voxel model in Blender, using registered multi-view references, profile silhouette checks, and optional rigging and animation. Use for character turnaround-to-voxel work, art-directed outline revisions, or rigging a previously approved voxel character, not for automatically lifting pixels into 3D.
---

# Voxel character workflow

Use only the user's approved character/reference and current requested stage. Keep that revision and its assets intact. Record which view, face, palette, or silhouette the user already approved; lock those by default during local edits. Prioritize visible contour when a profile reads incorrectly. If the nose is questioned, compare the **eye/bridge → tip** and **tip → cheek/lip → chin** paths separately rather than simply deleting a nose block.

1. **Get a reference decision first.** For this chibi style, start with a small front/45° static sheet, then 0°/45°/90°/135°/180° plus overhead. Read [construction and face](references/construction-and-face.md). A stylized sheet is not a mathematically consistent scan.
2. **Put images in 3D before rebuilding the shape.** Use one uniform scale per side image; set a shared body height, ground and projected boot-sole midpoint; keep cameras fixed. Top is an approximate depth/part-separation guide. For already cropped PNGs, [register_blender_refs.py](scripts/register_blender_refs.py) and the [manifest template](assets/reference-manifest.example.json) make a new packed `.blend` with six switchable planes and matching orthographic cameras. It does not model or touch an existing scene.
3. **Make or edit actual occupied 3D cells.** Sculpt head, limbs, hair and garment volumes, tailored per character. Do not use a stack of view images, image-plane colors or a rescaled 2D mask as a substitute. Check true side, rear and top early. For local sculpt edits, fix the requested region without unasked-for face/body changes; use measured outline evidence to choose between candidates.
4. **Approve static before animation.** Provide readable same-scale views, a versioned native `.vox`, and an optional editable `.blend`. When animation is requested, read [motion and QA](references/motion-and-qa.md). Rebind before reusing motion on another character. Check idle, in-place walk and jump with the same body you actually deliver.
5. **Provide evidence and limits.** Compare fixed before/after cameras, test native volume/palette and protected parts, and distinguish painted appearance, geometry and measured overlap. If pose and shape checks disagree, show the issue rather than optimizing a number. Do not overwrite an approved artifact or imply game integration, publish, install, or upload outside the requested scope.

