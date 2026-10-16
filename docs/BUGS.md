# Bugs, fixes and lessons

Every bug found so far, what caused it, and the rule that prevents it. Read this before you change `reconstruction/fort_wall_gn.py`, `web/dist/wall-system.js` or the Blender scenes. Add new entries at the top of the relevant section.

## FortWall generator (`reconstruction/fort_wall_gn.py`)

### Geometry

| Bug | Cause | Fix and rule |
|---|---|---|
| Corners chamfered by about 3 m | Resample Curve at Resolution 3 cuts a chord across each knot. | The resample point nearest each knot snaps onto it. Never rely on resample spacing for corners. |
| Crenel wedges and slivers at concave corners (36 bad merlons out of 283) | Crenels were spaced by spine arc length but cut the parapet about 1.46 m off the spine, so at concave corners they bunched up and cut diagonally. | Space crenels along the parapet's own centreline. Corners that turn more than 20° keep one solid merlon. Measure with the merlon-component metric: min OBB side < 0.35 m or area < 0.2 m². |
| Straight-run merlon slivers (25, then 34 after the corner fix) | **Open.** Not investigated. | Keep the merlon metric in the check loop. |
| Stair feet buried or pinched at protruding inner corners (Stair_25 next to Bastion_2) | The open side, parapet and coping followed the blurred face line, which lies inside the wall at corners. | Set every side of a flight off the true mitered face (`face(t, w)`). The blurred line is only for stationing. Check up-facing stair area per flight: a healthy flight is about 16–18 m² total and 3.5–3.9 m² below 2.5 m. |
| Junction intersections at bastion–wall joins ("these intersections shouldn't be there") | My verification used only top-down inner views. | Verify every bastion with exterior oblique views as well as top-down views. Never claim "clean" from a narrow view set. |
| Bastions detached from the wall | Bastion disks sat off the traced spine. | The wall is chorded through each disk. Slide a detached disk onto the wall (Bastion_41 moved about 4 m). |
| Merlons on bastion junction piers | Crenel cutting ran across the piers. | Junction piers carry no crenels. |
| Walkway steps at bastion platforms | The walkway stayed at wall height. | It ramps to each platform's height over Ramp Run. |
| Ladders clipping into the wall | Ladders followed the spine tangent. | Each ladder is square to the courtyard face. The inner rail has gaps at ladders and stair tops. |
| Core volume −1.66 M (inside-out solid) | The R attribute was read after Instances to Points, so the ring and cut lathes were degenerate. | Store R on the INSTANCE domain before converting. |
| Overlapping parts not unioned | A Manifold boolean doesn't union overlapping components inside one mesh. | Feed separate inputs. EXACT with Self Intersection works but takes 18–29 s; MANIFOLD takes 0.3 s for the same volume. Use MANIFOLD. |
| Open courtyard prism | Extrude leaves the cap open. | Join the flipped fill and merge by distance. |
| A–B–A–B oscillation in the `unfold` fill | Nearest-valid snapping flipped between neighbours. | Forward fill through Accumulate Field. Reversals must be 0. |
| 731 overlaps after per-segment subdivision (patch6) | Subdivision broke station spacing. | Reverted to Resample Curve (52 overlaps). |
| 198 brick overlap pairs | Bricks on upright faces tilted along clamped ramp edges. | Flatten T in `bricks_at` when abs(U.z) > 0.7 (39 left). |
| Decimation raised overlaps from 46 to 76 with no speed gain | 6° kinks in the brick rows. | No decimation. |
| Bastion parapets vanished | The stage-6b variable `ring` shadowed the bastion `ring` solid. | Renamed it to `sid`. Earlier, `def lay()` shadowed the layout dict and was renamed `course`. Use unique names in the builder. |
| Mortar strip on the slab | The slab's `own` was 2. | The slab defaults to own 0 (wall). |
| Unbricked courtyard band at raised bastions | The inner-face top stopped at ZC. | Raise it to the nearest bastion's ZB within R (`zi`). |
| Circle fits 5–13 m off on most bastions | The bastions are polygonal, not round. | Bastions are disks sized by terrace area. |

### Modifier and interface

