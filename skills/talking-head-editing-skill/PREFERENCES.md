# Creator preferences (house style). Read before step 1.

Learned on the first job (IMG_0695, a Jio "free AI courses" reel, 2026-10-23/24). These are the user's defaults. Apply them without re-asking; only ask where the footage differs (see "Still ask").

## Output
- Vertical 9:16 reel, 1080x1920, 30 fps, h264 SDR, for Instagram Reels. Final file in `~/Downloads/out/`, versions named `<clip>_vN_sfx.mp4`; never overwrite an earlier version.
- Final loudness **-15 LUFS, true peak <= -4.4 dBTP** (stereo and mono). `check.py --platform reels` must show 0 FAIL (loudness target -14 +/- 2, so -16 fails).
- Music: **none by default.** Ask only if the user raises it; Mixkit direct URLs return 403, so get a file or a browser download from the user.

## Working style
- Terse reports with numbers, not adjectives. State what was NOT verified (audio by ear, motion in real time).
- Analyse first, then one plan table, then wait for "go". **Transcript gets its own approval step** before any build.
- Transcript: force `--language en` if auto-detect returns another script (Tanglish audio was read as Tamil gibberish). Flag garbled lines; the user corrects wording and dictates the CTA text.
- Ask before system installs (`brew`, big pip). Report side effects honestly (ffmpeg-full upgraded libvpx and broke plain ffmpeg; `brew reinstall ffmpeg` fixed it).
- After finishing, save new pitfalls to memory.

## Captions (burnt in, `scripts/captions_loud.py` + `assets/captions_example.json`)
- **Key phrases only, never every word.** Present the trimmed phrase list with timings and the dropped lines first.
- Loud and bold: 4 fonts (Impact, Montserrat Black from `$EV/fonts`, Avenir Next Condensed Heavy, Marker Felt), thick outlines, shadow, yellow/red/pink/orange emphasis words with a colour flash, 0.25-0.3 s pop-in with overshoot and tilt, slow 7% push, exit shrink. No thin script fonts (Snell, Brush).
- Place in the lower third, y 1215-1520 of 1920 (above the platform UI, clear of any burnt-in top banner and a lower watermark). Keep 3 lines max, widths inside 1080 even at the 126% pop.
- Caption the content inside screen-recording cutaways too when asked (the phone UI is busy; thick outlines keep it legible). Time multi-beat lists to the spoken words, not to cue boundaries.
- A full-frame graphic that repeats a caption's text hides that caption; let the graphic carry it.
- Burn with `caption.py --ass ... --fonts-dir $EV/fonts` and **ffmpeg-full first on PATH** (`/opt/homebrew/opt/ffmpeg-full/bin`); the Homebrew ffmpeg has no libass/drawtext.

## Motion graphics (motion-broll)
- Few and short: ~2 full-frame cutaways on the strongest facts (a price/number, a count). Default palette: canvas #E9E7E2, ink #0B0B0B, accent orange #FF5A1F, Geist. Only real numbers from the transcript; placeholders stay unnamed.
- A tap-the-button animation when the speaker says "follow": orange "Follow" pill over the chest (y ~1350), cursor tap, press-squish, **flips to white "Following" 0.08 s after the tap**, then shrinks away (`assets/motion-clips/03-follow.html`, transparent panel clip -> .mov). Time it from word timestamps and tell the user the timing is +/-0.3 s.
- Examples to copy: `assets/motion-clips/01-price-free.html`, `02-twelve-languages.html`. For portrait clips use a `beats.js` copy that resizes the viewport to the stage (stock one is 1920x1080 only).

## Person cut-out and background blur (object-separation)
- "Crop the person + blur the background a bit": SAM 2 masks, Gaussian sigma 10 on the background, person/hands/held mic sharp, **burnt-in banner kept sharp** (blur only below it). Skip non-person cutaway frames. `scripts/matte_sep.py` + `scripts/matte_blur.py`. Use a box + many points; fill the mic hole.
- Do it FIRST, before captions.

## Transitions (every hard join)
- Detect cuts with ffmpeg scene scores (>0.7 hard, ~0.3 jump cut). Apply `scripts/transitions.py`: 6-frame zoom-whip (up to 10% zoom, 60 px horizontal blur), half strength for a jump cut inside one shot. Do not treat caption exits or scrolling screens as cuts.

## Sound effects (no music)
- `scripts/sfx_mix.py` with the CC0 kit: whoosh on every cut starting 2 frames early (jump cut 6 dB quieter), riser ending on a reveal and on the CTA, impact on the key reveal, pop on each caption pop and on the follow flip, click on the tap. SFX sit ~8 dB under speech.
- sound-effects' `sound_pass.py` requires a music file, so use `sfx_mix.py` when there is no music. Check the 5 Freesound pages say CC0 and write `CREDITS.txt`.

## Pipeline order (house)
1. analyse + transcript approval + plan approval
2. (if asked) person matte + background blur on the ORIGINAL
3. captions burnt on that
4. motion-broll clips + panel clips composited (`composite.py`)
5. `loudness.py` -14/-1 (voice level before SFX)
6. transitions at hard joins
7. `sfx_mix.py`, then `loudness.py -I -15 --tp -4.4`
8. `check.py --platform reels`, stills of every effect, final report (+ memory update)

## Still ask (one AskUserQuestion round)
Goal if the footage is already edited (banner, watermark, cutaways), any music file, the exact CTA wording, the handle text for a follow button, and whether to caption over phone/screen cutaways.

## Known tool gotchas (also in memory `feedback_video_caption_and_broll_gotchas`)
ASS `\t()` times are ms; `caption.py --size/--margin` are 288p units (x6.7); `look.py` labels are offset ~1.4 s (extract frames by `-ss`); zsh does not split `$VAR` in `for`; macOS `sed -i ''`; SAM 2 needs `torchvision`; `cmd &` inside a background Bash fires a bogus completion notice.
