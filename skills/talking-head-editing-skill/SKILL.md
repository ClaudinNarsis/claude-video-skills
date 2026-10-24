---
name: talking-head-editing-skill
description: End-to-end editor for talking-head footage. Analyses the video first (format, length, speech, pauses, audio, framing, screen/cam/mic files), picks the right skills from the installed video stack (edit-video, ffmpeg-skill, motion-broll, sound-effects, object-separation), asks the user only the questions the analysis could not answer, runs the edit, verifies it and delivers the final file with a short report. Use when the user gives a raw talking-head, vlog, interview, course, podcast-video or screen+face recording and wants it edited, cleaned up, cut down, captioned, made into a reel/short, or just "edited" without saying how. Also use for "/talking-head-editing-skill <file>".
---

# talking-head-editing-skill

An orchestrator. It owns four things: **analyse → clarify → run → deliver**. The actual editing is done by the stack below; never re-implement what they do and never call raw `ffmpeg` for a job one of their scripts covers.

`$FF` = `~/.claude/skills/ffmpeg-skill`, `$EV` = `~/.claude/skills/edit-video`, `$MB` = `~/.claude/skills/motion-broll`, `$SFX` = `~/.claude/skills/sound-effects`, `$OS` = `~/.claude/skills/object-separation`, `$TH` = `~/.claude/skills/talking-head-editing-skill`.

**Read `$TH/PREFERENCES.md` first.** It holds this user's house style (loud multi-font key-phrase captions, follow-button tap, person cut-out + blur, zoom-whip transitions on hard joins, SFX without music, -15 LUFS / -4.4 dBTP, approval order) and the reusable scripts in `$TH/scripts/` and templates in `$TH/assets/`. Treat its defaults as answered: skip those questions in step 3 and put them in the plan. **Taste profiles live in `$TH/tastes/`.** If the user says "in the Grow with Sri style/taste" (optionally with dial overrides like "transitions 3"), read `$TH/tastes/grow-with-sri.md` and apply its dials on top of PREFERENCES.md. Run every ffmpeg-based script with `export PATH=/opt/homebrew/opt/ffmpeg-full/bin:$PATH` (the Homebrew ffmpeg has no libass/drawtext).

## The stack and when each is the right tool

| Skill | Use it for | Do not use it for |
|---|---|---|
| **edit-video** | Raw talking-head (or screen + cam + separate mic) → polished **vertical 9:16** reel: pause/duplicate cuts, -14 LUFS, animated captions, zoom on cuts, title, callouts, cards flying behind the speaker, stock cutaways, music. Own whisper transcription. | Horizontal/long-form output, pure audio fixes, quick trims. Heavy first-run install (~1 GB). |
| **ffmpeg-skill** | Everything deterministic: probe, silence/filler cuts, trim, join, reframe, captions (SRT/ASS/karaoke), overlays, lower-thirds, audio clean-up/ducking/loudness, HDR→SDR, platform export, `check.py`, `look.py`. | Taste calls (what is a good cut). Anything it has no script for. |
| **motion-broll** | Motion-graphic cutaways timed to the speaker's words (one-shape style) for explainers, numbers, comparisons. Works on any aspect ratio. Outputs clips + composited preview. | Plain cleanup. Videos with no transcript and no way to get one. |
| **sound-effects** | A measured SFX/music pass on a video that already has motion graphics (motion-broll output, Remotion). | Plain talking head with no graphics: nothing to land cues on. |
| **object-separation** | Cut-out / isolate the person or an object (SAM 2). Only on explicit request. | Anything else; slow and heavy. |
| explainer-default / -engaging / -high-energy | Product-demo videos from code, not footage. **Not part of this workflow**; mention only if the user asks for a product video instead. |

## 1. Analyse (before any question)

Work in the folder holding the footage. Write notes to `work/<name>/analysis.md` as you go.

1. **Inventory.** List the input (file, or folder). Detect the three-file set (`Head`/`cam`, `Screen`, `Sound`/`mic`/`audio`); if present the job is a **split recording** (edit-video format 2).
2. **Probe.** `python3 $FF/scripts/probe.py <file> --json`: duration, resolution, orientation, fps, `variable_frame_rate_suspected`, HDR flag, audio channels/codec. Never ask the user for anything this reports.
3. **Look.** `python3 $FF/scripts/look.py <file> --tiles 4x3`, view the PNG. Note: framing (face position, headroom), background, anything in front of the speaker (mic, cup), screen content if split, burnt-in text/logos, lighting problems.
4. **Speech and pauses.** `python3 $FF/scripts/silence.py <file> --dry-run --json` for pause count and total silent seconds. Estimate filler density only if a transcript exists. Words-per-minute from the transcript tells the pace.
5. **Audio.** `python3 $FF/scripts/loudness.py <file> --dry-run --json` (integrated LUFS, true peak). Note hiss/room noise by ear-free means only: report measured values, never "sounds good".
6. **Transcript (only if a route needs it).** Reel route: `node $EV/scripts/vid.mjs prep <file> [uk|ru|en|auto]` (run `node $EV/scripts/setup.mjs` once first, in background). Otherwise `caption.py --transcribe` / words from `silence.py --filler`. Detect the language from the transcript; do not ask.
7. **Classify** into one profile:
   - **Short-form candidate**: ≤ 3 min of speech, or the user mentions Reels/TikTok/Shorts.
   - **Long-form**: > 3 min, YouTube/course/podcast-video; keep horizontal.
   - **Split recording**: screen + cam + mic files.
   - **Fix-only**: user asked for one narrow thing (trim, loudness, captions).

