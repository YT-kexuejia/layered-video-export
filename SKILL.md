---
name: talking-head-studio
description: Package a narration or talking-head video with timed explanatory visuals, original 3D scenes, a reusable style template, browser preview, SRT subtitles and segmented accelerated export. Use when a user supplies a video and wants an agent to complete post-production using this repository.
---

# Talking Head Studio

Run this repository with the user's existing agent. No additional model API key is needed: **you author the semantic scene plan**, while local tools transcribe and render. Do not claim that a generic keyword script understood the narration.

Read [WORKFLOW.md](WORKFLOW.md) for commands and [TEMPLATES.md](TEMPLATES.md) for the template interface. Install `npm install` and `python -m pip install -r requirements.txt` using Python 3.13+, and locate Node, Chrome, FFmpeg and ffprobe. Never upload a user's footage, transcript, generated project or export cache into the template repository.

1. Initialize an isolated project from the video with `pipeline.py init`. Preserve narration and video duration; cutting speech is a separate task.
2. Run local word-timestamp transcription with `pipeline.py transcribe`. Inspect difficult product names and representative passages; correct captions against actual audio when needed. Model download is local inference, not an upload of the video.
3. Read the full timed transcript. Author `plan.json` following [PLAN.md](PLAN.md). Place scene changes and each information reveal at the corresponding spoken phrase, never earlier. Use actual evidence for charts and technical claims; label conceptual diagrams as illustrations. Use licensed assets with provenance.
4. Use the bundled Studio Blue style or a downloaded compatible template. Alternate explanatory structures according to meaning: comparisons, a node graph, a metal object, a spatial demonstration, an editorial panel or an actual UI. Avoid repeating a three-card diagram throughout the video. Preserve legible typography, fixed caption/footer geometry and smooth sphere reveals.
5. Build, start local preview, and inspect the intro, each chapter boundary, representative 3D scenes and late-video scenes. Test forward/backward seeking, source audio, mobile controls and paused frames. All animation must be a function of film time, not wall-clock timers or scroll position. Check source/template fit; a portrait position may need adjustment for the new speaker.
6. Deliver a preview and SRT. If the user authorized rendering, export at 1080p24 using the existing split layers. Otherwise leave the webpage export button ready. Record measured overall frames/sec; do not extrapolate a GPU-only phase as final throughput.

The export invariant is 7200-frame (five-minute) segments: commit only validated segments, then delete only their temporary images/layers. Keep incomplete work for continuation. Source and completed segments must survive pauses. Rebuilding the scene plan changes the fingerprint; start a new export instead of combining incompatible caches.

Publication and third-party asset licenses are separate from rendering. MIT applies to our own code and template; dependencies keep their own licenses. Do not introduce React Bits, proprietary Motion+ examples, paid animation packs, or GSAP into the bundled template without an explicit license review.
