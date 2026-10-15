SINDHUDURG FORT (Kurte island, off Malvan, Maharashtra) - low-poly replica
======================================================================
Units: metres. Z up. +Y = north, +X = east (towards Malvan). Sea level = Z 0.
Interior ground = Z 2.0 (assumed). Everything lives in scene "Sindhudurg",
collection SINDHUDURG. To rebuild: open sd_build_all.py in the Text Editor
and press Run Script.

1. RESEARCHED FACTS USED IN THE MODEL
-------------------------------------
Built 25 Nov 1664 - 1667 for Chhatrapati Shivaji Maharaj as the Maratha naval HQ.
Work credited to Hiroji Indulkar (CCRT) or Govind Vishwanath Prabhu (Marathi
Vishwakosh); ~3,000 workers + Portuguese masons from Goa (CCRT).
Foundation stones set in poured molten lead.
UNESCO: component 1739-011 of "Maratha Military Landscapes of India" (2025);
property 19.11 ha, buffer 783.59 ha, N16 2 33 E73 27 35. ASI protected.

Dimensions (sources disagree - the model uses the first value):
  Area ............ 19.0 ha modelled  (48 acres ~19.4 ha; UNESCO 19.11 ha)
  Wall height ..... 9.1 m / 30 ft     (gazetteer 29-30 ft; Vishwakosh ~10 m)
  Wall thickness .. 3.7 m / 12 ft
  Bastions ........ 42                (Vishwakosh, CCRT; 1880 gazetteer ~32;
                                       some sites say 52 or 26 - unreliable)
  Bastion spacing . 40-130 yd (37-119 m), half-round, embrasured parapets
  Wall circuit .... documented 3.2-4 km; MODEL = 2.1 km trace / ~2.4 km walk
                    (see section 3 - area and circuit cannot both hold for a
                    plausible outline; area was prioritised)
Main gate (Mahadarwaja / Dilli Darwaja): NE corner, deep water even at low
  tide, hidden behind two bastions (gomukhi / "hidden semi-circular entrance"),
  narrow passage; ruined nagarkhana (drum house) above; Hanuman shrine just
  inside. Model: notch in the trace + screen wall from the north bastion, door
  faces the screened courtyard and is invisible from the sea.
Shivaji hand + foot prints: two small niches with little domes on the wall
  to the right of the main gate.
Shivrajeshwar temple: centre of the fort, built in Rajaram's reign
  (1689-1700); original 13 x 7 m; front hall added by Shahu of Kolhapur 1907.
Mahadev temple behind it, with a square deep stepwell, Nandi, Shivling.
Three sweet-water wells: Dudhbav, Dahibav, Sakharbav.
Jarimari temple on the path after the gate (inscription 1881); Bhavani,
  Mahapurush temples; palace ruins; tall isolated Nishankathi / Jhenda /
  Darya buruj (flag bastion) west of the palace ruins.
Ranichi Vela: small sand beach below the south wall with a door in the wall
  (Wikipedia photo caption says west side - CCRT says south; model = south).
Living fort: ~15-20 resident families, anganwadi / pre-primary school.
Satellite works: Padmagad (shipyard islet towards the shore), Rajkot and
  Sarjekot on the mainland (not modelled).

2. WHAT IS IN THE SCENE (collections)
-------------------------------------
SD_00_Guides ........ SD_GUIDE_Outline (editable wall trace), gate/beach
                      markers, hidden boolean cutters (not rendered)
SD_10_Fortifications  SD_Wall_Curtain, SD_Wall_Parapet (+merlons),
  SD_11_Bastions .... 42 x SD_Bastion_## + SD_Bastion_Gate_North/South
  SD_12_Wall_Stairs . 21 linked copies of one stair mesh
SD_20_Gate_Complex .. arch frame, doors (hinged origins), screen wall,
                      courtyard, nagarkhana ruin, print domes, Hanuman
                      shrine, jetty, Ranichi Vela door
SD_30_Interior ...... ground, paths, Shivrajeshwar temple (own sub-
                      collection, 7 parts), shrines + wells, settlement,
                      vegetation (instanced palms/trees), cannons
SD_40_Terrain_Sea ... rock shelf, reef rocks, beach, sea, Padmagad
SD_90_Camera_Light .. 4 cameras, sun

3. ACCURACY - READ THIS
-----------------------
* No measured plan or open vector footprint of the wall was reachable, so
  the trace is a hand-built approximation: right area, NE gate, south beach,
  irregular "projecting points and deep indentations" - but NOT the real
  outline. Fix: drop a top-down satellite image behind the top view,
  edit SD_GUIDE_Outline vertices in Edit Mode (keep it one closed loop),
  move the SD_GUIDE_Gate A-D / SD_GUIDE_Beach empties onto the real gate
  and postern, then Run Script on sd_build_all.py. Bastions, parapets,
  stairs, ground, rock shelf and cuts all regenerate from the trace.
* Interior positions are representative; the inventory is sourced, the
  layout is not surveyed. Temple elevations follow typical Konkan forms.
* Bastion count fixed at 42 (custom property bastion_target on the guide).

4. TEXTURING
------------
* Every mesh has a "UVMap" in real-world metres (1 UV unit = 1 m). Walls,
  parapet and walkway use a continuous U along the wall length, so tiling
  textures run unbroken around the circuit. Bastions use cylindrical UVs.
* Each material already contains UV -> Mapping (scale = 1 / tile size) ->
  an empty Image Texture labelled "PLUG TEXTURE HERE". Load an image there
  and connect it to Base Color (and add normal/roughness the same way).
  The tile size is stored on each material as custom property tile_m.
* Material slots split surfaces by role (outer wall / inner wall / walkway /
  parapet, plaster / roof tile / timber, etc.) - 26 SD_ materials total.
* Repeated assets share mesh data: houses (3 variants), palms, trees,
  cannons, stairs. Texture one and every copy follows.

5. SOURCES
----------
UNESCO WHC 1739 maps/areas: https://whc.unesco.org/en/list/1739/maps
Wikipedia: https://en.wikipedia.org/wiki/Sindhudurg_Fort
Anantam IAS study note (quotes 1880 Ratnagiri Gazetteer, Marathi Vishwakosh,
  CCRT, ICOMOS): https://anantamias.com/sindhudurg-fort/
Durgbharari: https://durgbharari.in/sindhudurg/
RTF case study: https://www.re-thinkingthefuture.com/case-studies/a2791-sindhudurg-fort-the-1664-architecture-marvel-constructed-on-an-island/
Govt (FFO): https://ffo.gov.in/locations/locationInformation/192
orbat.info: https://orbat.info/cimh/forts/sindhudurg.html
Not reachable from the build session (worth reading for a v2): the 1880
Ratnagiri Gazetteer (gazetteers.maharashtra.gov.in), the UNESCO nomination
dossier (whc.unesco.org/document/206086), "Study of Sea Fort Construction
Techniques in Maharashtra" (ResearchGate 381851543), IJCS-18-60 lime-plaster
paper (ijcs.ro/public/IJCS-18-60_Singh.pdf), OpenStreetMap footprint.
