# FortWall Geometry Nodes review — 21 October 2026

What this change does: FortWall converts curves into walls, bastions, arched gates, stairs, masonry and props through one shared Geometry Nodes modifier. The extension is installed and enabled in Blender 5.2.2 LTS. This review adds evidence and reproduction scripts; it does not change the generator or overwrite a Blender scene.

## Must fix

1. **[P1] Empty bastion collections lower walls near the curve origin** (`fortwall/generator.py:225–232`).
   - **What this is:** The crown ramps to the platform height sampled from the nearest bastion.
   - **Problem:** With zero bastions, sampling returns zero, yet the ramp remains active near local (0, 0). A 20 m square's crown drops from 9.144 m to zero; moving the same control points from (100,100) to (0,0) changes volume from 3,134.229 to 2,827.736 m³. Both outputs remain closed, so the current solid check misses it.
   - **Fix:** Bypass the platform-height blend when the bastion point count is zero, preserving the original crown. Prove invariance when translating source points, including a source point exactly at the origin and an empty-but-assigned bastion collection.
   - **If we skip it:** Drawing or converting a valid curve with no bastions can silently produce a collapsed wall.

2. **[P1] Check Solid can certify disconnected walls and missing bricks** (`fortwall/generator.py:789–802`).
   - **What this is:** The check promises one closed, outward-facing core with bricks when enabled.
   - **Problem:** Two separate wall loops produce two core islands, but `check()` returns success: volume 4,866 m³, zero open edges. Blender also exposes an implicit self-instance: with no bricks there is still one instance, and a deliberately substituted closed cube passes `check()` with Bricks enabled, reporting `bricks: 1`. Total positive volume and manifold edges do not establish connectivity or individual island orientation.
   - **Fix:** Check the stage-7 core separately from the intentionally disconnected ladder/flag props. Require one core component, check its orientation, and count actual brick instances or their source points rather than all dependency-graph instances. Return `CANCELLED` from the check operator after a failed assertion.
   - **If we skip it:** Adversarial regression tests can report green while required geometry is absent or detached.

3. **[P2] Installing the extension does not update saved FortWall graphs** (`fortwall/generator.py:751`, `blend/Full Resconstruction_2.blend`).
   - **What this is:** `attach()` reuses a node group by its name; saved Blender files retain their own graphs.
   - **Problem:** The saved latest fort has 2,638 nodes / 4,092 links; source builds 2,646 / 4,108. The saved graph lacks the four empty-Mesh-1 guards already present in source. A no-parts square loaded from that graph grows to Z=200 m and about 57,061 m³, versus Z=10.344 m and 3,134 m³ from source. Reinstalling the Python package leaves that graph unchanged.
   - **Fix:** Rebuild the saved graph from the current generator after taking a recovery copy and recording modifier inputs. For future bundled graphs, record and verify the graph version/source fingerprint before reuse; keep socket identifiers and authored placements intact.
   - **If we skip it:** The installed source and the opened fort can exhibit different bugs and performance.

## Should fix

4. **[P2] First use constructs the entire graph synchronously** (`fortwall/generator.py:40–117`, `fortwall/generator.py:751`, `fortwall/__init__.py:113`).
   - **What this is:** The first fort builds 2,646 nodes and 4,108 links through Python. Existing forts share that graph.
   - **Problem:** Source graph construction took 228.990 s before geometry evaluation. Rebuilding with users took 382.558 s while other audit jobs also ran. Registration took only 0.064 s; the first small-fort evaluation took 0.134 s. Calling the whole delay “geometry compilation” misidentifies the measured bottleneck.
   - **Fix:** Bundle a current, versioned node-group asset and append it lazily on first use using Blender's library loader. Preserve the existing source builder for explicit development rebuilds. Loading the older saved group took 0.496 s; that demonstrates the loading route, not a validated replacement asset. Verify source/asset equivalence, modifier values and missing-file fallback before shipping it.
   - **If we skip it:** Starting a new fort can block Blender for minutes even though enabling the extension is fast.

## Whole graph coverage

All 14 source frames were read, including the actual helper/node links. Tests exercise their combined output; they do not establish a separate performance number for every frame.

| Stage | Review and evidence |
|---|---|
| 1 Spine / resampling | Source inspected; both translated and origin-based polygons evaluated. Exact corner preservation at every resolution remains unproved. |
| 2 Outside / winding | Source inspected. Global shoelace winding is used across splines; mixed-winding and nested-spline behavior was not exhaustively tested. |
| 3 Wall offsets / unfold | Basic wall and gate-only outputs are closed. Existing forward-fill logic retained; no speculative replacement proposed. |
| 3b Bastion sampling / ramp | Empty-collection height collapse reproduced in current source. |
| 4 Wall and courtyard solids | Current no-bastion guard prevents the saved graph's 200 m courtyard regression. |
| 5 Bastion lathes | Added a bastion after a gate; output remains manifold. Radius/height fields and instance-domain capture inspected. |
| 6 Crenels / gates | Gate-only and bastion-plus-gate cases evaluated. Known merlon slivers in `docs/BUGS.md` remain unresolved; manifoldness does not prove their absence. |
| 6b Stairs | A flight was added and evaluated; Edit Mode placement at two selected points also passed. Every real stair's tread area was not measured. |
| 6c Rail gaps / ladders | Source inspected and exercised by bastion/stair cases. Props create expected disconnected mesh islands, so a future core check must exclude them. |
| 7 Boolean core | Five MANIFOLD Boolean nodes and four empty-first-mesh guards in source. Keep necessary realization before booleans; blanket removal would change behavior. |
| 8 Brick rows | Seven wall and seven bastion row families, cheeks, centre slabs and stair rows inspected. No row-spacing or geometry simplification applied. |
| 9 Brick fitting | Thirteen Raycast nodes: one support test plus four directions × three limits. They enforce face ownership and edge clearance; deleting them requires overlap/support regression proof. |
| 10 Bricks / material branch | Brick instances stay unrealized. Switching bricks off preserves identical mesh coordinates/faces/volume while removing the brick instances. |
| 11 Ladders / flags | Final realization of these props is a possible later memory optimization, but it has no measured benefit here and changes what `to_mesh()` and the existing checker see. |

