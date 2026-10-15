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

## Project files

- `web/`: viewer, shared wall geometry builder, survey, tests, generated meshes and validation results.
- `reconstruction/`: procedural Blender scripts, metric input data, scene files and reconstruction notes. See [the Blender guide](reconstruction/README.md).
- `research_notes/` and `reports/`: source records, confidence limits and geometry/topography brief.
- `SAT/` and `Tree/`: supplied mapping and modelling inputs.
- `web-audit/`: browser checks, screenshots and earlier visual audit evidence.

## Current status — 2026-10-15

The shared v2 wall rebuild and full geometry verification pass. The latest bake has 42 bastions, 46 stair flights and approximately 385,000 rampart triangles. The default outline error is 0.126 m. The surveyed walk-height profile is retained.

Browser checks confirm the baked wall joins, gate/postern openings, sampled stair connection and mapped 1828 parapet toggle. Two findings remain:

- **Editable-wall blocker:** the browser worker omits the Hanuman clearance used by the bake and rejects the default editable wall as overlapping the shrine. The last mapped model is retained.
- At 390 px width, Explore crops the fort slightly at the sides; Plan fits the full fort.

A full wall build takes about 52 seconds, above the six-second target. Editor v2, houses, foliage and the final screenshot pass remain. See [the rework handoff](web/REWORK_PLAN.md) and [latest browser evidence](web-audit/evidence/wall-v2/browser-checks.json).

Source attribution and uncertainty are recorded with the research inputs and survey. Installed dependencies retain their upstream licenses in `web/dist/vendor/`.
