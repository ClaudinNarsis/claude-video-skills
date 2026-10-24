# Taste profile: "Grow with Sri"

Trigger: the user says "in the Grow with Sri style / taste / profile" (optionally with dial overrides, e.g. "Grow with Sri, transitions 3, no blur"). Apply this profile on top of `../PREFERENCES.md` (which holds process, tools and gotchas). A named dial the user overrides wins; everything else stays at the default rating.

Source: the IMG_0695 Jio "free AI courses" reel (2026-10-23/24), an Indian edu/tech short. Feel: loud, fast, high-contrast, every beat has a visual and a sound. (Named after the clip's "Growwithsri" watermark.)

## Dials (rating 1-5; default is 5 = exactly what shipped on IMG_0695)

| Dial | 5 (default, as shipped) | 3 | 1 |
|---|---|---|---|
| **Copy volume** (how much is captioned) | Key phrases only, ~1 caption group per 4-6 s; hook, the money/number, the benefit, the CTA | add one supporting line per beat | hook + CTA only |
| **Copy loudness** | 4 fonts (Impact, Montserrat Black, Avenir Next Condensed Heavy, Marker Felt), 112-270 px, outline 8-12 px + shadow, emphasis words in yellow #FFD400 / red #FF2D55 / pink #FF2D95 / orange #FF5A1F, 2-3 stacked lines | 2 fonts, 90-170 px, outline 6, yellow emphasis only | one font, white, outline 4 |
| **Copy motion** | pop-in 126% overshoot + tilt, key-word colour flash, slow 7% push, exit shrink/fade (`captions_loud.py`) | pop + fade | fade only |
| **Transitions** | zoom-whip on every hard join, 6 frames, 10% zoom, 60 px horizontal blur; jump cuts at half strength (`TRANS_SCALE=1`) | `TRANS_SCALE=0.6`, graphics cuts only | none (hard cuts, whoosh only) |
| **SFX density** | whoosh on every cut (2 frames early), riser into each reveal and the CTA, impact on the key reveal, pop on every caption pop, click on UI taps; no music | whooshes + one impact | whooshes only |
| **Motion graphics** | 2 sparse full-frame cutaways on the strongest facts, default palette (#E9E7E2 / #0B0B0B / #FF5A1F, Geist), plus the follow-button tap when "follow" is spoken | 1 cutaway | none |
| **Subject separation** | person cut out, background Gaussian blur sigma 10, banner sharp, mic sharp | sigma 6 | off |
| **Loudness** | -15 LUFS, TP <= -4.4 dBTP | same | same |

Dials 1-5 map linearly between the columns; use the closest column when unsure and say which values you picked in the plan.

## Copy structure (the "heavy copy" recipe)
1. **Hook**: setup in a small script-ish line, the number or claim in huge Impact ("Don't pay / ₹10,000-15,000").
2. **Benefit**: one giant word + qualifier ("FREE" 270 px / "AI COURSES from Jio").
3. **Detail beats**: one phrase per spoken item, each in a different font and colour, timed to the word (AI AGENTS / PROMPT engineering / AI TOOLS).
4. **Reassurance**: "NO AI" huge + handwritten "experience needed".
5. **CTA**: "COMMENT" + giant yellow keyword + "for the LINK" (keyword text is the user's; ask if unknown).
Layout: lines centred at x 540, y 1215-1520, never over a top banner or the lower watermark.

## How to run it
- Captions: `scripts/captions_loud.py` (copy `assets/captions_example.json`, replace phrases, times and colours).
- Graphics: `assets/motion-clips/*.html` as starting points (price->FREE, count->grid, follow tap).
- Person + blur: `scripts/matte_sep.py`, `scripts/matte_blur.py`.
- Transitions: `TRANS_SCALE=<0-1> python3 scripts/transitions.py in out "t:strength,..."`.
- SFX: `scripts/sfx_mix.py`, then `loudness.py -I -15 --tp -4.4`.
- Order and checks: see PREFERENCES.md "Pipeline order". Always show stills of each effect and list what was not verified.

## Never in this profile
Music unless asked, thin script fonts, every-word captions, invented numbers or handles, captions on the top banner, effects on non-person frames that break the picture (blur only person segments), overwriting earlier versions.
