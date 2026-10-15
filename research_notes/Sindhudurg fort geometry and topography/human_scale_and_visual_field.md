# Human-scale reference dimensions and remaining geometric/visual-field factors around Sindhudurg Fort

Compiled 2026-10-13 for a 1:1 metre-scale Blender reconstruction. Source quality varies: official (Maharashtra Tourism, ASI tender, CPCRI, INCOIS, IMD) > scholarly (NFHS, NCD-RisC, ICRAF) > the old Bombay Gazetteer transcription > travel blogs and aggregator sites (flagged "low reliability" where used). Items labelled "Calculation" are my own arithmetic (NOAA-style solar formulae, spherical geometry), not citations. Coordinates: fort = 16.043769 N, 73.461416 E ([Wikipedia](https://en.wikipedia.org/wiki/Sindhudurg_Fort)).

## 1. What reference human height and eye height should the model use (India / Maharashtra / Konkan; modern and 17th century)?

### Takeaway
Use a 1.65 m adult male as the single scale figure (eye height about 1.53-1.55 m), with a 1.525 m adult woman as the secondary figure; both are anchored on two independent national datasets that agree. No Maharashtra/Konkan-specific or 17th-century Maratha height was found, so use the national figure for both and treat as +/- 5 cm.

### Cited Findings
- NFHS-3 average adult heights are 165 cm (men) and 152 cm (women), ages 20-49, with a secular trend of about +0.50 cm/decade (men) and +0.22 cm/decade (women) — [SAGE, Food & Nutrition Bulletin](https://journals.sagepub.com/doi/10.1177/156482651103200103)
- NCD-RisC (via Our World in Data): India 1996 birth-cohort mean height is 164.95 cm for men and 152.59 cm for women (cohort aged 18 in 2014) — [OWID men](https://ourworldindata.org/grapher/average-height-of-men?overlay=download-data); [OWID women](https://ourworldindata.org/grapher/average-height-of-women)
- NCD-RisC reports that the South Asian plateau is 5-10 cm below Japan/South Korea and that the male-female gap is about 12 cm for the 1996 cohort (164.95 - 152.59 = 12.4 cm, consistent) — [eLife 2016 PDF](https://cdn.elifesciences.org/articles/13410/elife-13410-v2.pdf)
- Between NFHS-3 and NFHS-4, Indian male height fell by 1.10 cm (ages 15-25) and 0.86 cm (ages 26-50); Maharashtra is among the states with a significant decline for men aged 26-50 — [PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0255676)
- An NFHS-5 Maharashtra state report exists but I could not extract a mean adult height from it — [DHS FR374 Maharashtra](https://dhsprogram.com/pubs/pdf/FR374/FR374_Maharashtra.pdf)

### Inferences
- Recommended figures (rounded from the 165 / 152.6 cm anchors, which agree across NFHS-3 and NCD-RisC):
  - Adult male: stature 1.65 m. Eye height about 0.93 x stature = about 1.53 m (general anthropometric rule of thumb, not cited here).
  - Adult woman: stature 1.525 m. Eye height about 1.42 m.
  - Walk-through camera height: 1.55 m (covers the male eye height, a little above female).
- A one-time NFHS-4 male decline of about 1 cm is within the +/- 5 cm tolerance, so it does not change the recommendation.
- The secular trend (+0.5 cm/decade for men) implies 17th-century people were probably not taller than today, but extrapolating 350 years linearly is not valid. Keep 1.65 m and do not invent a "period soldier" height.

### Gaps
- No measured or documentary height for 17th-century Maratha soldiers/mavle was found.
- No Maharashtra- or Konkan-specific mean adult height (NFHS-5 state report not extracted; ICMR-NIN data not found).
- A search summary of DHS forum threads suggested NFHS-3/4/5 men's heights are inconsistent across rounds (not for women); I did not verify this directly, so it is not cited.

## 2. Traditional units (hath, gaj) and Maratha/Konkan built dimensions relative to humans (doors, plinths, stairs, wall-walk, parapet, merlons, jangya)

### Takeaway
A hath is about 18 in (0.457 m); gaz values vary regionally (0.686-0.914 m) so "gaj" must not be converted without knowing the region. For Sindhudurg itself I found no numeric door, stair, parapet, merlon or jangya heights; only wall bulk (about 9 m high, 3-4 m thick), qualitative features, and analogue dimensions.

### Cited Findings
- Hath is approximately 18 in (about 0.457 m); gaz values listed include Bombay 27 in (0.686 m), Madras/government 33 in (0.838 m), Bengal 36 in and Akbar's Ilahi gaz 33-34 in — [Wikipedia, Indian units of measurement](https://en.wikipedia.org/wiki/Indian_units_of_measurement). Conflict: the same page's "2 hath = 1 gaz" line implies 36 in (0.914 m), which matches only the Bengal gaz, not the Bombay one.
- Shivaji-era land-measure kathi (Shivkathi) is 5 5/6 cubits = 114.035 in (2.896 m) — [Maharashtra State Gazetteer, Kolaba District, early land measures](https://www.gazetteers.maharashtra.gov.in/cultural.maharashtra.gov.in/english/gazetteer/Kolaba%20District/land_early.html)
- Konkan houses use square-ish modules of 9x13, 11x15 and 13x17 arm lengths and a steep timber stair to the attic — [IJERT/RIP paper on Konkan houses](https://www.ripublication.com/irph/ijert_spl17/ijertv10n1spl_04.pdf)
- Warli (Thane) analogue, not Malvan: 1 hand = 1 ft 6 in; core room height 5 hands (7 ft 6 in = 2.29 m); plinth 12-18 in (0.30-0.46 m) — [Remi De Souza blog, low reliability](https://remidesouza.blogspot.com/2010/05/warli-house-and-habitat-1.html)
- Qualitative Maratha parapet: semicircular/pointed merlons with loopholes in merlons and under crenels — [HistoryMarg](https://www.historymarg.com/2023/12/the-war-architecture-and-shivaji-raje.html) (low reliability, no dimensions)
- Sindhudurg walls (headline): 48 acres, rampart about 3 km, walls 30 ft (9.1 m) high and 12 ft (3.7 m) thick — [Wikipedia](https://en.wikipedia.org/wiki/Sindhudurg_Fort); [Maharashtra Tourism](https://maharashtratourism.gov.in/fort/sindhudurg/)
- Conflicting wall figures: rampart 9 m high x 3 m wide, 4 km zigzag — [Hindu Janajagruti Samiti](https://www.hindujagruti.org/history/40075.html); foundation walls 4 m thick, rampart to 10 m, wall length 3.2 km, enclosed area about 15 ha (vs 48 acres = 19.4 ha) — [Indian Military History](https://indianmilitaryhistory.org/forts/sindhudurg.html)
- Old Gazetteer text: walls 29-30 ft, average 12 ft thick, about 32 towers spaced 40-130 yards apart (36.6-118.9 m, calculation), towers are outstanding semicircles with embrasures, "stones projecting inwards drilled with flag staff holes", narrow staircases from inside to the wall-top, entrance at the north-east corner — [Bombay Gazetteer transcription](https://shivshahi.tripod.com/sindgaze.html)
- Bastion/tower count conflict: 32 towers ([Gazetteer](https://shivshahi.tripod.com/sindgaze.html)), 42 bastions ([Hindu Janajagruti](https://www.hindujagruti.org/history/40075.html), [Merwyn's blog](https://merwynsrucksack.blogspot.com/2014/02/sindhudurg-fort.html)), 52 bastions ([Shivaji's Forts](https://shivshahi.tripod.com/sindhu.html)), 52 embrasures ([Indian Military History](https://indianmilitaryhistory.org/forts/sindhudurg.html)), 29 bastions ([MeghaBlogs](https://meghablogs.com/en/sindhudurg-fort-malvan/), low reliability).
- Wall-walk: "six people could walk easily on it, side by side" (anecdote) — [Merwyn's blog](https://merwynsrucksack.blogspot.com/2014/02/sindhudurg-fort.html)
- Stairs: "narrow and huge steps ... extremely steep" ([Merwyn's blog](https://merwynsrucksack.blogspot.com/2014/02/sindhudurg-fort.html)); "uneven ... no safety features" ([Inditales](https://inditales.com/sindhudurg-fort-konkan-coast/)); one site claims 42 staircases ([MeghaBlogs](https://meghablogs.com/en/sindhudurg-fort-malvan/), low reliability).
- Main entrance is hidden behind a 30 ft (9.1 m) bastion, with Jarimari temple in front — [TrekFORTS](https://www.oocities.org/trekforts/f_sindhudurg.html); door is teak, "jangyas" are described as slanted holes for pouring boiling oil — [MeghaBlogs](https://meghablogs.com/en/sindhudurg-fort-malvan/) (low reliability)
- Condition in 1828: the west and south faces had parapet "not above two feet remaining" in places, with terreplein washed away — [Bombay Gazetteer transcription](https://shivshahi.tripod.com/sindgaze.html)
- Analogue only: Vijaydurg bastion diameter 23.31 m, height 15.63 m — [Exa library record of a Vijaydurg paper](https://exa.ai/library/publication/vvpf31lxyrj)
- A 2026 University of Auckland architectural thesis covers Sindhudurg as a case study and may contain measured dimensions, but only the abstract was accessible (PDF not read) — [Kulkarni, Auckland ResearchSpace](https://researchspace.auckland.ac.nz/items/bb42bae3-d326-4ad3-89b3-d5c5ed5b4966)

### Inferences
- If a Konkan "arm length" means a hath, the house modules are 4.1 x 5.9 m, 5.0 x 6.9 m and 5.9 x 7.8 m (calculation); treat as a plausible span range for fort houses, not a measured fact.
- Six people abreast at about 0.6 m each is about 3.6 m, which is consistent with a 3.7 m (12 ft) thickness; the usable wall-walk is the thickness minus the parapet, so model about 3.0-3.5 m clear, unless photos show otherwise.
- Stair planning check (calculation): if a flight climbs the full 9.1 m wall height, a 0.20 m riser needs about 46 steps and a 0.25 m riser about 36 steps, so flights run roughly 9-11 m along the inner wall face and cannot fit inside the wall thickness. Riser and tread values are unmeasured. Descriptions as "huge and steep" suggest risers above modern norms, so calibrate from photos using the 1.65 m figure rather than a code value.
- The old Gazetteer's 52 vs 42 vs 32 counts probably reflect different definitions (embrasure vs bastion vs tower); the wall-circuit researcher should resolve against a plan.

### Gaps
- No numeric figure for: gate (Mahadarwaza) width/height; door heights; stair riser/tread; parapet height; merlon height; jangya height/position; interior ground level vs outside (so true free wall height inside is unknown).
- The Kulkarni thesis PDF (12.9 MB) was not fetched and is the most promising source for measured values.
- Whether "gaj" is used in any Sindhudurg-specific historical document was not found.

## 3. What vegetation grows inside and on the fort, and what are mature dimensions and spacing?

### Takeaway
Documented on the fort: coconut palms (about 300-400, sparse), a few small fig trees on the walls (1828), vegetables, and unspecified "beautiful trees" around the Shivaji temple. None of the other listed species (banyan, peepal, mango, cashew, kokum, jackfruit, casuarina, tamarind, badam, pandanus, Calotropis, Lantana, Prosopis) has a fort-specific source, so they are model-choice assumptions. Coconut sizing and spacing are well sourced; mango and banyan sizes have wide ranges.

### Cited Findings
- Fort-specific presence:
  - "Some 300-400 coconut trees at present" (page dated 2012), land inside unsuitable for cultivation because of sea water, "only vegetables are grown", land mostly private, 10 houses with about 20 people — [MalvanCity](https://www.malvancity.com/sindhudurg-fort/)
  - Interior "mostly empty, except rubble walls, small step wells and coconut groves" — [WebIndia123](https://tourism.webindia123.com/tourism/monuments/forts/Sindhudurg_Fort/index.htm)
  - Houses on the fort "produce coconut and vegetables"; a rare branched coconut tree is to the left after the entrance — [TrekFORTS](https://www.oocities.org/trekforts/f_sindhudurg.html)
  - "Beautiful trees surround" the Shivaji temple; "coconut trees forming the skyline" on the mainland — [Inditales](https://inditales.com/sindhudurg-fort-konkan-coast/)
  - "A few coconut trees grew in its premises" (viewed from the sea) — [Merwyn's blog](https://merwynsrucksack.blogspot.com/2014/02/sindhudurg-fort.html)
- Branched coconut tree conflict: still standing per [MalvanCity](https://www.malvancity.com/sindhudurg-fort/) and [WebIndia123](https://tourism.webindia123.com/tourism/monuments/forts/Sindhudurg_Fort/index.htm); struck by lightning in 2009 and lost per [Parisa Beach Resort](https://parisabeachresort.com/sindhudurg-fort-information-and-travel-guide/) (resort marketing page, low reliability).
- Vegetation on walls: in 1828, "a few fig trees had here and there made their appearance, but they were of no great size" on the north and east faces — [Bombay Gazetteer transcription](https://shivshahi.tripod.com/sindgaze.html)
- A 2018 restoration "cleared overgrown vegetation from the 42 bastions" and restored a stone-paved perimeter walkway — [HiddenRoutes](https://hiddenroutes.in/monuments/sindhudurg-sea-fort-malvan) (low reliability; the same page calls the ramparts basalt, which I could not corroborate)
- Neighbouring sites: Padmagad/"Pandavgad" island has "ruins and coconut palms" ([Gazetteer transcription](https://shivshahi.tripod.com/sindgaze.html)); Sarjekot village sits in "gardens of coconut trees" ([Exa place record](https://exa.ai/library/place/gjc5hpwntfr)).
- Coconut, tall type (West Coast Tall): height 15-18 m, life span 60-80 years, dwarfs 5-7 m — [ICAR-CPCRI](https://cpcri.gov.in/filemgr/webfs/publication/Coconut_English_No133.pdf); [Coconut Board](https://coconutboard.in/images/Packageofpractice.pdf)
- Coconut planting spacing: 7.5 x 7.5 m to 8 x 8 m square (156-177 palms/ha), hedge 6.5 m x 9.5 m, wide 10 x 10 m for intercropping — [ICAR-CPCRI](https://cpcri.gov.in/filemgr/webfs/publication/Coconut_English_No133.pdf)
- Coconut root and crown: main roots extend laterally up to 10 m; crown holds about 15 open and 15 developing leaves; trunk is unbranched — [TNAU](https://agritech.tnau.ac.in/expert_system/coconut/coconut/coconut_varieties.html)
- Coconut trunk girth: Tiptur Tall 71-87 cm, Lakshadweep Ordinary 80 cm at about 11.6 m height — [Jay Hind Farm](https://jayhind.farm/coconut-varieties/) (aggregator)
- Mango (Mangifera indica): 10-40 m tall, crown radius 10 m, grafted trees 6-9 m — [Phytojournal 2018](https://www.phytojournal.com/archives/2018/vol7issue2/PartAT/7-2-211-896.pdf); to 20 m with trunk diameter 90 cm — [ICRAF AgroForestryDB](https://apps.worldagroforestry.org/treedb/AFTPDFS/Mangifera_indica.PDF); up to 90 ft (27 m) tall and 80 ft (24 m) wide, planted 35-40 ft (10.7-12.2 m) apart — [CTAHR Hawaii](https://www3.ctahr.hawaii.edu/oc/freepubs/pdf/hc-2.pdf). Conflict: canopy "100-125 ft" (30-38 m) wide in [eFlora of India](https://efloraofindia.com/efi/mangifera-indica/) versus the 10 m radius above.
- Banyan (Ficus benghalensis): over 30 m tall, can spread to 180+ m via aerial-root trunks — [ICRAF](https://apps.worldagroforestry.org/treedb2/AFTPDFS/Ficus_benghalensis.PDF); up to 30 m tall per [Kew POWO](https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:852482-1/general-information); the largest known individuals have crown spreads of 100-200 m — [Outreach Ecology report](https://outreachecology.com/landmark/media/pdfs/TheWorldsLargestTrees-CataloguingIndiasGiantBanyans-byYDBar-Ness-OutreachEcologyReport-Jun10.pdf)

### Inferences
- Density (calculation): 300-400 palms over 19.4 ha (48 acres) is about 15-21 palms/ha, versus 156-177/ha in a plantation. Palms are therefore clustered near houses and the temple, not a uniform grove; the open interior in the WebIndia123 description fits.
- Recommended coconut model values (derived, to be checked against photos): mixed age 8-18 m (tall type), trunk diameter about 0.25-0.35 m (girth 71-87 cm gives 0.23-0.28 m, plus bole flare), crown diameter about 6-8 m, centre spacing at least 7.5 m in groves (CPCRI planting norm is set so that mature crowns just touch). Palms on exposed coasts lean with wind; no lean data was found, so take lean from photos.
- Fig on walls: Ficus saplings rooting in masonry joints are the plausible reading of "fig trees" in 1828 (inference; species unspecified). Use small trees, under 3 m, at isolated wall-top and joint locations on north and east faces. A 2018 clearance claim suggests fewer wall plants now; low confidence.
- Spacing guidance by size class (derived from sourced maxima): keep mango crowns at least 10-12 m apart, banyan or peepal crowns at least 20 m from other large trees. Mature banyan or mango on this site is a modelling choice; with no fort-specific evidence, prefer a small number of medium trees near the temple.
- Trees belong on the interior side only; the exposed west and south faces take monsoon waves (see Q5) and are unlikely to host trees.

### Gaps
- No botanical survey of the fort; species other than coconut and fig are unconfirmed.
- No sourced crown spread or trunk diameter for West Coast Tall coconut, nor for cashew, casuarina, kokum, jackfruit, tamarind, badam, pandanus, Calotropis, Lantana or Prosopis.
- No source on coconut lean, nor on which trees surround the Shivaji temple.

## 4. Sun path at 16.04 N, and haze/visibility

### Takeaway
Solar noon elevation ranges 82.6 deg (21 June) to 50.5 deg (21 December), noon is at about 12:30-12:37 IST, and sunrise/sunset azimuths swing between 66-114 deg and 246-295 deg. The sea horizon to the west is unobstructed, so sunsets happen over open water. No haze/visibility statistics were found.

### Cited Findings
- Fort latitude 16.0438 N, longitude 73.4614 E — [Wikipedia](https://en.wikipedia.org/wiki/Sindhudurg_Fort)
- Boats are suspended roughly June-September (monsoon) — [Travel Konkan](https://travelkonkan.in/sindhudurg-fort/); best season November-February — [Parisa Beach Resort](https://parisabeachresort.com/sindhudurg-fort-information-and-travel-guide/) (low reliability). Indicates cloud and rain dominate the June-September light, though no haze data was found.

### Inferences
Calculation (NOAA-style solar-position approximation, IST = UTC+5:30, geometric horizon, no refraction; verify in Blender with a test shadow):

| Date | Declination | Noon max elevation (azimuth) | Sunrise (azimuth) | Sunset (azimuth) |
|---|---|---|---|---|
| 20 Mar (equinox) | -0.3 deg | 73.5 deg (180, south) | 06:46 (91) | 18:44 (270) |
| 21 Jun (solstice) | +23.5 deg | 82.6 deg (about 1, north of zenith) | 06:09 (66) | 19:07 (295) |
| 22 Sep (equinox) | +0.4 deg | 74.6 deg (180) | 06:29 (89) | 18:30 (271) |
| 21 Dec (solstice) | -23.4 deg | 50.5 deg (180) | 07:03 (114) | 18:06 (246) |

- Elevation/azimuth at 09:00 and 16:00 IST: Mar/Sep 32-36 deg at az 101 and 36-39 deg at az 256-259; Jun 39 deg at az 73 and 42 deg at az 287; Dec 25 deg at az 126 and 26 deg at az 233.
- Noon on 21 Dec: elevation 50.5 deg, so a 9.1 m wall casts a shadow of about 7.5 m onto the north side; 09:00 shadow about 19.5 m toward az 306; 16:00 shadow about 18.7 m toward az 53. At June noon the sun is just north of zenith (about 1.2 m shadow toward south). The sun is north of the zenith only while declination exceeds 16.04 deg, i.e. roughly early May to early August.
- Practical check: on 21 Dec at noon the shadow of a 1 m post must point north (+Y) with length 0.82 m.
- Sunrise is over the mainland (Malvan) and the Sahyadri direction; sunset is over open sea. The sea-facing west walls therefore receive afternoon light at low angles, and the interior is lit from the east until late morning.

### Gaps
- No measured haze, aerosol or visibility range statistics for Malvan (IMD visibility data was not located).
- Cloud-cover fractions by month were not collected.

## 5. Sea state: waves, tides, and sea level relative to the wall toe

### Takeaway
Tidal range is roughly 1.6 m mean, up to about 2.6 m at spring (model predictions, datum uncertain). Monsoon swell forecasts reach 3.2-3.5 m on this coast, while fair-season nearshore waves are around 0.5 m. West and south faces take the wave attack; sea level versus wall toe is not documented.

### Cited Findings
- Malvan tide predictions: mean range about 1.6 m, spring up to about 2.6 m, neap about 0.7 m; some sites show a lower datum (low -0.3 m, high 1.66 m) — [TideChecker](https://tidechecker.com/india/maharashtra/malvan/); [Tides.Today](https://tides.today/en/%F0%9F%8C%8D/india/maharashtra/malvan); [TidesChart](https://www.tideschart.com/India/Maharashtra/Sindhudurg/Malvan/); [TidesNear.me](https://tidesnear.me/tide_stations/9896). Model output, not Survey of India; reference station for one site is Ratnagiri, about 105 km away ([DevDarsha](https://devdarsha.com/tide-today/malvan)).
- INCOIS high-wave warning for the Sindhudurg coast (Vijaydurg Harbour to Terekhol): waves of 3.2-3.5 m forecast 20:30 on 3 July to 23:30 on 5 July 2026 — [IMD RSMC New Delhi fishermen bulletin](https://rsmcnewdelhi.imd.gov.in/uploads/archive/45/45_3491c1_fisherman.pdf)
- Fair-weather snapshot for Malvan: waves 0.44-0.54 m, period 6.2-7.3 s, sea temperature about 30 C (one day, model) — [DevDarsha](https://devdarsha.com/tide-today/malvan)
- INCOIS defines significant wave height as the mean of the highest third of waves, approximating visually observed height — [INCOIS OSF](https://incois.gov.in/site/services/osf.jsp)
- July 2026: monsoon waves caused a roughly 3 m wide breach at the base of the east-facing No. 2 bastion wall; the west and south walls (facing waves) already have cracks and small breaches, and ASI is criticised for inaction — [Pudhari (Marathi news, 18 July 2026)](https://pudhari.news/maharashtra/kokan/sindhudurg/sindhudurg-fort-wall-damage-archeology-department-neglect-ss88)
- July 2002: a wall section 10 m long by 8 m high collapsed and was repaired — [MalvanCity](https://www.malvancity.com/sindhudurg-fort/)
- 1828: monsoon waves washed away parapets and undermined the west and south faces — [Bombay Gazetteer transcription](https://shivshahi.tripod.com/sindgaze.html)
- ASI tender 2024-25 covers repairs to the rampart top surface and water tanks — [Sigma Tenders (ASI tender listing)](https://sigmatenders.com/tender/66g45Eo5PGMS696pckgn7s)
- Landing is on "rocky patches" (2014); a sandy "Ranichi vel" bathing beach lies on the dry south side — [Merwyn's blog](https://merwynsrucksack.blogspot.com/2014/02/sindhudurg-fort.html); [MalvanCity](https://www.malvancity.com/sindhudurg-fort/)

### Inferences
- Set the Blender water plane at mean sea level and extend wall and reef meshes at least 2 m below it, so the 1.6-2.6 m tidal range never exposes a floating base. Water at the base of the walls will vary between roughly 0 and 2.6 m of exposed foundation course (datum caveat).
- Condition modelling: the E/NE faces are intact and sheltered, the W and S faces are rougher, with lost parapet, cracks and rubble at the toe. Include the E-side 3 m breach only if the target date is after July 2026.

### Gaps
- No official tide-gauge or Survey of India tide table for Malvan.
- No measurement of height of wall toe/foundation course above mean sea level or chart datum.
- No wave climatology (annual mean Hs) for Malvan; only one forecast and one model snapshot.

## 6. What is visible from the ramparts (distances and bearings): Malvan shore, Dandi, Padmagad, Rajkot, Sarjekot, Tarkarli, jetty, ferries, Western Ghats

### Takeaway
The mainland shore is about 0.8 km (Dandi point) to 1 km away to the east/north-east, Malvan town about 2 km north, Sarjekot about 4.6 km north, Tarkarli about 6 km south; Padmagad lies on a rocky island between the fort and the coast. The Sahyadri is a faint skyline at under 1 deg elevation if visible at all.

### Cited Findings
- Fort to shore: "about half a mile from the Dandi point of the Malwan shore", but about a mile (1.6 km) of navigation from the harbour through the channel between the two small islands — [Shivaji's Forts](https://shivshahi.tripod.com/sindhu.html). Modern: 1 km off the coast with a 10-15 min ferry — [Maharashtra Tourism](https://maharashtratourism.gov.in/fort/sindhudurg/); half a km — [WebIndia123](https://tourism.webindia123.com/tourism/monuments/forts/Sindhudurg_Fort/index.htm) (conflict with 1 km, probably straight-line vs route); 1-1.5 km — [MeghaBlogs](https://meghablogs.com/en/sindhudurg-fort-malvan/).
- The sole approach channel runs between the small islands of Padmagad and Dhontara; Padmagad lies between Sindhudurg and the coast and had a dry dock — [Indian Military History](https://indianmilitaryhistory.org/forts/sindhudurg.html); [Hindu Janajagruti](https://www.hindujagruti.org/history/40075.html)
- Padmagad is about a quarter mile (0.4 km) from the shore and nearly connects by a sand neck at low ebb — [Shivaji's Forts](https://shivshahi.tripod.com/sindhu.html); conflict: an island fort of one acre "about half a mile from the mainland" (named "Pandavgad", probably the same) — [Gazetteer transcription](https://shivshahi.tripod.com/sindgaze.html). A page gives Padmagad coordinates 16.05 N, 73.47 E (rounded to 0.01 deg) but also says it is 18 km from Sindhudurg, which is self-contradictory — [Kokan Explore](https://kokanexplore.com/padmagad-fort-history/) (low reliability).
- Malvan reference point 16.0621 N, 73.4627 E — [DevDarsha](https://devdarsha.com/tide-today/malvan)
- Rajkot Fort: about 2 km from Malvan bus stand, on rising ground at the north-west corner of the town, sea on three sides; only one bastion with a flagpole remains; a large Shivaji statue is claimed to be 91 ft including a 10 ft base — [Trawell](https://www.trawell.in/maharashtra/malvan-sindhudurg/rajkot-fort) (claim not corroborated); the Gazetteer called it "a mere enclosure of dry stone" in 1828 — [Gazetteer transcription](https://shivshahi.tripod.com/sindgaze.html)
- Sarjekot: 2 km north of Rajkot ([Tarkarli Tourism](https://www.tarkarlitourism.com/forms/forts.aspx); [Indian Military History](https://indianmilitaryhistory.org/forts/sindhudurg.html)), 1.5-1.75 miles north of Rajkot ([Gazetteer](https://shivshahi.tripod.com/sindgaze.html)), about 4-5 km from Malvan bus stand ([Trawell](https://www.trawell.in/maharashtra/malvan-sindhudurg/sarjekot-fort)), at the mouth of Kalavali creek. Coordinates 16.085317 N, 73.462257 E — [Exa place record (Google data)](https://exa.ai/library/place/gjc5hpwntfr). Conflict: Wikipedia gives 18.6344 N, 72.8642 E, which is about 290 km away and clearly a data error — [Wikipedia Sarjekot fort](https://en.wikipedia.org/wiki/Sarjekot_fort).
- Tarkarli is about 6 km from the fort ([Travel Konkan](https://travelkonkan.in/sindhudurg-fort/); [Hidden Routes](https://hiddenroutes.in/forts/sindhudurg-fort)); Tarkarli Beach is visible from one side of the fort and coconut trees form the mainland skyline with colourful boats — [Inditales](https://inditales.com/sindhudurg-fort-konkan-coast/)
- Malvan beach hosts jet-skiing and parasailing near the jetty; snorkelling and scuba trips run from the area — [MeghaBlogs](https://meghablogs.com/en/sindhudurg-fort-malvan/); [Merwyn's blog](https://merwynsrucksack.blogspot.com/2014/02/sindhudurg-fort.html)
- Ferry: small launch with 20 passengers plus two crew and an outrigger "side car", about 20 min (2014) — [Merwyn's blog](https://merwynsrucksack.blogspot.com/2014/02/sindhudurg-fort.html); about 15 min with life jackets (2024) — [Punekar News](https://www.punekarnews.in/exploring-sindhudurg-fort-a-jewel-of-maratha-empire/); boat waits about an hour at the fort — [TrekFORTS](https://www.oocities.org/trekforts/f_sindhudurg.html)
- Sahyadri: eastern boundary of the district, hills over 200 m at the base and about 700 m at the upper reaches — [GSDA Maharashtra](https://gsda.maharashtra.gov.in/en-district-sindhudurg/); Amboli Ghat is at about 690-700 m and is promoted as a hill station where "the sea" can be seen — [Maharashtra Tourism, Amboli](https://maharashtratourism.gov.in/nature/amboli-ghat/); [Maharashtra Tourism, Sindhudurg district](https://maharashtratourism.gov.in/districts/sindhudurg/)

### Inferences
Calculation (flat-earth approximation from the coordinates, error under 1% at these ranges):
- Malvan reference point: 2.0 km at bearing about 4 deg (N). This is the town centre, not the jetty.
- Sarjekot: 4.6 km at bearing about 1 deg (N).
- Padmagad (rounded Kokan Explore coordinates): about 1.15 km at about 53 deg (NE), uncertainty about +/- 0.5 km. Use only as a hint that it lies NE between the fort and the shore, consistent with the other sources.
- Rajkot (no coordinates): by distance bookkeeping, about 2 km north (1.8-2.6 km), north-west edge of Malvan.
- Tarkarli: about 6 km, south of Malvan (direction not sourced), so it lies in the southern sector.
- Geometric horizon from the wall top (eye about 10.6 m, using d = 3.57 sqrt(h) km with standard refraction): about 11.6 km; from a person at ground level (1.65 m): about 4.6 km. The sea horizon is therefore 10-12 km away from the ramparts.
- Sahyadri crest elevation angle: for a 700 m crest at an assumed 50 km (the real distance is unsourced), the apparent elevation after curvature drop is about 0.6 deg. Even at 30 km it is under 2 deg, so the Ghats are a low, haze-washed skyline; do not model them as a large feature. The Amboli "sea view" claim suggests the line of sight exists in clear conditions.
- Bearings of the shore features lie in the eastern/north-eastern sector; the main gate faces the city (NE/E), so the Malvan skyline is framed in that direction.

### Gaps
- No coordinates for Malvan jetty, Dandi beach, Dhontara, Rajkot Fort, Tarkarli, or the Padmagad island (only a rounded, unreliable value).
- Real distance from Malvan coast to the Sahyadri crest and the actual crest silhouette are unsourced.
- Ferry boat length, beam and height are not documented (only capacity 20 plus 2 crew).
- Whether the 91 ft Rajkot statue exists or has been replaced was not verified; check before including it in the skyline.

## 7. Modern additions on and around the fort

### Takeaway
Documented additions are modest: a landing/jetty (conflicting reports), a tourist information centre and ticket counter, small shops, tiled houses, iron railings at the footprint shrine, a broken cannon and Hanuman shrine at the gate, and ongoing ASI repairs. I found nothing on electric poles, water tanks, signboards or flagpole height.

### Cited Findings
- Landing: "There is no jetty near the fort ... alight on the rocky patches" (2014) — [Merwyn's blog](https://merwynsrucksack.blogspot.com/2014/02/sindhudurg-fort.html); "got off the boat at the jetty" then a "twisting, curving and rocky path with high walls" (2024) — [Punekar News](https://www.punekarnews.in/exploring-sindhudurg-fort-a-jewel-of-maratha-empire/). Conflict or change between dates.
- A Tourist Information Centre sits just after the entry arch and a small south-facing Hanuman mandir before it — [Punekar News](https://www.punekarnews.in/exploring-sindhudurg-fort-a-jewel-of-maratha-empire/); a ticket counter sells a fort pamphlet (undated page) — [TrekFORTS](https://www.oocities.org/trekforts/f_sindhudurg.html)
- Broken cannon at the entrance; Hanuman shrine painted bright orange — [Merwyn's blog](https://merwynsrucksack.blogspot.com/2014/02/sindhudurg-fort.html)
- Shivaji's hand- and footprint structure is a small enclosure viewed through iron rods; small shops sell cold drinks, sharbats and snacks; stairs have no safety features (2013) — [Inditales](https://inditales.com/sindhudurg-fort-konkan-coast/)
- The footprints are on the parapet close to the entrance under two small domes — [Hindu Janajagruti](https://www.hindujagruti.org/history/40075.html)
- Residents live in tiled houses; 18 families — [Tarkarli Tourism](https://www.tarkarlitourism.com/forms/forts.aspx); household-count conflict: 10 houses / about 20 people ([MalvanCity](https://www.malvancity.com/sindhudurg-fort/)), 18 houses ([MeghaBlogs](https://meghablogs.com/en/sindhudurg-fort-malvan/)), about 20 families ([Hindu Janajagruti](https://www.hindujagruti.org/history/40075.html)).
- Temples named: Shivrajeshwar, Mahadev, Bhavani, Jarimari, Hanuman, Mahapurush — [MeghaBlogs](https://meghablogs.com/en/sindhudurg-fort-malvan/); [Travel Konkan](https://travelkonkan.in/sindhudurg-fort/)
- Restoration: the 2002 collapse repair, the ASI 2024-25 repair tender for the rampart top surface and water tanks, and the July 2026 breach noted in Q5 — [MalvanCity](https://www.malvancity.com/sindhudurg-fort/); [Sigma Tenders](https://sigmatenders.com/tender/66g45Eo5PGMS696pckgn7s); [Pudhari](https://pudhari.news/maharashtra/kokan/sindhudurg/sindhudurg-fort-wall-damage-archeology-department-neglect-ss88)
- Three sweet-water wells (Dudh, Dahi, Sakhar bav) and two rain-water tanks — [Shivaji's Forts](https://shivshahi.tripod.com/sindhu.html)

### Inferences
- The "water tanks" in the ASI tender are probably the historic rain-water tanks, not modern overhead tanks (inference).
- Residents (10-18 households) plus shops imply at least basic electricity and water lines and some wiring or poles, but no source confirms it. Treat poles and signs as optional detail, kept off the main photographic sight lines unless photo references show them.
- For a "historical" model, omit the ticket booth, stalls, railings and signboards; for a "present-day" model, place them at the gate area and temple.

### Gaps
- No data on electric poles, overhead wires, modern water tanks, solar panels, signboards, handrails (other than the footprint grille), toilets, or a flagpole (height, location, or existence) on Sindhudurg.
- Rajkot's flagpole bastion is documented ([Trawell](https://www.trawell.in/maharashtra/malvan-sindhudurg/rajkot-fort)) but is not Sindhudurg.
- Jetty dimensions and layout at the fort and at Malvan are not documented.

## 8. Common geometric mistakes in fort reconstructions and how to avoid them

### Takeaway
No documentation was searched for this question; the list below is practitioner knowledge, flagged as such, tailored to this site's numbers. The most important checks are watertight solid walls, openings cut fully through, burying bases, and verifying scale with a 1.65 m mannequin.

### Cited Findings
- None. No source was retrieved for this question; all items below are practitioner knowledge, not citations.

### Inferences
Practitioner rules (not tested in this session; verify in Blender):
- Doors into solid walls: boolean-cut every opening through the full thickness (3.0-3.7 m), then add lintel or arch and a threshold; confirm with a test mannequin walking in and out. Check that every door opens onto walkable floor on both sides and the staircase runs along the inner face (see the Q2 arithmetic).
- Buildings on paths: keep house footprints at least 1.0-1.5 m clear of path edges except at doorways; check paths for obstruction by placing a 0.6 m wide capsule along them.
- Z-fighting: avoid coplanar faces between wall, floor and plaster; offset by at least 1-2 cm or merge them. Use camera clip start 0.1-0.5 m and end about 10-20 km. Keep the world origin near the fort centre. A 32-bit float resolves about 0.06 mm at 1 km and about 1 mm at 10 km (calculation), so distant props at the 5-10 km scale (Ghats, far shore) should be low-detail or a backdrop.
- Light leaking: model walls as closed, solid manifold volumes at least about 0.3 m thick (parapets and merlons included), not single planes. Overlap neighbouring solids by 5-10 cm rather than butting coplanar edges, and bury wall bases in terrain or reef. Cycles is path-traced and does not leak through closed solids. In EEVEE, raise shadow resolution or lower bias if thin elements glow.
- Floating objects: snap by ray cast or shrinkwrap to the terrain; sink building plinths 0.3-0.5 m; set palm trunk bases 0.2-0.3 m below ground with a root flare; wall bases 2 m below the water plane (see Q5).
- Scale: put a 1.65 m mannequin at the gate, stair foot, wall-walk, and temple door; compare with photographs. Re-check the sun direction with the 21 Dec noon shadow test (Q4).
- Contact rules: every object must touch a supporting surface within 5 cm; parapets sit on the wall top; stairs land on both ground and wall-walk; trees do not intersect wall faces.

### Gaps
- No documented standards (e.g., Blender manual bias or shadow settings) were retrieved; confirm settings in the Blender manual for the version used.
