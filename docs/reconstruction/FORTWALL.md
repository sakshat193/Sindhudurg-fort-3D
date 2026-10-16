# FortWall: procedural fort generator (Blender 5.2)

`fort_wall_gn.py` builds one Geometry Nodes group, **FortWall**, that turns a closed Bezier curve and three collections of empties into a joined fort. The output is a battered wall, bastions, gates, stairs, a walkway, merlons, ladders, flags and optional bricks. Manifold booleans join the core into one closed solid.

## Run

In Blender's Python console or Text Editor:

```python
exec(open(r'B:\Blender\Blender_Fort_Reconstruction\reconstruction\fort_wall_gn.py').read())
```

This rebuilds the node group. It creates the demo objects only if they are missing: the `Fort_Wall` curve, the `Bastions`, `Gates` and `Stairs` collections, and the materials. An existing scene keeps its curve, empties and modifier values.

To use the helpers without running the demo:

```python
ns = {}
exec(open(path).read().split("if __name__")[0], ns)
ns['build_group']()   # rebuild the node group in place
ns['check']()         # {'volume', 'open_edges', 'bricks', 'secs'}; asserts a closed outward solid
ns['mod_input'](md, 'Height').value   # read or write a modifier input (Blender 5.x)
```

The first rebuild of a large scene can freeze Blender for several minutes while it compiles. Wait for it; don't kill Blender, because an unsaved scene would be lost.

## Controls

| Object | Edit | Effect |
|---|---|---|
| `Fort_Wall` curve | Alt+S on a point | Crown width there (radius × Crown Width) |
| | G Z on a point | Wall height there (point Z is added to Height) |
| `Bastions` empty | Move / scale / Z | Placement / radius / extra platform height |
| `Gates` empty | Move / scale | Snaps across the nearest wall. Width = 2 × scale X, height = Gate Height × scale Z |
| `Stairs` empty | Move / rotate / scale X | Foot of the flight, rising along local X. Width = scale X. Rise ≤ 0.2 m, going 0.3 m |

Main modifier inputs:

- **Size:** Height, Crown Width, Batter, Ground, Parapet Height/Thickness.
- **Detail:** Resolution (resample step in metres), Bastion Batter, Ramp Run.
- **Merlons:** Merlon Height/Spacing/Randomness and Crenel Width. A Merlon Height of 0 means no merlons.
- **Bricks:** Bricks, Brick Size, Mortar Gap, Brick Relief, Brick Jitter, Seed.
- **Extras:** Flag Chance, Flagpole Height, Flip Outside (use it if the outside is detected on the wrong side), and the materials.

## Geometry rules

- **Corners:** the resample point nearest each knot snaps onto it, so corners stay sharp at any Resolution.
- **Crenels:**
  - They are spaced along the parapet's own centreline.
  - Corners that turn more than about 20° keep one solid merlon.
  - Junction piers at bastions have no crenels.
- **Stairs:**
  - Stations run along a smoothed copy of the courtyard face.
  - Every side of a flight is set off the true mitered face, so flights turn corners with winders.
- **Walkway:** it ramps to each bastion platform's height over Ramp Run.
- **Ladders and rail:** each bastion gets a ladder up its courtyard face, square to the wall. A low rail lines the courtyard edge, with gaps at stair tops and ladders.

## Editing the generator

- **Never reassign `md.node_group` or add, remove or reorder interface inputs.** The socket IDs change, and every modifier value on existing objects resets.
- Keep the interface list in `build_group` stable. To add an input, append it at the end and expect to re-enter its value.
- After any change, run `check()`. It must return `open_edges == 0` and a positive volume.

## Sindhudurg trace

The real-fort scene uses this method:

- The spine is the traced outline offset inward by half the wall thickness. Its points carry the surveyed toe Z, with Ground = −1 and Height = 9.044.
- Bastions are disks with the terrace areas. The wall is chorded through each disk.
- Bastion and stair empties have been hand-placed. Keep them as they are.

The exporter that produced the spine JSON from `web/dist` (`makeSampler` plus survey data) is not yet in the repository.
