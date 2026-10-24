# claude-video-skills

A Claude Code skill stack for editing talking-head video, plus the `talking-head-editing-skill` orchestrator and the "Grow with Sri" taste profile.

```bash
git clone <this repo> && cd claude-video-skills && ./install.sh
```

Then restart Claude Code and run `/talking-head-editing-skill <file>`.

## What's in `skills/`

| Skill | Origin |
|---|---|
| `talking-head-editing-skill` | Original. Analyses footage, routes to the skills below, asks clarifying questions, delivers the final file. Includes `tastes/grow-with-sri.md` and `PREFERENCES.md`. |
| `edit-video` | [hukvadim/edit-video-skill](https://github.com/hukvadim/edit-video-skill), MIT |
| `ffmpeg-skill` | [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill), MIT (installer, tests and evals omitted) |
| `motion-broll`, `sound-effects`, `object-separation`, `explainer-default`, `explainer-engaging`, `explainer-high-energy` | [Barty-Bart/motion-graphics](https://github.com/Barty-Bart/motion-graphics), MIT |

Upstream licences are in `licenses/`. Bundled sound effects are CC0 (see `skills/sound-effects/LICENSES.md`). The upstream authors' copyright applies to their parts; prefer installing from the upstream repos for updates.

## Requirements

`ffmpeg` built with libass/drawtext (e.g. `ffmpeg-full`), Python 3.10+, Node 20+. `edit-video` downloads its own models on first run (~1 GB); `motion-broll` installs Playwright on first run.
