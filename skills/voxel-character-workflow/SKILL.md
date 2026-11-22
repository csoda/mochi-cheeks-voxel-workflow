---
name: voxel-character-workflow
description: Generate and verify six-view character art, then build an editable 3D voxel model from it. Use for character turnaround-to-voxel work, art-directed outline revisions, or optional Blender rigging, not automatic pixel-to-3D reconstruction.
---

# Voxel character workflow

Use only the user's approved character/reference and current requested stage. Keep that revision and its assets intact. Record which view, face, palette, or silhouette the user already approved; lock those by default during local edits. Prioritize visible contour when a profile reads incorrectly. If the nose is questioned, compare the **eye/bridge → tip** and **tip → cheek/lip → chin** paths separately rather than simply deleting a nose block.

1. **Generate and review the six-view art before modeling.** Use the approved concept as the identity reference. Create front, true side, rear, front oblique, rear oblique and overhead views of the same pose; reuse approved six-view art if available. Confirm the angles and track asymmetrical details between views. Read [construction and face](references/construction-and-face.md) for the sheet layout, prompt and checks. A render of a model built from fewer views is not source art for this step.
2. **Register the approved views.** Use one uniform scale per upright image, a shared height/ground and boot-sole midpoint, and fixed cameras. For already cropped PNGs, [register_blender_refs.py](scripts/register_blender_refs.py) and the [manifest template](assets/reference-manifest.example.json) build an optional packed Blender reference scene. The same references can guide native-grid construction without Blender. Treat the top view as depth and occlusion evidence, not a hard mask.
3. **Sculpt the actual 3D cells.** Use all six references to decide which forms need depth, which parts overlap, and how the design continues around the back. Build head, torso, limbs, hair and clothing as distinct volumes on one grid. Do not paste image planes onto the model or stretch a front silhouette. For a local edit, preserve already approved parts and existing files.
4. **Compare all six renders before animation.** Use the same ground, scale and cameras across revisions. Show art next to the actual model, especially the rear oblique and top, and note when a drawing's pose or occlusion cannot be copied literally. Save a versioned native `.vox` and reopen it to check occupied cells and palette. A turntable helps catch angle-dependent issues.
5. **Rig only after static approval when requested.** Read [motion and QA](references/motion-and-qa.md). Rebind before reusing motion on another character. Check action poses and joint continuity with the same model you deliver.

