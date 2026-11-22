# Reference, native block construction, and two-profile-curve checks

## 1. Generate the six-view source art

Start with the approved identity drawing. For a chunky game asset, make the source explicitly block-first: thick stepped forms, large readable color regions and no fine marks that require a finer grid. If the user already supplied approved six views, do not regenerate them. Make fresh drawings before touching the model when the requested change is to the concept.

Use one figure per panel. A useful sheet layout is:

| Top left | Top middle | Top right |
|---|---|---|
| 1. Front (0°) | 2. True side (90°) | 3. Rear (180°) |
| 4. Front oblique (45°) | 5. Rear oblique (135°) | 6. True overhead |

**Prompt template:** “Use the attached approved design as the reference. Draw the same character in the same neutral pose, scale and outfit in six separate panels, using the view order above. Keep asymmetrical features on the same anatomical side. Keep the first five views upright at matched height, with ample gutters and a plain background. Show the real back in the rear oblique, not a nearly side view. Use a straight-down top view, with the front pointing down on the page. Preserve the stepped volume and large color regions. No unrelated props or dramatic perspective.”

Inspect every panel before modeling: compare head-to-body ratio, foot stance, eye placement, which ear is taller, and where the strap, pouch, or raised arm sits. If a panel is drawn from the wrong angle or flips a feature, correct that panel first, keeping the approved art and the other panels unchanged. Review the corrected sheet before building. Six panels do not guarantee six consistent measurements: when residual perspective or impossible overlap disagrees, keep one coherent 3D pose and use the affected cue qualitatively.

## 2. Register the approved views

- Crop each approved panel separately. With X right and Z up, front is −Y and a positive 45° camera sees the nose point screen-left. Check that the drawing really corresponds to that camera; a plausible image number alone is not evidence.
- Pre-crop views; exclude shadows and stray alpha around the character. Mark the same anatomical/extreme height landmark across views (typically crown → soles) and the center of the **boots at the floor**, not the wide hair/skirt bounding-box center. Leave clear margins. Alternate hair ties can change the actual highest strand, in which case choose a consistent height datum instead.
- Register each side image with its own uniform pixels-to-world factor; keep aspect ratio. A 512 px sheet and a 320 px sheet can coexist. The reference and camera transforms are fixed before comparing old/new geometry. Do not silently give the new model better centering, rescale or camera zoom.
- Mark a crown/part landmark for top and choose a plausible scale. The top drawing is a soft guide, not a hard fit target. If it shows face/skirt regions hidden by the actual orthographic top camera, use it for large depth and hair direction only. Do not force five independently generated or drawn views into one hard visual hull.

## 3. Build and compare a real solid grid

- Use front to set widths, face and part placement; true side for head/body depth and waist; rear for wraparound details; the obliques for corner falloff and overlap; overhead for depth footprints and protruding parts. Author the head, torso, limbs and accessories as distinct shapes. Choose a block grid suited to the character, not a cosmetic screenshot size. Retain native mesh/material/occupancy data and render with depth. Export `.vox` for editable cells; a Blender surface mesh is not itself a voxel editor unless rebaked to the native grid.
- Check curl openings and actual face cross-sections at 90°, 135°, and overhead. Use individual changes in depth, spacing and arc (crown, tail, drape), not one global depth scale. True diagonal silhouette may worsen even if side becomes closer; inspect 45°/135° as well.
- Use the source palette as inspiration, not a screen-space image pasted on the visible head. A front-only decal often creates disappearing lashes or awkward diagonal seams. Place iris, lash, cheek and smile in a coherent pattern on the actual block surface. Leave the already approved eye design alone when revising a side outline unless asked otherwise.

- Render the actual voxel occupancy in all six views and place it beside the approved art. Review the parts whose depth changed; silhouette overlap is diagnostic, not an objective to maximize when the drawings disagree. Before delivery, reopen the native export and check the cell layout, palette and part connectivity as appropriate. A turntable should render the same actual model.

## The two profile curves

1. At one calibrated 90° view, identify the eye-base or bridge recess, the tip, a mid-cheek or lip-height point, and the chin. Trace the visible **skin edge** below the fringe. If a bang dominates alpha above the bridge, mark the skin/hair boundary only as visual context or leave that section out of the numeric fit.
2. Annotate the art and before/after renders with the same two colors: eye/bridge-to-tip, then tip-to-cheek-to-chin. If a reference nose would be too strong in a small mascot, keep a restrained turn; deform the lower cheek and chin as well. Native quantization makes true 1-block steps unavoidable.
3. Use the trace as a target for the side contour of a *shared* 3D shape. Shape the transverse cheeks and thickness as you adjust depth. Do not use per-angle colors or move unrelated hair. Both 90° and 270° must show the same underlying construct. Check 0°, 45°, 315° for unexpected double features or damaged negative spaces.
4. If front colors are locked, compare physical first-hit color/mask at true horizontal 0° and record whether eye depth also stayed fixed. Lit renders may differ subtly because true local geometry changes shadows. Report visible changes, not just a score. If measuring silhouette depth, report which rows are sampled and whether the numbers are voxel coordinates or projected pixels.

## Example of scope control

If the front is accepted but the profile looks flat, leave the frontal eye pattern untouched. Rebuild the side silhouette around the eye line, cheek and jaw, then compare front and profile at the same physical scale. A changed shadow is not the same as a changed frontal palette. In a separate static sample, local depth edits improved the side outline while a diagonal still differed from the illustration; report both.
