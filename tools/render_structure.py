import sys
from pymol import cmd

pdb = sys.argv[-1]
cmd.load("%s.cif" % pdb.lower(), "s")
cmd.hide("everything")
cmd.remove("solvent")
cmd.remove("not polymer and not resn 5BU")
cmd.remove("polymer.protein")          # keep the RNA only
cmd.bg_color("white")
cmd.set("ray_opaque_background", 0)
cmd.set("cartoon_ring_mode", 3)
cmd.set("cartoon_ring_finder", 1)
cmd.set("cartoon_nucleic_acid_mode", 4)
cmd.set("cartoon_ladder_mode", 1)
cmd.set("cartoon_tube_radius", 0.45)
cmd.show("cartoon", "s")

ramp = [(0.710,0.851,0.992),(0.580,0.737,0.890),(0.455,0.616,0.769),
        (0.349,0.494,0.639),(0.255,0.380,0.502),(0.173,0.271,0.365)]
for i, rgb in enumerate(ramp):
    cmd.set_color("rf%d" % i, list(rgb))
cmd.color("rf1", "s")
res = []
cmd.iterate("s and name P", "res.append((chain, resi))", space={"res": res})
n = max(len(res) - 1, 1)
for i, (ch, ri) in enumerate(res):
    cmd.color("rf%d" % min(int(round(i / n * (len(ramp) - 1))), len(ramp) - 1),
              "s and chain %s and resi %s" % (ch, ri))

for k, v in [("ray_shadows",0),("antialias",2),("specular",0.15),
             ("ambient",0.22),("direct",0.55),("depth_cue",0),("field_of_view",20)]:
    cmd.set(k, v)
cmd.orient("s")
cmd.turn("z", 90)
cmd.zoom("s", 2)
cmd.png("cand-%s.png" % pdb, width=1360, height=1646, dpi=144, ray=1)

# Usage:
#   curl -O https://files.rcsb.org/download/2GIS.cif
#   pymol -cq tools/render_structure.py -- 2GIS
#   (run from the repository root; the PNG goes to content/static/images/)
#
# Produces cand-<ID>.png with a transparent background, ray traced at
# 1360x1646 (2x the site's 680x823 hero ratio). Flatten onto the page ground
# and cut the web assets with:
#   magick cand-2GIS.png -background "#f2f2f3" -flatten -resize 680x \
#          -strip -quality 88 content/static/images/research-2gis.jpg
