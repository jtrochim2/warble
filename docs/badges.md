# Achievement badge artwork

Each achievement has its own original illustrated trophy. The family uses rough iron, bone, oxblood cloth or enamel, aged brass, and weathered handcrafted surfaces inspired by the requested Warcry / Games Workshop atmosphere. No official logo or faction insignia is reproduced.

## Delivery and display

- Generation: built-in imagegen tool, one transparent image per achievement.
- Runtime files: `static/images/badges/<achievement_key>.webp`, each 512 × 512 with preserved alpha transparency; optimized for web delivery.
- Shared use: the achievement catalog and player badge collection use `core/achievements.py` and `templates/core/partials/achievement_card.html`.
- Earned badges display in color; unearned badges use the same illustration in subdued grayscale, with a separate text status.
- Images are decorative next to translated names and requirements, have empty alt text, and load lazily.

## Shared generation prompt

Use case: stylized-concept. Asset type: a single ORIGINAL premium achievement badge icon for a dark fantasy Warcry tabletop community website. Match the savage handcrafted grimdark Warhammer/Games Workshop atmosphere: battle-scarred iron, rough bone, oxidized brass, oxblood enamel, hand-forged rivets, coarse leather and rope, restrained rust and ash. Tactile hand-painted sculpted bas-relief, high-end miniature trophy rendering, strong readable silhouette at 96-160 pixels, deliberate material detail, crisp sculptural edge highlights and deep charcoal recesses. Front-facing isolated heraldic trophy, square composition, centered, emblem occupies about 78% of the canvas with generous clear padding around every protrusion. Rugged angular frame integrated with the object, not an elaborate frame around an empty illustration. Consistent soft warm light from upper left. Palette charcoal iron, aged brass, desaturated bone, dark red accents; no bright gold shine. Entire background genuinely TRANSPARENT, no floor, no backdrop, no cast shadow outside the badge. No letters, words, numerals, UI, watermark, logos, Games Workshop logos, official faction emblems, modern symbols, cartoon style, blue magic glow, smooth plastic, elven ornament, or circular magical halos. Generate only ONE badge; no sheet or variants. Subject: 

First Muster was generated first. For the other badges, its image was supplied as a material, painting, and lighting reference only, with instructions to create the new subject rather than repeat the horn. Each icon retains a genuinely transparent background and clear cutout silhouette; the full subject stays within the canvas.

## Individual subject prompts

For badges 2–14, append this reference instruction after the individual subject:

The provided image is a MATERIAL, PAINTING, and LIGHTING reference only. Create the NEW subject described above, not another horn. Match its rugged sculpted iron and brass craftsmanship, bone textures, dark red cloth, believable miniature paintwork, clear cutout silhouette, and truly transparent alpha background. Keep the entire icon inside the canvas with padding; no cropping. No text.

### First Muster

File: `static/images/badges/first_muster.webp`

A single battered iron war horn with a flared brass mouth, suspended by coarse rope, laid diagonally across a small dented iron shield. A short ragged oxblood cloth strip ties the horn. Symbolize answering the first call to battle.

### Campaign Regular

File: `static/images/badges/campaign_regular.webp`

A heavy weathered iron-shod warrior boot planted on three rising rough basalt stepping stones, a short red campaign cord tied around its ankle. Strong unmistakable boot and path silhouette, symbolize returning to the battlefield.

### Season Veteran

File: `static/images/badges/season_veteran.webp`

An old torn oxblood war standard on a thick iron spear shaft, a tiny bone skull finial and five distinct bone fang trophies hanging from its crossbar. A battered brass veteran shield plaque sits behind the standard. Symbolize a long campaign.

### First Blood

File: `static/images/badges/first_blood.webp`

A single broad chipped iron dagger pointing downward, with one large polished dark crimson enamel teardrop suspended from its point. Brutal leather-wrapped hilt and a small bronze crossguard. Symbolize the first victory; the droplet is stylized enamel, no gore.

### Proven Fighter

File: `static/images/badges/proven_fighter.webp`

Two broad brutal iron axes crossed over a heavy dented oxblood shield, with five deep tally notches cut into the shield edge. Oxidized brass studs and leather bindings. A compact powerful crossed-axe silhouette.

### Battle Hardened

File: `static/images/badges/battle_hardened.webp`

A scarred closed iron war helm facing forward, very narrow dark eye slit and angular battered cheek guards, framed by chipped broken sword blades. One cracked cheek repaired with rough bronze rivets. Symbolize surviving many battles.

### Crossed Blades

File: `static/images/badges/crossed_blades.webp`

Two clearly readable notched short swords crossed in an X through a heavy open iron torc, with leather-wrapped handles and blunt brass pommels. Strong clean crossed-sword silhouette; no axes, no text.

### Known Rival

File: `static/images/badges/known_rival.webp`

Two opposing side-profile iron war helmets facing one another, one with a copper crest and one with a bone brow, joined below by a short taut iron chain. A dramatic mirrored rivals silhouette inside a rugged metal crest.

### Across the Warlands

File: `static/images/badges/across_the_warlands.webp`

A rough rolled hide map with torn edges behind a chunky toothed iron compass, with a long bone compass needle and three small oxblood route studs, no writing and no identifiable real map. Brutal explorer trophy, no elegant filigree.

### Many Faces

File: `static/images/badges/many_faces.webp`

Three distinct overlapping tribal war masks in a fan: one carved weathered bone, one dark riveted iron, and one oxidized bronze with a torn crimson cloth tie. Distinct brow and jaw shapes; empty dark eye holes, not human faces.

### Rise Again

File: `static/images/badges/rise_again.webp`

A powerful armored iron fist thrust upward through a broken iron chain, snapped chain links curling below, with three tiny warm orange ember accents. Battered knuckle plates with bronze rivets, a bold raised-fist silhouette.

### Unbroken

File: `static/images/badges/unbroken.webp`

A broad unbroken riveted iron tower shield with a reinforced bronze spine, holding firm as a shattered axe head and broken blade fragments fall away at its edges. Clearly intact shield, strong angular defensive silhouette.

### On the Podium

File: `static/images/badges/on_the_podium.webp`

A heavy bronze skull medallion hanging from a short chain above a three-level rough black stone podium, center level highest, two lower side levels. Readable stepped-podium silhouette, no numerals or lettering.

### Champion

File: `static/images/badges/champion.webp`

A brutal jagged iron crown with broad triangular spikes set above a central weathered bone skull, a dark crimson cabochon in its brow, heavy aged brass lower rim and small broken iron laurels. The most prestigious badge, powerful crown silhouette, no elegant royal filigree.

### Loyality

File: `static/images/badges/loyality.webp`

A single torn oxblood war banner on a jagged iron pole, bound by three interlocking
iron oath rings, with a weathered bone skull at its foot. Original sculpted miniature
style: rough charcoal iron, aged brass, bone and dark red cloth, warm upper-left
light, isolated transparent background, no text or official faction insignia.
Generated individually and optimized to 512 × 512 WebP with alpha transparency.