Report the findings in at most 8 lines (numbers, not adjectives) before moving on.

## 2. Pick the route

| Profile / ask | Route |
|---|---|
| Short-form candidate, "make it a reel/short" | **R1**: edit-video full pipeline (prep → edit.json → preview → render) |
| Split recording | **R1** with `layout: "split"` |
| Long-form, "clean it up" | **R2**: ffmpeg-skill chain: `silence.py --speech-aware [--filler]` → `audio.py --voice` → `caption.py` (if wanted) → `loudness.py` → `render.py --template youtube` or `export.py` → `check.py` |
| Fix-only | **R3**: the single ffmpeg-skill script from its Request→script table |
| Wants motion graphics / animated cutaways / "make it more visual" | add **motion-broll** on top of R1 or R2 (clips composited over the cleaned cut) |
| Motion graphics were added and wants sound design | add **sound-effects** after motion-broll |
| Wants subject cut-out / background removal | **object-separation**, standalone |

Routes combine in a fixed order: cleanup (cuts, audio) → captions → motion-broll → sound-effects → loudness/export → check. Cut first, so every later stage is timed to the final timeline.

Edit-video produces its own captions, music and whoosh; do not stack ffmpeg `caption.py` or `audio.py --music` on top of an R1 render.

## 3. Clarify (one round, only what is still open)

Use AskUserQuestion, **one call, max 4 questions**, each with a recommended default marked `(Recommended)` and chosen from the analysis. Skip any question already answered by the user's message or by the analysis. Typical candidates:

1. **Destination / format**: Reels-TikTok-Shorts 9:16, YouTube 16:9, keep source. (Skip if stated.)
2. **Target length or aggressiveness**: keep everything / remove pauses and fillers / tight cut to N seconds. State what the analysis measured ("38 pauses, 71 s of silence of 6:12").
3. **Look add-ons**: captions (style), motion-graphic cutaways, stock b-roll, background music, title/callouts. multiSelect.
4. **Assets**: brand colours/font/logo, music file, cover images/screenshots for card b-roll, `avoid` object in frame. (Ask only if an add-on needs them; otherwise use defaults.)

Never ask for: resolution, fps, duration, language, loudness targets, face position (all measured or looked at). Never ask one question per turn.

If the user is unreachable (non-interactive), proceed on the Recommended defaults and say so in the report.

## 4. Plan and approve

Show one compact plan before the long run:

```
Input:  <file>  <dur>  <res>  <lufs>
Route:  R1 edit-video  (+ motion-broll)
Steps:  cuts N (−X s) · captions clean · title "…" · 3 callouts · music · -14 LUFS
Output: out/<name>_final.mp4  1080×1920
Time:   ~N min (mask/render heavy)
```

edit-video already requires an "ok" on its cut table (its step 2); ask once, not twice. For R2/R3 a plan line plus `--dry-run --json` from the first writing step is enough; proceed unless the plan deletes content (large trims on a talk) — then wait for "ok".

## 5. Run

Load the chosen skills through the Skill tool and follow their instructions exactly; this file only sequences them.

- **R1**: invoke `edit-video`. Pass the answers from step 3 into its edit.json (title, callouts, music, captions, `avoid`, `layout`). Run its long jobs (`prep`, `preview`, `render`) in the background and wait for completion.
- **R2/R3**: invoke `ffmpeg-skill`. Three or more steps → one `render.py` with a `project.json`. Never overwrite the source; outputs go to `out/`.
- **motion-broll**: invoke it after the cleaned cut exists; it has its own interview and approval table, so seed its answers from step 3 rather than re-asking.
- **sound-effects**: invoke it on the motion-broll export. Credit/licence output (`CREDITS.txt`, `SOUND.md`) is delivered with the video.
- A failed step is reported with its error message and stops that branch; do not retry the same command blindly or switch to raw ffmpeg.

## 6. Verify and deliver

1. `python3 $FF/scripts/check.py <final> --platform <reels|tiktok|shorts|youtube|…>`; fix FAIL rows that are format-only, report WARNs.
2. `python3 $FF/scripts/look.py <final> --tiles 3x2`, view it. Check against the plan: captions inside safe area, no text on the face, nothing covering the `avoid` object, titles readable.
3. Confirm numbers from `probe.py`: duration, resolution, fps, audio, LUFS/true peak.
4. Final message, in this shape and nothing longer:

```
Done: <abs path to final file>
<dur> · <res> · <fps> fps · <LUFS> LUFS / <TP> dBTP
What changed: <cuts: N removed, −X s> · <captions> · <graphics> · <music/SFX>
Checked: check.py <PASS/WARN list> · contact sheet <abs path to PNG>
Not verified: audio by ear (measured only) — please listen once.
Credits/licences: <path or "none needed">
```

Also leave next to the output: `work/<name>/analysis.md` (what was measured) and the plan used, so the edit can be reproduced or tweaked ("make the cuts less aggressive" = re-run from the saved plan, not from scratch).

## Rules

- Analysis before questions, questions before work, plan before long renders.
- Numbers from tools, not impressions. Say "not inspected" when you could not view something; never claim to have heard the audio.
- Originals are never modified. Stock/music downloads follow edit-video's licence rules (Mixkit Free License only, no Cloudflare bypass, never commit media).
- Don't add stages the user didn't want just because the stack has them. Default to the smallest route that satisfies the request.
- Heavy installs (edit-video setup ~1 GB, motion-broll Playwright) happen only when that route is chosen, and the user is told once what and how big.
