# sd_build_all.py - press "Run Script" here to (re)build the Sindhudurg scene.
# Rebuilds every SD_ collection from the editable guide SD_GUIDE_Outline (+ SD_GUIDE_Gate*/Beach).
# Nothing outside the "Sindhudurg" scene / SINDHUDURG collection is touched.
import bpy
STAGES = ["outline", "walls", "gate", "interior", "terrain", "finish"]
MODS = ["sd_core.py", "sd_outline.py", "sd_walls.py", "sd_gate.py", "sd_interior.py", "sd_terrain.py", "sd_finish.py"]
ns = {}
for m in MODS:
    exec(compile(bpy.data.texts[m].as_string(), m, "exec"), ns)
sc = ns["scene"]()
if bpy.context.window is not None:
    bpy.context.window.scene = sc
report = {st: ns["build_" + st]() for st in STAGES}
print(report)
