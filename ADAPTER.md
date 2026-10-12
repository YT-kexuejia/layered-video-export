# Composition adapter contract

The exporter does not automatically decompose arbitrary HTML. Its reference adapter has a fixed layout: a 1920×1080 stage and a presenter card at x=1496, y=292, width=342, height=500. The source must be 1920×1080 and contain an audio track. The portrait crop is 738×1080 at x=615, y=0.

## Runtime API

The page must expose:

```js
window.__story = {duration, chapters, scenes};
window.__film = {
  seek(timeSeconds, synchronous) { /* set every visible state from time */ },
  getScene() { /* return the active scene object */ }
};
```

`story.json` includes `duration`, `chapters[{start,theme,accent}]` and `scenes[{id,start,end,kind,chapter}]`. Optional `items`, `rows`, `labels`, `reveal`, `titleAt` and `visualAt` describe UI motion intervals. `captions.json` is a list of `{start,end,text}` cues. `captions.json` may be empty. The shipped JSON files are hand-authored synthetic configuration, not user transcripts or previous test results.

## DOM layers

- `.light canvas`: animated background, drawn at 340,-200 in a 1330×1330 layer. A horizontal 0→20% / 82→100% alpha mask is applied during export.
- `.scene-visual canvas`: Three.js / Canvas models. Bounding rectangles, inherited opacity and inset percentage clips are read by the GPU compositor.
- `.presenter .portrait`: measured intro geometry. Intro contracts from (102,164,1716,766) to (1496,292,342,500) between 6.42 and 7.62 seconds using power3.inOut.
- `#speaker`: source video; hidden in browser captures and composed continuously by FFmpeg.
- `.portraitshade`, `.caption`, `.wave`: generated in the composition step instead of browser screenshots.
- Other DOM content is captured as transparent UI.

The renderer blocks `source.mp4` in capture pages so source video decoding does not slow those pages.

## React compositions

Set `uiEntry` to a local entry point such as `main.jsx`. The exporter builds a UI-only version using esbuild and stubs files named `Scene3D.jsx`, `Objects3D.jsx` and `LightPillar.jsx`. Your `filmFile` must reference `bundle.js` / `bundle.css`, as in the original integration. Declare the React, GSAP or other packages your own page actually imports. They are not required by the minimal standalone example.

For a non-React page, set `uiEntry: null`. `uiFile` is served through `/ui-film.html`; `filmFile` through `/film.html`.

## Important limits

New continuously changing UI needs its own capture interval in `render_layers.mjs`. CSS animations are disabled in the UI-only screenshot pass; convert necessary animation to deterministic seek-controlled state first. Complex backdrop filters, masks and blend modes need explicit reproduction and visual verification. The reference reproduces its chapter wipe with a 12px blur mask and protects the footer. It is not a complete browser compositor.

Output is fixed to 1080p24 and NVIDIA NVENC. A universal layout adapter, selectable codecs and non-Windows cancellation are future work.
