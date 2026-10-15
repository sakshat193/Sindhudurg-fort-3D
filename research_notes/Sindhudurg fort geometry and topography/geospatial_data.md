# Sindhudurg Fort: machine-readable geospatial data (OSM, Wikimapia/Wikidata, DEMs, UNESCO boundary, drawings, historical charts)

Conventions used throughout. Local frame: metres, +X east, +Y north, Z = 0 mean sea level, origin 16.04253 N, 73.45908 E (WGS84). Conversion used for every X/Y below (computed by me): X = (lon - 73.45908) x 111320 x cos(16.0425 deg) = (lon - 73.45908) x 106,996 m; Y = (lat - 16.04253) x 110,574 m. Retrieval date 2026-10-13. Raw files saved next to these notes (all in `B:\Blender\Blender_Fort_Reconstruction\research_notes\Sindhudurg fort geometry and topography\`):

| File | What it is |
|---|---|
| `osm_sindhudurg.json` | Raw Overpass `nwr(bbox); out geom;` answer (server snapshot timestamp 2026-10-13T15:22:02Z) for S 16.036, W 73.454, N 16.048, E 73.465 (620 elements: 576 nodes, 40 ways, 4 relations; 8.7 MB because 4 admin-boundary relations carry geometry) |
| `unesco_1739-011_sindhudurg_boundary.geojson` | UNESCO core polygon (341 vertices, 19.1 ha) and buffer polygon (70 vertices, about 783.7 ha), EPSG:4326 |
| `wikimapia_places.json` | 33 Wikimapia places with parsed polygon rings, centroid lat/lon, X/Y, area, min-area-rectangle size |
| `dem_samples.json` | 53 sample points (24 landmarks, 16 N-S transect, 13 E-W transect) x 11 elevation datasets, plus raw elevation windows (72 rows x 40 columns for Copernicus GLO-30, ALOS and NASADEM; 38 x 24 for GLO-90) |

Note on method: the OSM and Wikimapia footprint sizes below are minimum-area bounding rectangles (rotating calipers, 1 degree steps) of the traced polygon; areas are shoelace areas in the local frame. Centroids for buildings, natural polygons, the coastline and Padmagad are area centroids; the centroids quoted for the wall, track and pier lines are plain vertex averages. These are my computations from the retrieved data, not statements by the sources.

---

## 1. What does OpenStreetMap actually contain for the fort and its seascape (features, coordinates, building footprints, paths)?

### Takeaway
OSM has an accurate islet outline (291-node coastline way, 2.80 km perimeter, 19.1 ha), 20 unnamed building footprints inside the fort, 3 unnamed tracks, 2 piers, one fort node, one named gate node and 15 submerged-rock seamarks, but it has no names, no temples, no wells, no bastions, no width tags and only a 69 m stub of "city_wall". OSM is a good base for the island outline and rough building positions, not a source for rampart geometry.

### Cited Findings
- Query: Overpass API, bbox S 16.036 / W 73.454 / N 16.048 / E 73.465, `nwr(bbox); out geom;`; full answer stored in `osm_sindhudurg.json`. OSM data licence is ODbL (attribution "© OpenStreetMap contributors", share-alike on derived databases) — [OSM copyright](https://www.openstreetmap.org/copyright); endpoint [Overpass API](https://overpass-api.de/api/interpreter).
- Island outline: way 19804981, tags `natural=coastline` + `place=islet`, 291 nodes, perimeter 2,799 m, enclosed area 19.10 ha, minimum rectangle 665 x 492 m with long axis rotated 65 deg from east (i.e. SSW-NNE); extent X -221..301, Y -398..352 — [OSM way 19804981](https://www.openstreetmap.org/way/19804981). Mean node spacing about 9.7 m (2,799 m / 290 segments; my arithmetic).
- Fort node: node 342119741 `historic=fort`, `name=Sindhudurg Fort`, 16.0427900 N, 73.4600899 E, X 108.0 Y 28.7 — [OSM node 342119741](https://www.openstreetmap.org/node/342119741).
- Main gate: node 2713509503 `barrier=gate`, `name=Sindudurg Fort Main Gate` (sic), `motor_vehicle=no`, `bicycle=no`, 16.0438243 N, 73.4614705 E, X 255.7 Y 143.1 — [OSM node 2713509503](https://www.openstreetmap.org/node/2713509503). A node 8540140046 whose only tag is `source=PGS` sits at X 263.5 Y 144.0 beside it.
- Wall: only two wall ways exist. Way 426199526 `barrier=city_wall`, `name=Sindhudurg Fort`, 6 nodes, 68.8 m long, centroid X 60.3 Y 124.5 — [way 426199526](https://www.openstreetmap.org/way/426199526). Way 426199496 `barrier=wall`, 6 nodes, 41.5 m, centroid X 20.6 Y -162.8 — [way 426199496](https://www.openstreetmap.org/way/426199496). No height, thickness, material or bastion tags on either.
- Tracks (no `name`, `width`, `surface` or `highway` class other than `track`): way 426199527 `tracktype=grade3`, 12 nodes, 213 m, centroid X -56.9 Y -155.4 — [way](https://www.openstreetmap.org/way/426199527); way 426199528 `tracktype=grade2`, 21 nodes, 234 m, centroid X 115.8 Y -217.9 — [way](https://www.openstreetmap.org/way/426199528); way 426199529 `tracktype=grade2`, `layer=1`, 28 nodes, 432 m, centroid X 115.0 Y -11.8 — [way](https://www.openstreetmap.org/way/426199529).
- Piers (`man_made=pier`, untagged otherwise): way 426199491, 6 nodes, 72.0 m, centroid X 269.9 Y 162.5, from the gate area to about X 285 Y 204 — [way](https://www.openstreetmap.org/way/426199491); way 426199494, 3 nodes, 157.3 m, centroid X 344.4 Y 263.0 — [way](https://www.openstreetmap.org/way/426199494). Unnamed `amenity=ferry_terminal`, `ferry=yes` node 4255020451 at 16.0454133 N, 73.4627005 E, X 387.3 Y 318.8 — [node](https://www.openstreetmap.org/node/4255020451).
- Malvan mainland landing (outside the fort, 1.35 km north of the origin): node 13570010601 "Marvan Jetty" `amenity=ferry_terminal`, 16.05471 N, 73.464334 E (X 562, Y 1347) with pier way 365721849 (`man_made=pier`, centroid 16.054863, 73.464173; X 545, Y 1364) - [node 13570010601](https://www.openstreetmap.org/node/13570010601), [way 365721849](https://www.openstreetmap.org/way/365721849). These two lie north of the saved bbox (N edge 16.048 = Y 606 m) and came from an earlier, wider Overpass query that I did not save, so they are NOT in `osm_sindhudurg.json`.
- Padmagad islet: coastline way 426103123 `name=Padamged` and place way 1425300062 `name=Padamged Island`, 138 x 70 m, area 6,176 m2, centroid X 577 Y 549; one building 1425300061 (13.4 x 11.7 m, 156 m2) at X 606.9 Y 538.0; fishing node 5883325588 `name=padmagad` at 16.0471126, 73.4648627 — [way 426103123](https://www.openstreetmap.org/way/426103123), [way 1425300061](https://www.openstreetmap.org/way/1425300061), [node 5883325588](https://www.openstreetmap.org/node/5883325588).
- Protected area: way 678002187 `Malvan Marine Sanctuary`, `leisure=nature_reserve`, `protect_class=4`, wikidata Q13119963; a 5-vertex rectangle of about 5,887 x 1,220 m (4,148,627 m2, long side rotated 20 degrees from +X), so it is a coarse legal boundary and not a fort feature — [way 678002187](https://www.openstreetmap.org/way/678002187). Admin relations present: Maharashtra (1950884), Sindhudurg (1997166), Malvan Taluka (10356050), Western Zonal Council (16087866) — [relation 10356050](https://www.openstreetmap.org/relation/10356050).
- Natural polygons east of the fort (minimum rectangle long x short, shoelace area, area centroid): `natural=bare_rock` ways 1425300052 (26.6 x 14.6 m, 242 m2, X 623 Y 94), 1425300055 (46.3 x 12.7 m, 422 m2, X 469 Y 33), 1425300056 (33.4 x 24.8 m, 624 m2, X 383 Y 148), 1425300059 (105.9 x 46.0 m, 3,031 m2, X 487 Y 376), 1425300060 (41.6 x 20.4 m, 620 m2, X 634 Y 556); `natural=beach` ways 1425300057 (124.6 x 59.4 m, 4,449 m2, X 341 Y 218), 1425300058 (176.7 x 72.8 m, 7,613 m2, X 657 Y 501); and a small second `natural=coastline` way 19805032 (72.6 x 34.6 m, 1,755 m2, X 501 Y 374) — [way 1425300057](https://www.openstreetmap.org/way/1425300057), [way 19805032](https://www.openstreetmap.org/way/19805032).
- 15 `seamark:type=rock`, `seamark:rock:water_level=covers` (submerged rocks) nodes, e.g. 4254161627 (X 75, Y -536), 4254161635 (X 480, Y 33), 4254161636 (X 437, Y 49), 4254161637 (X -250, Y 79), 4254161638 (X 617, Y 100), 4254161639 (X 350, Y 179), 4254161640 (X -247, Y 210), 4254161641 (X 370, Y 229), 4254161642 (X 497, Y 331), 4254161643 (X 534, Y 338), 4254161645 (X 439, Y 392), 4254161646 (X -133, Y 403), 4254161648 (X 417, Y 451), 4254161654 (X 288, Y 507), 4254161655 (X 455, Y 556) — [node 4254161627](https://www.openstreetmap.org/node/4254161627). Positions only, no depths. In addition the file holds 44 vertex nodes whose only tags are `source=PGS` (36 with ids 206405256-206405307, 7 with ids 206406062-206406145, and node 8540140046 at X 263.5 Y 144.0 beside the gate; node 206405258 also has `created_by=JOSM`); they are scattered from X -208 to 606 and Y -388 to 593 and are not features. A further 513 nodes are untagged way vertices.

**Fort-interior building footprints (all `building=yes`, no names, no height/levels tags).** Source: Overpass data, ways at [openstreetmap.org/way/ID](https://www.openstreetmap.org/way/426199498). Centroid X/Y in metres; rectangle = minimum-area bounding rectangle, long x short, with its rotation from +X.

| Way | X | Y | Footprint (m) | Area m2 | Long-axis angle, deg CCW from +X |
|---|---|---|---|---|---|
| 426199498 | 25.0 | -205.7 | 23.6 x 10.9 | 182 | 8 |
| 426199500 | 44.4 | -57.9 | 5.7 x 4.9 | 28 | 6 |
| 426199502 | 73.3 | 27.0 | 13.9 x 8.7 | 120 | 5 |
| 426199504 | 51.4 | -9.9 | 17.4 x 11.8 | 204 | 92 |
| 426199506 | 127.7 | 72.3 | 10.8 x 9.5 | 101 | 119 |
| 426199507 | -168.5 | -203.6 | 4.2 x 4.0 | 17 | 29 (near-square, ambiguous) |
| 426199509 | 65.7 | 43.1 | 12.8 x 7.8 | 98 | 1 |
| 426199511 | 47.4 | -38.0 | 13.7 x 9.3 | 126 | 106 |
| 426199512 | 122.0 | -241.8 | 15.5 x 11.8 | 181 | 132 |
| 426199513 | 38.4 | -20.7 | 9.1 x 5.8 | 52 | 1 |
| 426199515 | 98.9 | 16.3 | 12.3 x 9.9 | 122 | 91 |
| 426199516 | 45.4 | 89.8 | 7.5 x 5.8 | 43 | 179 |
| 426199518 | 10.3 | -8.8 | 11.5 x 9.5 | 107 | 93 |
| 426199519 | 248.5 | 138.8 | 12.4 x 6.2 | 76 | 92 |
| 426199520 | 17.0 | 46.0 | 16.7 x 13.4 | 222 | 89 |
| 426199521 | 78.7 | 40.4 | 6.6 x 5.2 | 34 | 87 |
| 426199522 | 25.7 | 18.7 | 10.4 x 9.2 | 96 | 90 (near-square, ambiguous) |
| 426199523 | 88.1 | -20.1 | 9.8 x 6.9 | 67 | 87 |
| 426199524 | 85.9 | 16.7 | 12.2 x 11.2 | 124 | 77 (near-square, ambiguous) |
| 426199525 | 64.3 | -160.0 | 13.0 x 10.1 | 110 | 151 |

X, Y are shoelace area centroids; footprint is the minimum-area bounding rectangle (1-degree steps); the angle is of the rectangle's long side measured CCW from +X. Fifteen of the 20 footprints have their long axis within 15 degrees of east or north (typical of quick imagery tracing); five are skewed (426199506, 426199507, 426199511, 426199512, 426199525). The Padmagad building 1425300061 (13.4 x 11.7 m, 156 m2, X 606.9 Y 538.0, axis 100 deg) is the 21st building in the bbox.

### Inferences
- OSM can seed the 20 interior building footprints and the island coastline; each footprint is a coarse rectangle (4-24 m on a side) and none has a height, so heights must come from photos or other notes.
- Way 426199526 (68.8 m, centroid X 60, Y 125) is evidently a short stretch of the rampart on the north-west side; the rest of the 2.8 km rampart is not in OSM as a wall. For the wall line the best machine-readable proxy is the coastline way or the UNESCO core polygon (see section 4), which agree to within about 3-9 m (section 6).
- The gate building 426199519 (12.4 x 6.2 m) plus pier 426199491 give the only OSM-derived landing geometry; whether the 229 m of "pier" ways (72 + 157 m) is a jetty, a breakwater or a mapped ferry track is not stated by the tags.

### Gaps
- OSM has no temples, wells, Rani chi Vel, bastions, towers, rampart walk, stairs or named buildings; none of the requested temple/well features can be sourced from OSM.
- No path widths, surfaces or names are tagged on any of the 3 tracks.
- The Malvan "Marvan Jetty" node/way are outside the saved bbox (see above); re-run Overpass with a wider box if they are needed in the JSON.

---

## 2. Where are the named monuments (temples, wells, Rani chi Vel, main gate, jetty) according to Wikimapia, Wikidata, Wikipedia and OSM, and how precise is each?

### Takeaway
Wikimapia is the only source with positions (traced polygons) for Shivrajeshwar, Jari Mari, Mahapurush, Bhavani, a Shiva temple, the Dudh/Dahi/Sakhar wells and Rani chi Vela; Wikipedia's fort coordinate is essentially the gate and Wikidata's is 257 m away from it, so single-point "fort" coordinates should not be used for placing anything. No source gives a Hanuman temple.

### Cited Findings
- Retrieval: Wikimapia's JSON API with a demo key returned nothing; the site's own KML endpoint `https://wikimapia.org/d?BBOX=lon_min,lat_min,lon_max,lat_max&LNG=0&zoom=N` worked when sent the `nsess` cookie that the site's front page sets via JavaScript (no login, no CAPTCHA involved; disclosed here as a workaround). I fetched the full bbox plus 4x4 tiles at zoom 17 and 19, kept the largest version of each polygon ring and parsed only the LineString ring. Wikimapia content is user-contributed and offered under CC BY-SA 3.0 as noted on the site (verify before redistributing) — [Wikimapia](https://wikimapia.org/).
- Wikimapia polygons, centroid and minimum rectangle (computed from `wikimapia_places.json`):

| Feature (Wikimapia id, link) | lat | lon | X | Y | Rectangle (m) | Area m2 |
|---|---|---|---|---|---|---|
| Shri Shivrajeshwar Mandir compound ([18920737](http://wikimapia.org/18920737/)) | 16.0427973 | 73.4596155 | 57.3 | 29.6 | 59.5 x 52.6 | 3,065 |
| Chhatrapati Shivaji Maharaj Mandir, building ([254135](http://wikimapia.org/254135/)) | 16.0427799 | 73.4596661 | 62.7 | 27.6 | 34.6 x 17.7 | 602 |
| Jari Mari Mata mandir ([4199168](http://wikimapia.org/4199168/)) | 16.0435370 | 73.4610810 | 214.1 | 111.3 | 26.8 x 22.9 | 613 |
| Mahapurush mandir ([21025616](http://wikimapia.org/21025616/)) | 16.0433194 | 73.4595097 | 46.0 | 87.3 | 16.2 x 12.3 | 191 |
| Shri Bhavani Temple ([15131896](http://wikimapia.org/15131896/)) | 16.0402623 | 73.4604454 | 146.1 | -250.7 | 8.6 x 6.1 | 52 |
| Shri Shiva Temple ([4199162](http://wikimapia.org/4199162/)) | 16.0419968 | 73.4595004 | 45.0 | -59.0 | 5.6 x 5.6 | 31 |
| Dudh Bav ([4199153](http://wikimapia.org/4199153/)) | 16.0412972 | 73.4594318 | 37.6 | -136.3 | 7.0 x 4.6 | 27 |
| "dudhbav" (second record, [16106698](http://wikimapia.org/16106698/)) | 16.0413385 | 73.4595269 | 47.8 | -131.7 | 25.4 x 2.4 (sliver) | 29 |
| Dahi Bav ([4486290](http://wikimapia.org/4486290/)) | 16.0413163 | 73.4596301 | 58.9 | -134.2 | 4.8 x 4.2 | 20 |
| Sakhar Bav ([4486331](http://wikimapia.org/4486331/)) | 16.0409536 | 73.4599765 | 95.9 | -174.3 | 4.5 x 4.2 | 19 |
| Ranichi Vela ([4486307](http://wikimapia.org/4486307/)) | 16.0407807 | 73.4579278 | -123.3 | -193.4 | 37.2 x 16.1 | 409 |
| Sindhudurg Entrance ([445369](http://wikimapia.org/445369/)) | 16.0438233 | 73.4614135 | 249.6 | 143.0 | 9.8 x 5.4 | 53 |
| Mukhya pravesh dwar of the fort ([15526588](http://wikimapia.org/15526588/)) | 16.0438707 | 73.4615075 | 259.7 | 148.2 | 77.3 x 25.0 (19 vertices) | 487 |
| Sweet water lake ([1865604](http://wikimapia.org/1865604/)) | 16.0437482 | 73.4605354 | 155.7 | 134.7 | 34.7 x 10.6 | 252 |
| Nishan Buruj ([2674562](http://wikimapia.org/2674562/)) | 16.0406841 | 73.4592883 | 22.3 | -204.1 | 14.2 x 10.5 | 128 |
| Tehalni Buruj ([17812645](http://wikimapia.org/17812645/)) | 16.0406374 | 73.4592924 | 22.7 | -209.3 | 16.5 x 10.0 | 130 |
| Torture Chamber ([11286442](http://wikimapia.org/11286442/)) | 16.0405960 | 73.4589511 | -13.8 | -213.8 | 6.1 x 6.1 | 30 |
| Shivaji Padunka ([24748299](http://wikimapia.org/24748299/)) | 16.0443163 | 73.4614835 | 257.1 | 197.5 | 22.8 x 10.2 | 168 |
| Shivaji fingerprints ([1731550](http://wikimapia.org/1731550/)) | 16.0443174 | 73.4614858 | 257.4 | 197.6 | 5.0 x 4.2 | 21 |
| Padmagad ([20033440](http://wikimapia.org/20033440/)) | 16.0474031 | 73.4646024 | 590.8 | 538.8 | 51.7 x 26.7 | 947 |
| Sindhudurg Fort island polygon ([101740](http://wikimapia.org/101740/)) | 16.0422218 | 73.4597961 | 76.6 | -34.1 | 662.9 x 493.2 | 189,706 |

  Also in `wikimapia_places.json` (houses inside the fort, useful as occupied-building markers): Jadhav Family Home (X -26.2, Y -47.1; 34.4 x 15.2 m), Bhonslay Family House (37.5, -44.9; 18.7 x 9.8), Sakpal house (70.3, 7.6; 10.9 x 7.0), Shaikh's Abode (119.9, 69.1; 14.1 x 6.5), Phatak House (138.6, -239.0; 13.8 x 13.5), and the "haunted rock (Sarmunda triangle)" reef polygon (684.8, -4.3; 118 x 45 m). Wikimapia names are volunteer-entered and spellings are inconsistent (e.g. the Mahapurush record is entered in Devanagari).
- Wikipedia infobox coordinate for the fort: 16 deg 02' 38" N, 73 deg 27' 41" E (16.043769, 73.461416), i.e. X 249.9 Y 137.0 — [Wikipedia: Sindhudurg Fort](https://en.wikipedia.org/wiki/Sindhudurg_Fort). The Wikipedia geosearch API returns the same point, and the Hindi-language article carries the identical value (read from my API queries; no separate link). Wikipedia also gives the rampart as about 3 km long, 9.1 m high, 3.7 m thick and the fort as 48 acres — [Wikipedia: Sindhudurg Fort](https://en.wikipedia.org/wiki/Sindhudurg_Fort).
- Wikidata item Q13413791 "Sindhudurg Fort": P625 = Point(73.45985873 16.04199662), i.e. 16.04199662 N, 73.45985873 E (X 83.3, Y -59.0), 8 significant decimal digits but no stated accuracy; the same value is used by the Wikimedia Commons category "Sindhudurg Fort". A `wikibase:around` SPARQL query and a Commons geosearch (both via the public APIs) returned it — [Wikidata Q13413791](https://www.wikidata.org/wiki/Q13413791). Its sitelinks include enwiki, mrwiki, hiwiki and commonswiki. A Wikidata text search (`wbsearchentities`) for "Shivrajeshwar", "Bhavani temple Sindhudurg", "Jarimari", "Mahapurush temple Sindhudurg", "Hanuman temple Sindhudurg fort", "Rani chi Vel", "Dudh Bav" and "Sindhudurg jetty" returned no entities for any of them — [Wikidata API](https://www.wikidata.org/w/api.php).
- UNESCO's own centre point for component 1739-011 is N16 2 33, E73 27 35 (16.0425, 73.4597222; X 68.7, Y -3.3) — [UNESCO list 1739 maps](https://whc.unesco.org/en/list/1739/maps).
- Gate sources compared (X, Y): OSM gate node 255.7, 143.1; Wikimapia "Sindhudurg Entrance" 249.6, 143.0; Wikipedia fort coordinate 249.9, 137.0; the coordinate supplied in the task brief (16.04393 N, 73.46160 E) 269.6, 154.8.
- A web search surfaced temples to Mahadeo, Jarimai, Mahapursh and Bhavani plus the Shivaji temple inside the fort (search-result summary of the Outlook Traveller Malvan feature; the page itself was not opened) — [Outlook Traveller](https://www.outlooktraveller.com/destinations/india/maharashtra-malvan-maratha-heritage). Neither OSM nor the Wikimapia KML nor Wikidata contains a Hanuman temple (section 2 Gaps).

### Inferences
- Computed from the table: Wikipedia's coordinate lies 8.4 m from the OSM gate node and 6.0 m from the Wikimapia entrance, so it is a gate-side coordinate, while Wikidata's is 257 m from Wikipedia's (and 38 m from the Wikimapia Shiva temple). The OSM fort node (108.0, 28.7) is 51 m from UNESCO's centre and 91 m from Wikidata's. None of the four is a true centre; the three island polygons give an area centre near X 64-84, Y -34..-22 (OSM 63.6, -22.3; Wikimapia 76.6, -34.1; UNESCO core 84.3, -28.7, all shoelace area centroids).
- The task-brief gate (269.6, 154.8) is 18.2 m from the OSM gate, 23.2 m from the Wikimapia entrance point and 26.5 m from the centre of OSM gate building 426199519; the OSM, Wikimapia and Wikipedia gate positions agree with each other to 6-8 m, so I would move the model gate to about X 250-256, Y 137-143 unless the model's local origin has its own known offset.
- Offsets between the two datasets (my computation: Wikimapia centroid as stored in `wikimapia_places.json` minus OSM shoelace centroid; each pairing is my judgement from name and size). Good pairs: Shiva temple (Wikimapia 5.6 x 5.6 m) vs OSM way 426199500 (5.7 x 4.9 m), dX +0.6, dY -1.1, 1.3 m apart; Mahapurush shrine vs way 426199516, dX +0.6, dY -2.5, 2.5 m (but the Wikimapia polygon is 16.2 x 12.3 m against 7.5 x 5.8 m in OSM); Nishan Buruj vs way 426199498, dX -2.7, dY +1.6, 3.1 m; Wikimapia entrance vs gate-house way 426199519, dX +1.1, dY +4.2, 4.4 m. Looser pairings: Shaikh's Abode vs way 426199506, dX -7.8, dY -3.2, 8.5 m; Bhonslay house vs way 426199511, dX -9.9, dY -6.9, 12.1 m; Phatak House vs way 426199512, dX +16.6, dY +2.8, 16.9 m (these last two are guesses). Signs are mixed, so I found no systematic shift between Wikimapia and OSM; the four good pairs agree to 1-4.4 m and poorer ones scatter to about 17 m. Jari Mari has no OSM building nearby (nearest is the gate house, 44 m away).
- The Shivrajeshwar compound polygon (59.5 x 52.6 m) and its inner building (34.6 x 17.7 m, centroid X 62.7 Y 27.6) do not match any single OSM footprint: the nearest OSM centroids are way 426199502 (13.9 x 8.7 m) at 10.6 m, way 426199509 (12.8 x 7.8 m) at 15.8 m and way 426199524 (12.2 x 11.2 m) at 25.6 m, so that building's outline is uncertain; the two datasets disagree on its size by a factor of about 2-2.5 in each dimension.
- Wikimapia places Jari Mari (26.8 x 22.9 m) just south-west of the gate at X 214, Y 111, close to the "Sweet water lake" polygon (X 156, Y 135), and Bhavani at the island's far south end (Y -251) next to the "Phatak House" (X 139, Y -239); the three wells sit as a cluster at Y -134..-174 and the Rani chi Vela at the western coast (X -123, Y -193). These relative positions are consistent with the fort's described layout but are only as good as volunteer tracing, probably a few metres.

### Gaps
- No Hanuman temple coordinate in Wikimapia, OSM, Wikidata or the web search; the temple may be absent, unmapped or named differently.
- No separate jetty polygon in Wikimapia (the only fort-side landing geometry is the OSM pier ways).
- Wikidata/Wikipedia coordinate provenance (who set them, from what map) is unknown; Wikidata's accuracy field was not read.
- Hanuman temple: the web search surfaced a Hanuman idol only at Devgad fort (a different fort), with no identified source page; nothing for Sindhudurg.
- Wikimapia polygon precision is unverified (user-traced on satellite imagery of unknown date and unknown georeferencing error); no independent ground control found.
- Wikimapia licence text was not re-read this session beyond the site's own footer wording.

---

## 3. Which DEMs cover the island, at what resolution, and what do point samples show?

### Takeaway
Free global DEMs (SRTM 30 m, Copernicus GLO-30, ALOS AW3D30, NASADEM, ASTER, GLO-90) cover the island only at 30-90 m, which puts the whole 19.1 ha fort into about 210 pixels (30 m cells); they agree with each other to roughly 0.5-2 m on the interior but are surface models that include walls, trees and buildings, and sea cells are flattened to 0. No DEM finer than 30 m and no LiDAR was found; they can set a coarse island-scale surface, not 1 m terrain.

### Cited Findings
- Samples were taken at 53 points (24 landmarks including every position in section 2, 16 N-S transect points at lon 73.4590 / lat 16.0385-16.0460 every 0.0005 deg = 55 m, 13 E-W transect points at lat 16.0425 / lon 73.4565-73.4625 every 53.5 m); all values (nearest and bilinear) and the raw elevation windows are in `dem_samples.json`.
- opentopodata public API (nearest-neighbour, integer metres) for `srtm30m`, `srtm90m`, `aster30m`, `mapzen`, `etopo1`, `gebco2020` — [OpenTopoData](https://www.opentopodata.org/). Open-Meteo elevation API (documented as Copernicus-DEM based) — [Open-Meteo elevation](https://open-meteo.com/en/docs/elevation-api).
- Copernicus GLO-30 (`Copernicus_DSM_COG_10_N16_00_E073_00_DEM.tif`, float32) and GLO-90 cloud-optimised GeoTIFFs read by HTTP range with rasterio from the AWS open-data bucket — [Copernicus DEM on AWS](https://registry.opendata.aws/copernicus-dem/). Pixel sizes at this latitude (computed from the GeoTIFF transforms): GLO-30 29.7 m E-W x 30.7 m N-S; GLO-90 89.2 x 92.1 m.
- ALOS AW3D30 (`ALPSMLC30_N016E073_DSM`, int16) and NASADEM (`NASADEM_HGT_n16e073`, int16), both 29.7 x 30.7 m, were read through Microsoft Planetary Computer with its anonymous SAS signing endpoint — [Planetary Computer ALOS DEM](https://planetarycomputer.microsoft.com/dataset/alos-dem), [NASADEM](https://planetarycomputer.microsoft.com/dataset/nasadem). ALOS and NASADEM are integer-metre rasters, so their "nearest" values are whole metres and the fractional values below are bilinear.
- Sample values (metres). SRTM30, SRTM90, ASTER30 and Open-Meteo are the integer values returned by those services (opentopodata nearest-neighbour); GLO-30, ALOS and NASADEM are my reads from the rasters as nearest / bilinear; GLO-90 is bilinear from my own AWS read. (WM = Wikimapia position.) Source for all: `dem_samples.json`, built from the services above.

| Point | X | Y | SRTM30 | SRTM90 | ASTER30 | Open-Meteo | GLO-30 n / b | GLO-90 b | ALOS n / b | NASADEM n / b |
|---|---|---|---|---|---|---|---|---|---|---|
| Model origin | 0.0 | 0.0 | 7 | 7 | 9 | 3 | 7.4 / 6.7 | 6.6 | 9 / 8.8 | 7 / 6.4 |
| OSM fort node | 108.0 | 28.7 | 10 | 8 | 11 | 6 | 7.0 / 7.5 | 6.8 | 8 / 8.0 | 9 / 8.7 |
| UNESCO published centre | 68.7 | -3.3 | 8 | 8 | 10 | 5 | 9.2 / 9.2 | 7.7 | 9 / 8.8 | 7 / 7.0 |
| Wikidata fort | 83.3 | -59.0 | 9 | 7 | 6 | 7 | 7.6 / 7.6 | 7.1 | 8 / 8.3 | 8 / 7.1 |
| Wikipedia fort | 249.9 | 137.0 | 5 | 5 | 4 | 5 | 5.3 / 4.7 | 1.5 | 1 / 1.4 | 5 / 4.4 |
| OSM Main Gate | 255.7 | 143.1 | 5 | 5 | 4 | 5 | 5.3 / 3.9 | 1.1 | 1 / 1.0 | 5 / 4.2 |
| Brief gate coordinate | 269.6 | 154.8 | 4 | 5 | 0 | 5 | 0.0 / 1.2 | 0.4 | 0 / 0.3 | 3 / 3.7 |
| Wikimapia entrance | 249.6 | 143.0 | 5 | 5 | 4 | 5 | 5.3 / 4.8 | 1.5 | 1 / 1.3 | 5 / 4.6 |
| OSM pier start | 284.7 | 204.3 | 4 | 5 | 0 | 0 | 0.0 / 0.0 | 0.0 | 0 / 0.0 | 5 / 4.5 |
| OSM ferry terminal | 387.3 | 318.8 | 0 | 0 | 0 | 0 | 0.0 / 0.0 | 0.0 | 0 / 0.0 | 0 / 0.0 |
| Shivaji temple bldg (WM) | 62.7 | 27.6 | 9 | 8 | 11 | 5 | 8.5 / 8.6 | 6.9 | 8 / 8.7 | 9 / 8.8 |
| Shivrajeshwar compound (WM) | 57.3 | 29.6 | 9 | 8 | 11 | 5 | 8.5 / 8.6 | 6.8 | 8 / 8.8 | 9 / 8.6 |
| Jari Mari (WM) | 214.1 | 111.3 | 5 | 5 | 2 | 5 | 5.6 / 5.4 | 3.6 | 3 / 2.5 | 6 / 5.6 |
| Mahapurush (WM) | 46.0 | 87.3 | 7 | 6 | 7 | 5 | 7.6 / 7.1 | 5.4 | 9 / 8.8 | 6 / 6.1 |
| Shiva temple (WM) | 45.0 | -59.0 | 9 | 8 | 6 | 7 | 7.8 / 7.8 | 7.1 | 9 / 9.1 | 8 / 8.0 |
| Bhavani temple (WM) | 146.1 | -250.7 | 8 | 5 | 7 | 9 | 8.1 / 8.9 | 5.5 | 10 / 10.2 | 7 / 7.3 |
| Dudh Bav (WM) | 37.6 | -136.3 | 8 | 8 | 7 | 7 | 7.0 / 6.7 | 7.0 | 7 / 8.0 | 7 / 6.7 |
| Dahi Bav (WM) | 58.9 | -134.2 | 8 | 7 | 6 | 7 | 7.2 / 7.2 | 7.1 | 9 / 9.0 | 7 / 6.9 |
| Sakhar Bav (WM) | 95.9 | -174.3 | 8 | 8 | 7 | 7 | 8.5 / 7.8 | 8.2 | 9 / 8.6 | 8 / 7.2 |
| Rani chi Vela (WM) | -123.3 | -193.4 | 2 | 3 | 0 | 3 | 2.4 / 2.5 | 2.1 | 0 / 0.3 | 1 / 1.1 |
| Sweet water lake (WM) | 155.7 | 134.7 | 6 | 5 | 5 | 4 | 6.1 / 5.3 | 4.8 | 5 / 5.0 | 6 / 5.4 |
| Nishan Buruj (WM) | 22.3 | -204.1 | 7 | 7 | 6 | 7 | 8.1 / 8.5 | 5.8 | 5 / 4.7 | 6 / 6.2 |
| Padmagad (WM) | 590.8 | 538.8 | 0 | 0 | 5 | 1 | 2.2 / 2.3 | 0.4 | 0 / 0.0 | 0 / 0.0 |
| Malvan jetty (OSM) | 562.1 | 1346.8 | 0 | 3 | 0 | 0 | 0.0 / 0.0 | 0.0 | 0 / 0.0 | 0 / 0.0 |

- N-S transect at lon 73.4590 (X -8.6), by Y in metres, each as GLO-30 bilinear / SRTM30 / ALOS bilinear / NASADEM bilinear (m): -445.6 0.0/0/0.0/0.0; -390.3 0.0/0/0.0/0.0; -335.0 0.0/0/0.0/0.0; -279.8 0.0/0/0.0/3.2; -224.5 4.2/6/0.5/5.7; -169.2 6.0/6/4.1/4.8; -113.9 6.6/7/7.8/6.8; -58.6 6.3/7/7.8/7.2; -3.3 5.9/6/8.2/5.8; 52.0 7.1/7/7.2/6.4; 107.3 3.3/3/1.7/3.7; 162.5 0.0/2/0.0/1.4; 217.8 0.2/3/0.0/1.0; 273.1 1.2/4/0.0/1.0; 328.4 1.3/3/0.0/1.9; 383.7 0.1/0/0.0/0.0. Mapzen reads 3-4 m over this open sea where the others read 0.
- E-W transect at lat 16.0425 (Y -3.3), by X in metres, same four products: -276.0 0.0/0/0.0/0.0; -222.5 0.0/0/0.0/0.0; -169.0 0.0/4/0.0/3.0; -115.5 1.1/3/0.3/1.2; -62.1 2.7/4/2.8/2.2; -8.6 5.9/6/8.2/5.8; 44.9 8.9/8/9.5/7.0; 98.4 9.8/9/8.5/8.0; 151.9 4.4/7/4.9/5.4; 205.4 1.2/4/0.9/2.4; 258.9 0.0/5/0.0/2.4; 312.4 0.0/0/0.0/0.0; 365.9 0.0/0/0.0/0.0.
- Copernicus GLO-30 patch (72 rows x 40 columns, 0.000278 deg cells, upper-left 73.45375 E, 16.05625 N, i.e. lon 73.454-73.465, lat 16.036-16.056; stored in `dem_samples.json`): minimum -0.31 and maximum 17.56 m over the whole patch (the maximum is not on the island). Over the island the highest cells are 11.4, 10.9, 10.7, 10.6 and 10.5 m at X 69-128, Y -249 to -218 (the south end around the Bhavani temple), then 9.8 m at X 98, Y -3 and 9.4 m at X 69, Y 58.
- Other products at the origin: ETOPO1 +1 m and GEBCO 2020 -8 m (both bathymetry blends that do not resolve the island; GEBCO reads +5 m along the south end and -9 m to the west); Open-Meteo reads 3 m at the origin against 6.6 m for my GLO-90 bilinear read, and reads 5 m at several interior points where GLO-90 reads 5-7 m, so it is not identical to my AWS GLO-90 sampling (Open-Meteo documents the source as Copernicus-based; its exact sampling method was not checked). Mapzen tracks SRTM30 on land but returns 1-4 m over open sea.
- Spread among products (computed): taking GLO-30 bilinear as reference, over the 37 sample points where it reads at least 1 m, the mean difference / mean absolute difference / maximum absolute difference are: GLO-30 nearest -0.18 / 0.52 / 1.5 m; NASADEM bilinear -0.24 / 0.82 / 2.5; SRTM30 +0.57 / 1.05 / 2.8; GLO-90 bilinear -0.86 / 1.11 / 3.3; SRTM90 +0.33 / 1.29 / 3.9; ALOS bilinear -0.38 / 1.49 / 3.8; ASTER30 +0.41 / 1.64 / 4.3; Open-Meteo -1.29 / 1.95 / 4.2. (Selecting points by the reference's own reading biases these numbers somewhat.)

### Inferences
- Agreement among products of about 0.5-2 m mainly reflects shared resolution and a shared surface (canopy, buildings, walls); it does not demonstrate ground accuracy.
- All of these are surface models. Wikipedia gives the rampart as about 9.1 m high and 3.7 m thick, which is smaller than one 30 m cell, so a cell containing a bastion or wall top can read several metres higher than the ground beside it. The highest cells (10.5-11.4 m) are at the south end, where the bastions and the Bhavani temple area sit; I cannot separate wall and tree contributions without a survey, but the real ground inside the walls is probably lower than the central 7-11 m DSM values.
- The coast and the gate side are the least reliable: at the OSM gate the products read from 1.0 (GLO-90, ALOS) to 5.3 m (GLO-30 nearest), because a 30 m cell mixes rock, sea and quay. At the task-brief gate coordinate GLO-30 nearest, ALOS nearest and ASTER read 0 (sea) while SRTM30, SRTM90, NASADEM and Open-Meteo still read 3-5 m, so this is only weak, mixed evidence that the brief's point is displaced seaward (compare section 2). Every product sets sea cells to 0, so the DEMs give no bathymetry for the seascape; the only depth-like data are the coarse ETOPO1/GEBCO blends, which do not resolve the island.
- A defensible use is a smooth low-frequency trend only: a high ground running from the south end (about 9-11 m DSM) through the centre (about 6-10 m) toward the north-east, falling to about 3 m at Y of about 107 and to 0-3 m on the north tail, with 0-3 m at the eastern and western shores. Anything below about 5 m of relief should come from photos, a survey or the UNESCO/OSM outline.

### Gaps
- No product finer than 30 m was found or accessed. CartoDEM (ISRO/Bhuvan), FABDEM, TanDEM-X 12 m and any drone or LiDAR DEM from ASI, MRSAC or the Maharashtra archaeology directorate were not retrieved; their availability for this island is unconfirmed (Bhuvan downloads normally require registration; I did not attempt them).
- Published vertical-accuracy specifications and licences for each DEM were not read this session; verify before redistribution (Copernicus DEM, ALOS AW3D30 and NASADEM have different licence terms).
- Vertical datums (from my background knowledge, not re-checked: EGM96 for SRTM, ASTER, ALOS and NASADEM; EGM2008 for Copernicus) were not harmonised to local mean sea level, and the geoid-to-MSL offset on this coast was not looked up.
- No ground-truth heights (benchmarks, rampart crest levels) were found, so DEM error at the fort cannot be quantified.

---

## 4. What published measured drawings, site plans, boundary data and 3D models exist (UNESCO dossier, ASI, drone/photogrammetry, Sketchfab, Google Earth)?

### Takeaway
The only retrieved machine-readable boundary is the UNESCO 1739-011 core and buffer polygon (341-vertex core, 19.1 ha), which matches OSM and Wikimapia outlines to within about 1-9 m; the UNESCO map PDFs are huge and I did not open them, and I found no public measured drawing, photogrammetric model, Sketchfab model or Google Earth 3D data for Sindhudurg.

### Cited Findings
- UNESCO World Heritage listing 1739 "Maratha Military Landscapes of India": component 1739-011 Sindhudurg, 19.11 ha property and 783.59 ha buffer zone, N16 2 33 E73 27 35 — [UNESCO maps page](https://whc.unesco.org/en/list/1739/maps); documents list at [UNESCO documents page](https://whc.unesco.org/en/list/1739/documents/).
- UNESCO public ArcGIS FeatureServer queried with `outFields=*` and `f=geojson`: layer 1 (core) polygon for Sindhudurg with 341 vertices, area 19.1 ha; layer 2 (buffer) polygon with 70 vertices, about 783.7 ha (matches the 783.59 ha above); service base [FeatureServer](https://services6.arcgis.com/eMd5K6XXEvJETxfQ/arcgis/rest/services/prd_whc_sites_dossiers_elements_v2_view/FeatureServer). Stored as `unesco_1739-011_sindhudurg_boundary.geojson`. The service does not state a data licence in the responses I read.
- Dossier documents (UNESCO document IDs, URLs `https://whc.unesco.org/document/N`; sizes from HTTP headers, not downloaded): [209714](https://whc.unesco.org/document/209714) Maps, `1739-2592-Maps-en.pdf`, 332,116,566 bytes; [222454](https://whc.unesco.org/document/222454) "Maratha Military Landscapes of India - Maps of the inscribed property", `1739_maps.pdf`, 92,932,560 bytes; [209715](https://whc.unesco.org/document/209715) Annexes, `1739-2592-Annexes-en.pdf`, 1,238,014,351 bytes; [206086](https://whc.unesco.org/document/206086) Executive Summary; [206087](https://whc.unesco.org/document/206087) Nomination Text; [209713](https://whc.unesco.org/document/209713) Management Plan; [219084](https://whc.unesco.org/document/219084) Advisory Body Interim Report; [219040](https://whc.unesco.org/document/219040) Supplementary Information; [220595](https://whc.unesco.org/document/220595) Supplementary Information (Annexes); [222061](https://whc.unesco.org/document/222061) Advisory Body Evaluation (ICOMOS); [222063](https://whc.unesco.org/document/222063) Advisory Body Evaluation (IUCN). Titles are from the UNESCO documents list; only the sizes of 209714, 222454 and 209715 were checked.
- The executive summary includes boundary and buffer maps per component at 1:30,000, and the nomination file's annex table lists map files per component at 1:15,000 on A2 and 1:30,000 on A0; both were seen only for other components (Salher, Shivneri) in search-result excerpts, not confirmed for Sindhudurg. The dossier was prepared 2020-2023 by the Directorate of Archaeology and Museums, Maharashtra with the Archaeological Survey of India; each component has a Site Management Plan — [UNESCO Executive Summary](https://whc.unesco.org/document/206086), [UNESCO Management Plan](https://whc.unesco.org/document/209713).
- UNESCO document 221274 is a photograph (4000 x 3000 px) of Sindhudurg credited DRONAH from the nomination dossier, dated 2022-01-01; it is not a plan or drawing — [UNESCO document 221274](https://whc.unesco.org/fr/documents/221274).
- Search for measured drawings/photogrammetry returned no Sindhudurg-specific result; the nearest published work surfaced is a 2025 ISPRS paper that a search-result summary describes as being on Fort Vijaydurg (a different Konkan fort), combining viewshed analysis and photogrammetric output (paper not opened; the summary-to-URL pairing is my assumption) — [ISPRS 2025, XLVIII-M-9](https://isprs-archives.copernicus.org/articles/XLVIII-M-9-2025/965/2025/isprs-archives-XLVIII-M-9-2025-965-2025.pdf).
- A Maharashtra Remote Sensing Applications Centre (MRSAC) "Fort 3D mapping" document lists drone ortho-photo and 3D flythrough deliverables for Maharashtra forts, but Sindhudurg's inclusion could not be confirmed (server refused the connection when fetched) — [MRSAC fort 3D mapping](https://mrsac.gov.in/writereaddata/MRSAC/zip-files/15636166545d32e58e2d91cFORT3dmapping/files/basic-html/page2.html) (via search snippet only).
- A search for a Sketchfab model of Sindhudurg returned only unrelated models (Transylvania, Fort Negley, Fort Matanzas); a travel blog has drone video, not a model — [eNidhi drone footage](https://www.enidhi.net/2022/08/sindhudurg-fort-mh-drone-footage.html).
- Bastion counts in secondary sources conflict: search-result summaries gave 42 ("by modern counts"), 52 (with 45 stairways) and 53 bastions without a primary source I could identify; Wikipedia gives the rampart as about 3 km long, 9.1 m high and 3.7 m thick, and the fort as 48 acres — [Wikipedia: Sindhudurg Fort](https://en.wikipedia.org/wiki/Sindhudurg_Fort).

### Inferences
- The UNESCO core polygon is the best open vector for the rampart footprint: 341 vertices over about 2.8 km is a vertex every 8 m, similar to OSM, and the two outlines coincide to a few metres (section 6), so either is a defensible wall line; neither carries bastion detail or wall thickness.
- The 332 MB dossier Maps PDF and the 93 MB 2025 maps PDF probably hold site plans at the dossier's scales, but I did not open them, so whether they contain dimensioned or surveyed plans, contours, or bastion numbering is unknown. They are the first thing to inspect for a measured plan.
- Because several sources describe a drone-based dossier survey (DRONAH-credited imagery), a drone orthomosaic probably exists with the state archaeology directorate or ASI, but nothing public was found.

### Gaps
- Contents of UNESCO documents 209714, 222454, 209715 were not opened (sizes of 93 MB to 1.2 GB; downloading needs your approval). Whether they include dimensioned plans, elevations or a bastion-by-bastion survey is unverified.
- No ASI conservation plan, measured drawing or site plan for Sindhudurg was located; no INTACH, university or academic measured drawings were found.
- Google Earth 3D / Maps photogrammetry for the fort was not inspected (no machine-readable access route found); no Sketchfab, Mapillary or Wikimedia Commons check beyond the web search above.
- Bastion count (42 vs 52 vs 53) is unresolved across secondary sources and I identified no primary source; see sibling notes on walls and bastions.
- Licence for UNESCO imagery, maps and the FeatureServer data is not established (UNESCO document pages carry their own copyright notices; not retrieved).

---

## 5. What historical survey maps and Admiralty charts of Sindhudurg / Malwan exist and what detail do they give?

### Takeaway
There are at least two held-and-catalogued sea charts that cover the fort: an 18th-century Admiralty/Dalrymple "View and plan of Sinderdroo or Melundy" (1765 survey, printed 1774) and a late-19th-century Admiralty chart "Malwan to Vengurla" with a Malwan Bay inset, but I could not view either image, so the actual fort detail, bastion count and soundings are unconfirmed.

### Cited Findings
- National Maritime Museum G254:6/10, "India - West Coast Malwan to Vengurla including the Karil Kachal Channel surveyed by Commander L.S. Dawson RN ... 1882", HM Admiralty, date made 1886, scale 1:36,300, sheet 100 x 68.5 cm, with two insets (Malwan Bay and Vengurla, both about 1:12,000) plus two views and drawings of shore marks; catalogue does not mention the fort or soundings; rights "© Crown copyright. National Maritime Museum, Greenwich" — [RMG object 549769](https://rmg.co.uk/collections/objects/rmgc-object-549769).
- National Maritime Museum G254:6/44, "View and plan of Sinderdroo or Melundy on the Malabar Coast by Co. John Watson, 1765", creators HM Admiralty, Alexander Dalrymple, John Watson, P. Begbie (engraver), William Whitchurch (lettering); date made 1774; scale about 1:25,000; sheet 22.5 x 31.7 cm; "Table of references" and one view; rights © Crown copyright NMM — [RMG object 551098](https://rmg.co.uk/collections/objects/rmgc-object-551098). The catalogue does not say whether a fort outline, bastions or soundings are shown.
- A Gallica (Bibliotheque nationale de France) copy of the same Watson/Dalrymple plan, ark `btv1b532583381`, reported in search snippets as public domain with soundings ("sondages sous-marins") and Sindhudurg fort subject tags, scale given as two nautical miles — [ISIDORE record](https://isidore.science/document/12148/btv1b532583381), [South Asia Commons record](https://southasiacommons.net/artifacts/5026019/view-and-plan-of-sinderdroo-or-melundy-on-the-malabar-coast-by-co/5791392). (Both pages were blocked or reset when I fetched them; the descriptions come from search-result summaries only.)
- British Library photograph Photo 146/1(193) "Sindhudurg Fort, Malwan [Malvan]. The Konkun Coast", Thomas Walters Venn, 1930-1939, gelatin silver print 58 x 101 mm; a photograph, not a plan — [British Library record 041-003049846](https://searcharchives.bl.uk/catalog/041-003049846).
- A 1756 plan of Gheriah (Vijaydurg) with soundings exists at UC Berkeley and is a different fort; it is useful only as a stylistic comparison — [UC Berkeley GeoData](https://geodata.lib.berkeley.edu/catalog/72a691b8-689a-4997-8786-8cafca71142b).

### Inferences
- A 1:25,000 plan on a 22.5 x 31.7 cm sheet would show the island at only about 2 cm, so the Watson plan can at best give the island outline, approaches and soundings, not bastion-scale detail; a 1:12,000 Malwan Bay inset would show the fort as about 4 cm and likewise not resolve individual bastions. Neither can supply 1:1 geometry (reasoning from the catalogued scales).
- The Dawson chart, being a later survey, is the likelier source for the bay's approach channel, reef positions and charted depths; those could be compared with the OSM seamark rocks to place submerged reefs, but this needs the chart image.
- "Sinderdroo or Melundy" equating to Sindhudurg/Malvan is supported by the Gallica subject tags as reported in search snippets, not by anything I read directly.

### Gaps
- Images of both Admiralty/NMM charts and the Gallica copy were not retrieved or inspected; I cannot report soundings, wall plan or bastion count from them.
- No Survey of India sheet (Indian Atlas, SoI 1:63,360 or 1:25,000), British Library Indian Atlas, or ASI 19th-century plan of Sindhudurg was found.
- UK Hydrographic Office chart catalogue and the modern Indian Naval Hydrographic Office chart (Malvan) were not searched.
- The second British Library record (041-003049847) surfaced in search but was not opened.

---

## 6. How do the sources compare: coordinate offsets, precision and licences?

### Takeaway
The OSM, Wikimapia and UNESCO island outlines agree to about 1-9 m, and the best-matched building pairs agree to 1.3-4.4 m, so a combined outline is trustworthy to roughly +/-10 m; single-point "fort" coordinates (Wikidata, Wikipedia, UNESCO, OSM node) are 8-257 m apart and are not usable for placement. Licences are mixed: OSM is ODbL, Wikimapia is CC BY-SA, NMM charts are Crown copyright, the DEMs and UNESCO data have unverified terms.

### Cited Findings
- Island-outline extents in the local frame (computed from the retrieved data): OSM coastline way X -221..301, Y -398..352 ([way 19804981](https://www.openstreetmap.org/way/19804981)); UNESCO core polygon X -217..304, Y -397..354 ([UNESCO FeatureServer](https://services6.arcgis.com/eMd5K6XXEvJETxfQ/arcgis/rest/services/prd_whc_sites_dossiers_elements_v2_view/FeatureServer)); Wikimapia island polygon X -226..297, Y -401..350 ([Wikimapia 101740](http://wikimapia.org/101740/)). Areas: OSM 19.10 ha, UNESCO 19.1 ha (official 19.11 ha), Wikimapia 18.97 ha.
- Single-point fort coordinates (X, Y): OSM node (108.0, 28.7); Wikidata (83.3, -59.0); Wikipedia (249.9, 137.0); UNESCO (68.7, -3.3) — sources as in section 2.
- Licences: OSM ODbL ([copyright](https://www.openstreetmap.org/copyright)); Wikimapia CC BY-SA 3.0 as stated on the site ([Wikimapia](https://wikimapia.org/)); NMM charts "© Crown copyright. National Maritime Museum, Greenwich" ([RMG](https://rmg.co.uk/collections/objects/rmgc-object-549769)); the Gallica copy of the Watson plan reported as public domain ([South Asia Commons](https://southasiacommons.net/artifacts/5026019/view-and-plan-of-sinderdroo-or-melundy-on-the-malabar-coast-by-co/5791392)).

### Inferences
- Outline offsets (computed): OSM minus UNESCO is -4/-3 m (west/east extents) and -1/-2 m (south/north); Wikimapia minus OSM is -5/-4 m and -3/-2 m; Wikimapia minus UNESCO is -9/-7 and -4/-4 m. The outlines differ by 9 m at most, a uniform Wikimapia shift of about 4-9 m south-west relative to UNESCO, which is within ordinary tracing error; none of these extents suggests the 20-25 m offset I suspected earlier.
- The DEM samples add a weak check: the brief's gate coordinate reads 0 m (sea) in GLO-30 nearest, ALOS nearest and ASTER, against 5.3 m, 1 m and 4 m respectively at the OSM and Wikimapia gate positions; but SRTM30/90, NASADEM and Open-Meteo read 3-5 m at both, so the DEMs alone do not settle which gate position is right.
- Perimeter 2.80 km (OSM) is consistent with Wikipedia's "about 3 km" rampart, and the 19.1 ha area with the "48 acre" (19.4 ha) figure, so the outlines enclose the right ground.
- If a single coordinate is needed for the fort centre, the area-based centre of the three outlines (X about 64-84, Y about -34..-22; section 2) is a better choice than any of the four published points.
- Using OSM/Wikimapia data in a distributed model requires ODbL (share-alike, attribution) and CC BY-SA compliance; the model's own geometry should be derived from, and credit, those sources if redistributed.

### Gaps
- No ground control points (GCPs) or surveyed benchmarks were found to establish absolute accuracy of any source.
- Imagery date and georeferencing of OSM and Wikimapia tracing are unknown; tracing from different imagery vintages could explain the 4-9 m differences.
- Licence terms of the UNESCO ArcGIS service, DEM products and the dossier PDFs are not verified.
