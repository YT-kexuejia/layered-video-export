# Talking Head Studio / Layered Video Export

[简体中文](README.md) · **English** · [Español](README.es.md)

Give an existing Agent a talking-head video and let it handle local transcription, semantic scene planning, explanatory visuals, 3D motion, subtitles, browser preview, and accelerated layered export. The repository includes the **Studio Blue** template and supports installable compatible templates.

![Browser preview and export dashboard](docs/images/web-interface.jpg)

![Studio Blue template](docs/images/studio-blue-template.png)

The presenter in the preview is fictional. No user portrait, test footage, transcript, or previous export is included.

## How it works

Your Agent understands the narration, decides what each visual should communicate, and reviews the result. Deterministic local tools transcribe, build, preview, and render it. The repository does not require a separate AI API key and does not start a hidden AI service.

The workflow has nine artifact-driven modules: intake, speech, editorial planning, art direction, visual code, 3D, audio/subtitles, layered rendering, and independent review. See the [module specification](docs/zh/MODULES.md) and the machine-readable [module registry](config/workflow.modules.json). This organization preserves the approved template, timing, subtitle rules, and 1080p24 output baseline.

## Use the Skill with an Agent

```sh
git clone https://github.com/YT-kexuejia/layered-video-export.git
cd layered-video-export
npm install
python -m pip install -r requirements.txt
```

Give the repository folder and your video to an Agent that can read files, run commands, and inspect a local webpage. Send this prompt:

> Read SKILL.md and package this talking-head video with the bundled template. First deliver the browser preview and SRT. Verify narration-to-visual timing, presenter crop, transitions, and full-frame coverage, then export the approved result at 1080p24.

The Agent follows [SKILL.md](SKILL.md). Core commands are:

```sh
python pipeline.py init "D:\path\talking-head.mp4" --project "D:\path\my-video"
python pipeline.py transcribe --project "D:\path\my-video" --device cpu
# The Agent reads the transcript and authors plan.json.
python pipeline.py build --project "D:\path\my-video"
set LVE_CONFIG=D:\path\my-video\config.json
python serve.py
```

Open the local URL printed by `serve.py` to preview, seek, jump between chapters, download SRT, and start, resume, or pause an export. The [workflow guide](docs/zh/WORKFLOW.md) and [scene-plan specification](docs/zh/PLAN.md) contain the complete technical contract.

## Templates

The bundled template is in [`templates/studio-blue`](templates/studio-blue). It provides continuous blue light fields, editorial typography, a presenter rail, chapter palettes, metallic spheres, and purpose-built 3D diagrams. Information appears at the corresponding spoken phrase. Captions remove sentence punctuation, use spaces between clauses, and split long lines.

Install a compatible template from another folder with:

```sh
python pipeline.py build --project "D:\path\my-video" --template "D:\path\downloaded-template"
```

See the [template protocol](docs/zh/TEMPLATES.md). Bundled motion uses MIT-licensed Anime.js and Three.js; the light field and Studio Blue visual system are implemented by this project. Fonts, user media, and third-party images are not distributed.

## Accelerated layered export

The renderer continuously encodes backgrounds and 3D, captures UI only where it changes, generates a compact waveform layer with ManimGX, decodes the presenter with FFmpeg, and encodes validated segments with NVIDIA NVENC. Every 7,200 frames (five minutes), it validates and commits one segment before deleting that segment's temporary frames. Interrupted work remains resumable.

## Repository layout

```text
src/python/             Python internals
src/js/                 JavaScript render modules
templates/studio-blue/  bundled template
web/                    local export dashboard
examples/basic/         synthetic example and sample configuration
config/                 machine-readable workflow configuration
docs/                   workflow, design, and license documentation
```

## Requirements and license

The validated target is Windows with Python 3.13+, Node 22+, Chrome, FFmpeg/ffprobe, NVIDIA NVENC, and Chrome AVC WebCodecs. Dependency installation and the first transcription-model download require internet access.

Project-owned code and the bundled template are MIT licensed. Dependencies retain their upstream licenses. The repository does not bundle FFmpeg, ManimGX native wheels, fonts, or user media. See [third-party notices](docs/legal/THIRD-PARTY-NOTICES.md) and the [license audit](docs/legal/LICENSE-AUDIT.md).
