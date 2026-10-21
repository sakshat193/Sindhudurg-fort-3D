# Sindhudurg: 1:1 procedural reconstruction

The `reconstruction/` folder holds two Blender pipelines. Inputs and generated JSON/NPZ live in `reconstruction/data/`, preview PNGs in `reconstruction/images/`, and the scenes in `blend/`.

- **FortWall generator** (the `fortwall/` Blender extension at the repo root): the current procedural wall, bastion, gate and stair system. See [FORTWALL.md](FORTWALL.md).
- **1:1 mapped scene** (`build_sindhudurg.py`): the full-site scene described below. `sd_core.py` holds its shared helpers.

Data preparation runs in this order:

1. `prepare_site.py` turns the draft trace into `data/site_data.json` and `images/mapped_plan.png`.
2. `prepare_terrain.py` writes `data/terrain_samples.npz`.
3. `prepare_bastions.py` writes `data/bastion_candidates.json`.

`validate_scene.py` and `render_previews.py` write the validation JSON and preview PNGs.

The superseded low-poly `sd_*` pipeline and the October checkpoint .blend files were removed on 2026-10-17. They remain in git history.

Open **blend/Sindhudurg_1to1_Procedural.blend** and choose the **Sindhudurg_1to1** scene.
The original **Sindhudurg** scene and all 480 original objects are retained.

The fort is modelled in actual ground metres, with east along +X, north along +Y
and mean sea level at Z=0. The user's satellite-aligned trace in `blend/Draft1.blend`
was recovered and corrected for Web Mercator's local scale distortion. The
result encloses **190,112.57 m² (19.01 ha)** with a **2,988.78 m circuit**.
The mapped rampart envelope is approximately **526 × 759 m**.

The rampart's Geometry Nodes modifier exposes a nominal **9.144 m height** and
**3.6576 m thickness**. Height is measured from the assumed exterior toe to the
continuous parapet crest; embrasure cheeks extend another 0.45 m. The actual
projecting bastion shapes come from the trace. The published count of 42 is
recorded as documentary metadata. There are 42 raised fighting terraces following
the mapped perimeter: 33 clear projecting arcs and 9 provisional corner/entry
identifications. Rear deck depths are estimated; no perimeter point was moved to
force the count. Bastion decks, embrasures and stairs follow the live wall height.

The scene includes rough temples, three freshwater wells, a kund, resident
building proxies, ruins, gate/print shelters, paths, a jetty, a beach and rock
shelves. Roof centres and visible routes follow the supplied satellite image.
Building heights, landmark identity where obscured, well positions and terrain
heights remain provisional and are tagged in object custom properties.

## Edit

- `SD2_Wall_Mapped_Rampart`: Geometry Nodes modifier → wall height and thickness.
- `SD2_Occupancy_All_Trees`, `SD2_Occupancy_Scrub`, `SD2_Occupancy_Grass`:
  modifier → density, spacing and seed. Coconut and broadleaf trees share one
  Poisson distribution, with exactly one species per point. Spacing is clamped
  to the largest scaled footprint. Shrubs avoid tree crowns; grass avoids trees
  and shrubs through Geometry Proximity nodes. No instances are realized.
- `SD2_Scatter_Coconut`, `Broadleaf`, `Scrub`, `Grass`: consume those reserved
  points. Do not add independent distributions to these output objects.
- `SD2_Terrain_Interior`: point-domain density attributes sampled from the
  satellite image. Building/path/wall clearances are included in these masks.
- `SD2_Rampart_Embrasures`, `SD2_Rampart_Stairs`, `SD2_Shore_Rocks`: instances.
- `SD2_80_Instance_Assets`: hidden shared prototype meshes for scatter.
- `SD2_CAM_Top_North`: north-up plan inspection. The active aerial camera has
  an optional slow 15° orbit with still rests at frames 1–48 and 192–240.
- Blender's Text Editor: `SD2_RECONSTRUCTION_NOTES` and `SD2_build_sindhudurg.py`.

There are no Realize Instances nodes. Thousands of grass plants, shrubs, rocks
and wall details do not become thousands of Blender objects.
After editing a plant prototype's geometry, rebuild to recalculate its collision
bounds; changes to the provided density/seed/spacing controls remain protected.

To rebuild, run `reconstruction/build_sindhudurg.py` from Blender's Text
Editor (the embedded `SD2_build_sindhudurg.py` copy predates the 2026-10-17
folder move and uses old paths). It reuses assets in the protected original
scene. If relocating the project, update the hardcoded `ROOT` in
`build_sindhudurg.py`, `render_previews.py` and `validate_scene.py`.
`data/site_data.json` holds the metric outline and mapped features;
`data/terrain_samples.npz` holds sampled masks.

## Flora and confidence

Coconut (*Cocos nucifera*) groves are documented inside the fort. Broadleaf
canopies, coastal scrub and seasonal grass are modelled as recognizable rough
morphotypes. Mango, cashew and kokum are regional crops, but that does not
establish island-specific species ratios. No mangrove belt has been invented
around this exposed rocky island. The supplied satellite is visibly drier
than the attached aerial photo; seasonal canopy colour and density can be
changed through materials and scatter controls.

## Accuracy limits

This is a **1:1 metre-scale rough reconstruction, not a surveyed as-built**.
Satellite pixels represent about 1.15 ground metres; allow roughly 2–4 m of
outline/feature-position uncertainty. Interior elevations were estimated at
2.6–4.65 m above the sea. No usable ground elevation survey, measured building
plans, detailed bastion survey or island botanical inventory was supplied.
The footprint has not been stretched to force rounded published dimensions.

Sources and build contract: [PLAN.md](PLAN.md). Structural proof and actual
instance counts: `data/validation.json`. Pairwise same/cross-category footprint proof:
`data/scatter_collision_validation.json`. Preview images: `images/Sindhudurg_aerial.png`,
`images/Sindhudurg_plan.png`, `images/Sindhudurg_interior.png`. No paid AI generation was used.
