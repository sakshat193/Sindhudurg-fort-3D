# Sindhudurg Fort 3D

A mapped, metre-scale Blender reconstruction of Sindhudurg Fort, built with procedural tools toward a 1:1 replica. The model preserves the supplied coordinate frame, 19.01 ha mapped area, 2,989 m circuit, nominal 9.144 m wall height, 3.6576 m mean wall thickness, and 42 bastions. It is a reconstruction with documented estimates, not a measured as-built survey.

## Docs

All documentation lives in [`docs/`](docs/):

- [Bugs, fixes and lessons](docs/BUGS.md): read this before you change the generators.
- [FortWall generator](docs/reconstruction/FORTWALL.md): install and use the `fortwall/` Blender extension.
- [1:1 scene guide](docs/reconstruction/README.md) and [sources and build contract](docs/reconstruction/PLAN.md).

## Project files

- `fortwall/`: the FortWall Blender extension. `generator.py` builds the node group; `fortwall_nodes.blend` ships it prebuilt.
- `blend/`: every Blender scene, plus the textures `mangoTree.blend` loads by relative path. `Draft1.blend` holds the original satellite trace; `Full Resconstruction_2.blend` is the latest working scene; `Full Resconstruction.blend` and `Procedural build.blend` are earlier working scenes; `Sindhudurg_1to1_Procedural.blend` is the 1:1 mapped scene.
- `reconstruction/`: Blender scripts. Inputs and generated JSON/NPZ are in `data/`; preview and trace images are in `images/`. `data/survey.json` is the consolidated feature map: wall, buildings, gate and postern, wells, kund, stairs, inner walls, shore, terrain grid, and the confidence notes and conflicts.
- `research_notes/` and `reports/`: source records, confidence limits, the geometry/topography brief and the FortWall review.
- `SAT/`: satellite and elevation rasters.

## Current status — 2026-10-22

- **FortWall (Blender):** a packaged extension that traces the real outline with hand-placed bastion and stair empties.
  - The node group ships prebuilt, so adding a fort takes about a second.
  - `check()` passes: one closed, outward solid. Bricks work at every Brick Size.
  - Open: bricks poke out where a stair turns the SE courtyard corner, and straight-run merlon slivers. See [BUGS.md](docs/BUGS.md).
- **Web viewer:** removed on 2026-10-22 to focus on the Blender model. A viewer may return once the model is complete.

Source attribution and uncertainty are recorded with the research inputs and in `reconstruction/data/survey.json`.