| Bug | Cause | Fix and rule |
|---|---|---|
| Every modifier value reset to 0 or None after a rebuild | Rebuilding the interface gave the sockets new IDs. `items_tree` lists the output Geometry first, so the "names match" test always failed. | Compare against `['Geometry'] + names`. **Never add, remove or reorder interface inputs.** Append new inputs at the end only. |
| User modifier values lost (Seed, merlons, Ramp Run, Resolution) | I swapped `md.node_group` to a backup group for a baseline. | **Never reassign `md.node_group`.** Snapshot the inputs before any experiment, and tell the user if anything was lost. |
| `md[identifier] = x` raises TypeError | Blender 5.x moved modifier inputs to `md.properties.inputs.Socket_N.value`. | Use `mod_input(md, name)`. Skip the Geometry socket, which has no `.value`. |
| Wrong node input names (`Source_Position`) | The API name differs from the UI label. | Proximity uses `Sample_Position`. The `n()` helper asserts every input name. |
| Wrong argument order | Helper signatures differ. | `m(op, a, b)` takes the op first; `sw(c, false_val, true_val, typ)`. |

### Scenes and data

| Bug | Cause | Fix and rule |
|---|---|---|
| Exported bastions differed from Blender | The user had hand-moved or rescaled 15 empties. | Exports read the live empties. Never overwrite the user's empties. |
| `zslope` TypeError in the spine export | It used a stale length after the spine changed. | Read `spine.length` inside the loop. |
| `Draft1.blend` satellite image missing | It points to the absolute `B:\Blender_Fort_Reconstruction\GOOGLE_SAT_WM.tif`. | **Open.** Relink it to `SAT/GOOGLE_SAT_WM.tif` in Blender. Use relative paths (`//`) for all new images. |
| The embedded `SD2_build_sindhudurg.py` in `Sindhudurg_1to1_Procedural.blend` uses old paths | The 2026-10-17 folder move. | Run `reconstruction/build_sindhudurg.py` from disk. |

## Web viewer (`web/`)

| Bug | Cause | Fix and rule |
|---|---|---|
| Editable walls reject the default design ("overlaps Hanuman") | **Open.** The worker omits the Hanuman clearance that the bake uses. | Pass the same clearances to the worker as `survey.mjs` does. |
| Explore crops the fort at 390 px width | **Open.** | Fit the camera to the fort's bounds on narrow screens. |
| Full wall build takes 52 s (target 6 s) | **Open.** | Profile before optimising. |
| Shore triangles bridged incompatible height fields | One mesh spanned the interior and exterior. | Mesh each side along the exact mapped boundary, then unite the closed solids. |
| Old wall trenches stayed after editing | Terrain was cut once. | Keep a cavity-preserving island source, and subtract the committed wall on each build. |
| Multi-metre shoulder steps at bastion decks | Decks were flat. | Loft decks and parapets against the adjoining wall elevation. |
| A cutter count implied an opening that didn't exist | Only the count was checked. | Require a positive intersection and a continuous roof along each passage. |
| Moved bastions left ghost projections | The source bulge stayed in the curve. | Release an untouched projection to its shoulder chord when the bastion is moved or removed. |
| Merlon rhythm restarted at vertices | Each segment had its own stationing. | Use one stationing rule around the exposed circuit. |
| Rounded masonry edges | Shared vertex normals. | Use separate face normals for the stone mesh. |
| Browser tests could not run outside Codex | The Playwright scripts used a Codex-only runtime path. | Removed. Don't hardcode tool-specific paths in tests. |

## Tools and environment

| Problem | Fix |
|---|---|
| `bl_execute` rejects a `result` that is not a dict | Always set `result = {...}`. |
| `NameError: bpy` in `bl_execute` | Each call is a fresh namespace. Import `bpy` every time. |
| Bridge timeouts on long jobs | The job keeps running. Poll Blender's Responding state with PowerShell `Get-Process`, then read back. Never re-run mutating code after a timeout. |
| The first rebuild froze Blender for several minutes | Node compile. Wait; killing Blender loses the unsaved scene. |
| Headless `blender.exe` from WindowsApps gives "Access is denied" | Use `blender-launcher.exe -b --factory-startup --python-expr ...` through `Start-Process`, and have the script write its output to a file. |
| Euler view rotations framed the wrong side | Use a look-at with `to_track_quat('Z', 'Y')`, and set `view_distance` directly. |
| Evaluated curve objects have no `vertices` or `polygons` | Use `to_mesh()` / `to_mesh_clear()`, or `check()`. |
| bmesh index access fails | Call `ensure_lookup_table()`, or use `me.vertices`. |
| Probing `instances_pointcloud()` gave meaningless positions | Don't use it. |
| A Bash heredoc containing `'''` fails | Write the patch to a .py file and run it. |
| A temporary probe node was left in the group | Remove probe nodes and groups after use. |
| Too-close, perspective or selection-cluttered screenshots | Deselect all, use ortho, and hide the selection outline. Never make visual claims without viewing the screenshot. |
