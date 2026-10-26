# Warble art direction

An original Warcry-inspired ruined fortress: rough basalt, rusted iron, jagged towers, torn crimson banners, smoke, and orange firelight. The illustration replaces the earlier woodland scene with a harsh warband battleground. System sans-serif typography and the text-only wordmark are retained.

## Reference direction

The ruined battleground and forge atmosphere draws on the official [Warcry: Catacombs overview](https://www.warhammer-community.com/en-gb/articles/pYPZxc5w/warcry-catacombs-whats-in-the-box/). This is an original environment illustration, rather than a reproduction of an existing Warhammer image.

## Artwork

- Runtime asset: `static/images/ashfall-citadel.webp` (355 KiB).
- Generated using the built-in imagegen tool and converted to WebP for local delivery.
- The previous `static/images/whispering-wilds.webp` is retained as an unused earlier direction.
- No external image or font service is required.

## Motion

The background illustration is stationary. Drifting smoke, windblown embers, and the two foreground braziers provide ambient motion. `static/js/torches.js` samples warm flame pixels from the original artwork and renders small canvas overlays with independent flicker, upward flutter, and local glow. Overlay positions follow the background cover scale and CSS crop at every viewport size; the illustration and brazier structures remain stationary. The fire loop stops while the tab is hidden and runs at up to 24 frames per second. The footer control pauses ambient animations and remembers the preference when storage is available. OS reduced-motion settings disable animation. Without JavaScript, the scene is static. The join flow and native dialog behavior are unchanged.

## Generation prompt

Use case: stylized-concept.
Asset type: original cinematic background illustration for Warble, a Warcry community website.
Primary request: a savage dark-fantasy war-torn environment closely aligned with the aesthetic of Warhammer Age of Sigmar Warcry, specifically the brutal ruined battlegrounds of the Eightpoints and Bloodwind Spoil. This must feel like a warband skirmish setting, not an elegant elven kingdom.
Scene: a shattered fortress city on a desolate rocky escarpment. In the CENTER-RIGHT a massive broken fortified gatehouse of rough dark basalt, jagged ruined towers, crude riveted iron reinforcements, spike barricades, heavy hanging chains, weathered skull reliefs embedded in the architecture, torn deep crimson pennants whipping in the wind. Broken stairs and rubble lead to a scorched courtyard; iron braziers burn with fierce orange flame. Beyond, distant impossible jagged black spires and scattered battle fires disappear into dusty storm haze. Foreground: cracked earth, rusty discarded metal, masonry, ash and a few scattered bones, no gore.
Composition: wide landscape 16:9. Art must occupy the full canvas with beautiful layered depth. Keep LEFT THIRD low contrast and dark, with smoky barren rocky ground and shadowy distant ruins, to allow light website copy to overlay. Center-right fortress silhouette is the visual focal point and reads clearly even in a narrow mobile crop.
Style: premium grimdark fantasy painted environment key art, rich tactile brushwork, raw hand-forged materials, weathered and grounded. Strong cinematic composition, highly detailed but legible. NOT a photograph of tabletop miniatures, NOT a videogame screenshot.
Palette: soot charcoal, desaturated slate and cold iron, dusty bone, oxidized rust, blood-red banners, orange embers and restrained hellish firelight. Threatening heavy storm clouds, sulfurous red-orange light breaking through smoke on the horizon.
Avoid: lush foliage, forests, waterfalls, glowing magical portals, graceful white towers, elven filigree, elegant circular arches, cozy golden sunlight, fairytale atmosphere, excessive lava, people, characters, text, logos, branding, UI, watermarks. No Warhammer logo or exact reproduction of existing artwork.
