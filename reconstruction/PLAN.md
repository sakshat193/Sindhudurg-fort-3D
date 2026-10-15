# Sindhudurg reconstruction — 13 October 2026

SCENE
- intent: a present-day, rough but geographically faithful Sindhudurg model.
- deliverable: editable `Sindhudurg_1to1` Blender scene and procedural source.
- units: metres; axes: right-handed Z-up; +X east, +Y north; sea Z=0.
- render: existing Cycles retained; inspection previews may use EEVEE; 1920x1080.
- dynamic: restrained optional inspection-camera orbit; architecture is stationary.

HIERARCHY
- collection/object naming: SD2_ semantic names, grouped by terrain, walls, interior,
  vegetation, reference and presentation.
- parent/child relationships: fort structures anchored in one local geographic frame.
- protected existing objects: ALL original objects and the original Sindhudurg scene.

ASSETS
- A01 mapped rampart | [BLOCK] | blockout | satellite-derived metric dimensions
  | editable planar trace | wall height 9.144m, thickness 3.6576m.
- A02 terrain/shore | [BLOCK] | blockout | mapped island extent | sea Z=0
  | elevations are estimates because no usable ground survey is supplied.
- A03 temples/wells/settlement | [EXISTING] | blockout | reuse existing semantic
  meshes; relocate visible structures to mapped footprints; uncertain identity,
  dimensions and obscured positions explicitly tagged rather than called measured.
- A03b bastion fighting terraces | [BLOCK] | blockout | 42 terrace features;
  33 clear projecting arcs, nine provisional corner/entry identifications.
  Outer contours remain mapped; rear terrace depths are estimates. Terraces,
  embrasures and stairs follow the evaluated rampart height through Geometry Nodes.
- A04 coconut/broadleaf/scrub/grass | [BLOCK] | recognizable rough species forms
  | seeded Geometry Nodes instances; mapped canopy density; clearance masks.
  Coconut and broadleaf share Poisson occupancy; spacing is bounded by the
  largest scaled prototype radius. Scrub reserves distance from trees, and grass
  reserves distance from both. Proximity operates on points/flat structural
  footprints, including the live wall width, without realizing instances.
- A05 jetty/paths | [BLOCK] | blockout | trace satellite pixels into metric coordinates.
- A06 cameras/sun/water | [EXISTING/BLOCK] | inspection/presentation.
- generation estimate/submission: no generation and no credit spending.

SHOT
- active camera: SD2_CAM_Aerial; complementary north-up top orthographic camera.
- framing/lens/target: full island with coastline margin; local origin near centroid.
- depth: ocean foreground, wall/island subject, ocean background.

LOOK
- material roles: dark basalt/lateritic rubble, lime plaster, terracotta roofs,
  tawny grass/soil, green coconut and broadleaf canopy, teal ocean.
- material route: existing materials copied for SD2; local procedural shading.
- texture scale: object/world metric coordinates for roughness and bump.
- relief: bump only; no invented measured masonry detail.
- dielectric: rough stone/soil; low-roughness water; existing metal for props.
- world: restrained daylight fill.

LIGHTING
- focal subject: island perimeter and concealed northeast entrance.
- secondary: central temple/settlement; deepest shade under canopy.
- mood: readable coastal daylight; sun plus modest world fill.
- environment route: existing World copied; no generated HDRI.
- key: oblique Sun for wall height and canopy shadows; no arbitrary extra lights.
- exposure: AgX/existing transform checked, locked for preview comparisons.

MOTION
- optional 24fps inspection orbit, with a stable aerial rest pose.
- no structural animation or simulated flora required for geographic accuracy.

ACCEPTANCE
- structural: metric units, trace aligned to satellite, documented dimensions,
  original scene intact, named editable parts, GN vegetation with unrealized instances.
- plant overlap: positive conservative XY footprint clearance for all same and
  cross-category instance pairs; density/seed/spacing edits retain minimum spacing.
- motion: inspection camera stays aimed at the island; static top camera remains useful.
- visual: north-up footprint and aerial silhouette reviewed; no floating buildings,
  vegetation in ocean/on paths, missing textures or implausibly uniform forest.
- accuracy: trace perimeter/area measured; do not distort footprint merely to force
  published rounded 48-acre/3km values. Wall heights and interior elevations clearly
  distinguish nominal published dimensions from measured survey data.

refs_read: blender-scene, blender-scene-spec, blender-modeling, blender-lookdev,
blender-lighting-camera, blender-animation, blender-audit-finalize, blender-volatile.

Phases: A inspect/research/passport; B recovery checkpoint; C footprint/proportion/
contact/camera gate; D procedural geometry, flora and materials; E structural and
visual checks, recovery deliverable, restore useful Blender view.

Sources:
- Supplied `SAT/GOOGLE_SAT_WM.tif` and six-value worldfile; Web Mercator ground
  distances require local cosine(latitude) correction.
- https://maharashtratourism.gov.in/fort/sindhudurg/ — 48 acres, 30ft, 12ft.
- https://indiacinehub.gov.in/index.php/location/sindhudurg-fort — 42 bastions,
  concealed gate and freshwater wells.
- https://whc.unesco.org/en/list/1739/maps/ — component 1739-011, 19.11ha property
  (heritage-property area is a cross-check, not a wall footprint scale constraint).
- https://tourism.webindia123.com/tourism/monuments/forts/Sindhudurg_Fort/index.htm
  — coconut groves inside the fort.
- https://en.wikipedia.org/wiki/Sindhudurg_district — regional mango/cashew/kokum;
  insufficient evidence for island-specific tree proportions.

Accuracy limits: satellite approximately 1.15 ground metres per pixel; manual wall
trace approximately 2–4m uncertainty. Ground/roof elevations and obscured features
are provisional. This is a 1:1 metre-scale reconstruction, not a survey certification.
