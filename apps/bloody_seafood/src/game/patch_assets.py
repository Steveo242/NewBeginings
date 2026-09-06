p = 'assets.ts'
s = open(p).read()

files = {
    'bgSky': 'bg_land_sky',
    'bgBoats': 'bg_land_boats',
    'bgWater': 'bg_land_water',
    'bgNearBoats': 'bg_land_nearboats',
    'bgDock': 'bg_land_dock',
    'bgGulls': 'bg_land_gulls',
    'bgOverlay': 'bg_land_overlay',
    'titlePlaque': 'title_plaque',
}

entries = ""
for key in files:
    fname = files[key]
    entries += "\t" + key + ": {\n"
    entries += "\t\ttype: 'sprites',\n"
    entries += "\t\tsrc: new URL('../../assets/sprites/bgLayers/" + fname + ".png', import.meta.url).href,\n"
    entries += "\t\tpreload: true,\n"
    entries += "\t},\n"

anchor = "export default {\n"
if anchor not in s:
    raise SystemExit("anchor not found")

s = s.replace(anchor, anchor + entries, 1)
open(p, 'w').write(s)
print("inserted", len(files), "entries")