## Measured evaluation and loading

Times are individual local observations, not statistical benchmarks. Some background build experiments overlapped, especially the rebuild. Do not interpret differences of a few milliseconds as improvements.

| Operation | Observation |
|---|---:|
| Extension register in factory session | 0.064 s; no node groups created |
| Native install and enable | 2.04 s; open scene unchanged |
| Construct source graph | 228.990 s; 2,646 nodes / 4,108 links |
| Rebuild same group with users | 382.558 s; all captured input IDs and values preserved |
| Append saved 2,638-node group | 0.496 s; graph is older than source |
| Small fort: gate + bastion + stair, bricks off | 0.087 s repeated evaluation |
| Same small fort, bricks on | 0.208 s repeated evaluation; 14,085 actual bricks plus self-instance |
| Saved full fort: source control points | 218 |
| Saved full fort: bricks on | 8.73–10.88 s; 76,311 brick instances plus self-instance |
| Saved full fort: bricks off | 6.55 s; only self-instance remains |
| Saved full fort mesh in both branches | 165,725 vertices; 110,881 faces; signed volume 155,103.949 m³; zero non-manifold edges |

The full fort's substantial brick-free time means core geometry/booleans also matter; bricks alone do not explain all interaction cost. Keeping bricks off while editing is useful and already supported. Subdividing the whole graph into new subgroups or removing fitting checks has not been justified by a measured benefit.

An in-memory experiment deferred node parenting/positioning until construction finished. It still took 419.381 s under overlapping audit load, with long construction times in the brick row graph. This does not establish an improvement or a clean comparison against the initial build. Production source was left unchanged; no speed-up from that experiment is claimed.

## Extension workflow verification

- Installed as native extension `bl_ext.user_default.fortwall`, enabled and saved in Blender preferences.
- Installed `__init__.py`, `generator.py` and manifest SHA-256 hashes match the source files.
- Add menu callback and Fort sidebar panel are registered.
- Two selected curves convert together and receive separate part collections.
- Reattaching preserves the existing height, modifier and materials without creating duplicate collections.
- Bastion, gate and stair placement from Object Mode works and resolves back to the owning fort.
- Edit Mode adds stairs at exactly the two selected control points.
- Minimum three-corner fort creation with bastions disabled succeeds; bricks default to enabled.
- Register → unregister → register → unregister succeeds.
- Rebuilding current source preserves every captured modifier socket identifier and value.

## Evidence and rerunning

Run scripts only in a disposable process with `--background --factory-startup --python-exit-code 1 --python <script>`; they deliberately create test geometry there. They never save or overwrite the input scenes.

- `reports/fortwall_audit.py`: source graph, translated/empty-part cases, gate/bastion/stair additions, brick branch equality, rebuild preservation, disconnected validation attack and transformed curve smoke test. `-- --cached` instead exercises the older saved graph and skips the rebuild.
- `reports/fortwall-audit.jsonl`: current-source measurements, including completion and preservation proof.
- `reports/fortwall-cached-audit.jsonl`: deliberately older graph; do not confuse its failures with current-source output.
- `reports/fortwall_inventory.py` / `fortwall-inventory.jsonl`: all Geometry Nodes groups inventoried from four supplied scenes without evaluating them. The two older reconstruction scenes retain their small SD2 groups and unrealized scatter architecture; their full collision suite was not rerun.
- `reports/fortwall_scene_probe.py` / `fortwall-scene-audit.jsonl`: actual saved Fort_Wall parameters, output mesh and brick toggle timings.
- `reports/fortwall_extension_probe.py` / `fortwall-extension-audit.jsonl`: workflow and missing-bricks checker attack. The cube substitution is confined to the disposable test process.
- `reports/fortwall_build_probe.py`: optional in-memory construction experiments. Production generator unchanged.
- `reports/fortwall-installation.json`: final registration, source/installation hash matches and unchanged open-scene receipt. All temporary Blender test processes exited; only the user's interactive Blender process remains.
- `reports/fortwall-1.0.0.zip`: native installation archive; ignored by Git under the repository's archive rule.

The probes record observations and caught exceptions, so inspect JSONL records; process exit zero alone does not mean every invariant passed.

**Verdict: fix 1–3 before treating Check Solid or an installed package as proof that an opened fort is correct. Prioritize 4 for loading efficiency.**

**Not checked:** Blender 5.0/5.1 compatibility, restart smoke test, exhaustive exterior views of all bastion junctions, all stair area/overlap metrics, and every seed/resolution combination. No claim of complete visual or collision correctness is made.
