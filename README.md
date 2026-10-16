# Sindhudurg Fort 3D

A mapped, metre-scale reconstruction of Sindhudurg Fort with Blender sources and a local Three.js viewer. The model preserves the supplied coordinate frame, 19.01 ha mapped area, 2,989 m circuit, nominal 9.144 m wall height, 3.6576 m mean wall thickness, and 42 bastions. It is a reconstruction with documented estimates, not a measured as-built survey.

## Run the viewer

With Node.js installed:

```sh
cd web
npm ci
node serve.mjs
```

Open http://127.0.0.1:4173/. Built viewer assets are included in `web/dist/`; the viewer has no runtime CDN dependency.

## Rebuild and verify

Run from `web/`:

```sh
node vendor.mjs
node survey.mjs
node build-geometry.mjs
node verify.mjs
node wall-system.test.mjs
```

Keep the project folders together: the survey reads source data from `../research_notes/`.

## Docs

All documentation lives in [`docs/`](docs/):

- [Bugs, fixes and lessons](docs/BUGS.md): read this before you change the generators.
- Web viewer: [README](docs/web/README.md), [wall editor](docs/web/WALL_EDITOR.md), [rework plan](docs/web/REWORK_PLAN.md), [design](docs/web/DESIGN.md), [implementation plan](docs/web/IMPLEMENTATION_PLAN.md).
- Blender: [FortWall generator](docs/reconstruction/FORTWALL.md), [1:1 scene guide](docs/reconstruction/README.md), [sources and build contract](docs/reconstruction/PLAN.md).

`web/AGENTS.md` stays beside the code it governs.

## Project files

- `blend/`: every Blender scene, plus the textures `mangoTree.blend` loads by relative path. `Draft1.blend` holds the original satellite trace; `Full Resconstruction.blend` and `Procedural build.blend` are working scenes; `Sindhudurg_1to1_Procedural.blend` is the 1:1 mapped scene.
- `web/`: the viewer, shared wall builder, survey, tests and generated meshes. Validation results are in `web/validation/`.
- `reconstruction/`: Blender scripts. Inputs and generated JSON/NPZ are in `data/`; preview and trace images are in `images/`.
- `research_notes/` and `reports/`: source records, confidence limits and the geometry/topography brief.
- `SAT/`: satellite and elevation rasters.
- `web-audit/evidence/wall-v2/`: browser evidence for wall v2.

## Current status — 2026-10-17

- **Web viewer:** the shared v2 wall rebuild and full geometry verification pass.
  - The latest bake has 42 bastions, 46 stair flights and approximately 385,000 rampart triangles. The default outline error is 0.126 m.
  - The editable-wall worker still rejects the default design for overlapping the Hanuman shrine, because it omits the bake's clearance.
  - At 390 px width, Explore crops the fort slightly at the sides.
  - A full wall build takes about 52 s, against a 6 s target.
  - Editor v2, houses, foliage and the final screenshot pass remain. See [the rework handoff](docs/web/REWORK_PLAN.md).
- **FortWall (Blender):** traces the real outline with hand-placed bastion and stair empties.
  - Corners are sharp and crenels are spaced on the parapet centreline, with solid corner merlons.
  - Stairs are set off the true wall face.
  - `check()` passes: closed, outward solid.

Source attribution and uncertainty are recorded with the research inputs and survey. Installed dependencies retain their upstream licenses in `web/dist/vendor/`.
