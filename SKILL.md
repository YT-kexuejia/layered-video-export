---
name: talking-head-studio
description: Package a narration or talking-head video with timed explanatory visuals, original 3D scenes, a reusable style template, browser preview, SRT subtitles and segmented accelerated export. Use when a user supplies a video and wants an agent to complete post-production using this repository.
---

# Talking Head Studio

Run this repository with the user's existing agent. No additional model API key is needed: **you author the semantic scene plan**, while local tools transcribe and render. Do not claim that a generic keyword script understood the narration.

Read [MODULES.md](MODULES.md) for the collaboration contracts, [WORKFLOW.md](WORKFLOW.md) for commands and [TEMPLATES.md](TEMPLATES.md) for the template interface. Install `npm install` and `python -m pip install -r requirements.txt` using Python 3.13+, and locate Node, Chrome, FFmpeg and ffprobe. Never upload a user's footage, transcript, generated project or export cache into the template repository.

## Modular orchestration

Operate as an orchestrator. Complete these modules in order and persist each handoff artifact before starting the dependent module. A module may be performed by the same Agent, a specialist sub-agent when available, or deterministic local code; the artifact contract stays the same.

1. **Intake module** — validate the source, tools, duration and frame geometry; output project configuration and an environment report.
2. **Speech module** — transcribe locally with word timestamps, correct product names and produce punctuation-free, readable subtitle units.
3. **Editorial module** — understand the whole narration and write `plan.json` with semantic beats, exact reveal times, chapters and evidence notes. Visuals must never lead the spoken phrase.
4. **Art-direction module** — choose a limited palette, type scale, scene grammar and varied explanatory structures while preserving the selected template identity.
5. **Visual-code module** — turn the approved plan into deterministic time-driven layout, SVG/Canvas/UI animation and reusable components.
6. **3D module** — add Three.js scenes only where spatial form improves the explanation; define camera, lights, materials, entry/exit timing and a lightweight fallback.
7. **Audio/subtitle module** — preserve source speech, align captions, remove sentence punctuation, split long lines and generate SRT.
8. **Render module** — build browser preview, then use the existing layered, segmented 1080p24 export without changing the template's visual contract.
9. **Review module** — independently verify narration/visual alignment, typography, portrait crop, transitions, full-canvas coverage, encoded frames and cache cleanup. It can reject a handoff and return it to the responsible module.

The machine-readable registry is [workflow.modules.json](workflow.modules.json). Do not let modules share hidden state: use project configuration, transcript, `plan.json`, template files, captions, render manifest and QA report as the handoff boundary. Changing module organization must not change the accepted visual baseline; compare the same timestamps before and after workflow changes.

1. Initialize an isolated project from the video with `pipeline.py init`. Preserve narration and video duration; cutting speech is a separate task.
2. Run local word-timestamp transcription with `pipeline.py transcribe`. Inspect difficult product names and representative passages; correct captions against actual audio when needed. Model download is local inference, not an upload of the video.
3. Read the full timed transcript. Author `plan.json` following [PLAN.md](PLAN.md). Place scene changes and each information reveal at the corresponding spoken phrase, never earlier. Use actual evidence for charts and technical claims; label conceptual diagrams as illustrations. Use licensed assets with provenance.
4. Use the bundled Studio Blue style or a downloaded compatible template. Alternate explanatory structures according to meaning: comparisons, a node graph, a metal object, a spatial demonstration, an editorial panel or an actual UI. Avoid repeating a three-card diagram throughout the video. Preserve legible typography, fixed caption/footer geometry and smooth sphere reveals.
5. Build, start local preview, and inspect the intro, each chapter boundary, representative 3D scenes and late-video scenes. Test forward/backward seeking, source audio, mobile controls and paused frames. All animation must be a function of film time, not wall-clock timers or scroll position. Check source/template fit; a portrait position may need adjustment for the new speaker.
6. Run two visual-QA passes before delivery. First inspect a stable frame from every scene. Then inspect frames immediately before, during and after every scene or layout transition. The background must cover the full 1920×1080 canvas continuously. Reject and fix any vertical or horizontal black band, uncovered canvas, alpha seam, one-pixel edge, background discontinuity, stale previous-scene layer or hard module boundary. Compare suspicious frames at `t-0.1s`, `t` and `t+0.1s`; do not approve a preview from a single clean frame. Recheck the same timestamps in a short encoded export because browser preview and compositing can differ.
7. Deliver a preview and SRT. If the user authorized rendering, export at 1080p24 using the existing split layers. Otherwise leave the webpage export button ready. Record measured overall frames/sec; do not extrapolate a GPU-only phase as final throughput.

The export invariant is 7200-frame (five-minute) segments: commit only validated segments, then delete only their temporary images/layers. Keep incomplete work for continuation. Source and completed segments must survive pauses. Rebuilding the scene plan changes the fingerprint; start a new export instead of combining incompatible caches.

Publication and third-party asset licenses are separate from rendering. MIT applies to our own code and template; dependencies keep their own licenses. Do not introduce unreviewed third-party visual code or paid animation assets into the bundled template.
