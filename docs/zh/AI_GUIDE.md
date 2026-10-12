# Guide for AI coding assistants

This is a program, not a prompt-only renderer. Any assistant with filesystem and shell tools can use it. Do not claim that it accelerates every arbitrary webpage without an adapter.

1. Read `README.md`, `docs/zh/ADAPTER.md`, and `examples/basic/config.example.json`.
2. Copy the settings into local `config.json`. Keep paths, inputs and credentials out of commits.
3. Run `doctor.py`. Fix missing tools before rendering. Use official package registries for dependencies.
4. Establish a visual baseline for the user's own composition. Include animated titles, changing charts, chapter wipes, masking, 3D and media cropping.
5. Adapt `window.__film.seek(t, true)` and the documented DOM layers. All motion must be deterministic from time. Check sparse UI intervals for every new continuously animated element.
6. Render a short representative segment before the full video. Compare it visually and inspect frames, resolution, audio and timestamps with ffprobe.
7. Measure wall time for the complete pipeline. Small waveform fps and isolated background fps are not end-to-end video throughput.
8. Keep the maximum 7200-frame segment rule. Commit a validated segment and its manifest before deleting its work folder. Never delete source media, unvalidated images or someone else's job.
9. Pause through the local endpoint or the job's `.cancel` marker. Resume the same job only with an unchanged fingerprint.
10. A stopped partial GPU layer is regenerated for its current segment. Existing PNGs and completed layers are reused. Do not describe this as arbitrary per-frame GPU resume.

For the complete talking-head workflow, start with `SKILL.md` and `docs/zh/WORKFLOW.md`. Local transcription, agent-authored scene planning, the bundled Studio Blue template, browser preview and SRT are now included. The reference export adapter remains Windows + NVIDIA, 1920x1080, 24 fps, fixed presenter geometry. Do not promise automatic speech cuts, BGM, universal CSS compatibility or untested platforms.
