# Rig, motion and verification

## Rig only the accepted rest shape

- Store/hash the accepted native grid and material palette. Mesh exact exposed faces, and use a true armature or properly connected 3D parts. Keep eyes, mouth and head rigid unless expressive animation is requested. Shoulder/elbow/wrist and hip/knee/ankle are useful starting pivots, not fixed joint counts for every character.
- Separate garment, sleeve and leg *contact* points even if they touch in the rest image. Skin/blend real joints; do not weld unrelated boot↔hem or hand↔skirt contacts. Match outline/palette at rest and verify duplicate hidden contact faces don't become objectionable in motion.
- Put tail and fabric secondary movement on their own layers/bones. Keep lag subtle and check from true profile and oblique. A nice front pose cannot prove rear contact or side readability.
- Reusing relative arm/leg timing (e.g. a one-second chibi cycle) can be useful for comparable limb ratios and locomotion; it does not transfer weights, IK pivots, boot geometry, collisions or floor contacts. Rebind, adjust limb lengths and support volumes, adapt stride/swing and re-render. For very different morphology, make a new motion.

## Motion beats

- **Idle:** quiet 1.5–2 s loop; small breathing motion, near-still face, stable soles. Avoid strong sway unless it suits the character.
- **Walk:** contralateral stride and arm swing, contact/pass/lift/return. Check support exactly at the chosen ground plane. In-place walking moves the supporting foot backward relative to the root, so do not claim zero world-space sliding without root-motion/game integration.
- **Jump:** visible anticipation, push, airborne arc, feet preparing to land, landing compression, recovery. Measure sole height under evaluated deformation, not only the leg bone. Check launch and contact frames at true side.
- Use named editable actions when available. 24 fps is a reasonable starting convention, not a requirement. Match exported clip ranges, avoid duplicating the loop seam frame in preview, and normalize GLB clip times to zero where possible.

## QA before handoff

1. Reopen the exact deliverable. Verify expected actions/labels and pose changes. Re-import animated GLB if offered. GLB does not promise the same skinner/interpolation as Blender.
2. Compare source/rest native occupancy, surface/palette and protected parts. Use depths if protecting a face or a mouth/eye pose across revisions. Validate `.vox` with a decoded occupancy and palette round-trip, or state the actual verification performed.
3. Evaluate floor contact and motion phases, knee/elbow links, and face rigidity across the actual actions. Check 45° plus true right/left profile (rear too if haircut/skirt changes); open rendered frames for visible stretching, overdraw, plate gaps and silhouette jitter. Measure high-percentile as well as worst mesh-edge stretch if geometry gets pulled. Visual inspection is not a full self-collision test.
4. Render previews from the same frozen `.blend` that ships. Compare controlled angles, view target, scale and pose frames. Explain differences introduced by lighting versus shape. Don't claim battery cost, game performance or integration from offline previews.
5. Deliver only the formats requested: editable `.blend`, animated `.glb` if verified, native `.vox` for static and a comparison PNG/GIF/MP4 as useful. Keep the prior high-quality model and previously delivered revision separate.

For example, separating the hidden garment contact surfaces in the rest mesh can stop a glove or boot from pulling an unrelated skirt panel when a bone rotates. Verify each case with posed renders, not only vertex weights.
