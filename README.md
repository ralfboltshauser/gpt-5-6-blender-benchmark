<p align="center">
  <img src="site/assets/social/og-card.png" alt="One image, fifteen Blender scenes | GPT-5.6 benchmark" width="1200">
</p>

<h1 align="center">GPT‑5.6 Blender Benchmark</h1>

<p align="center">
  One reference image. One deliberately thin prompt. Fifteen finished Blender scenes.
</p>

<p align="center">
  <a href="https://blender-bench.ralfboltshauser.com/"><strong>Explore the interactive benchmark</strong></a>
  ·
  <a href="site/assets/data/benchmark.csv">Raw data</a>
  ·
  <a href="https://www.linkedin.com/in/ralfboltshauser/">Ralf Boltshauser</a>
</p>

<p align="center">
  <img alt="15 of 15 runs completed" src="https://img.shields.io/badge/runs-15%2F15-171814">
  <img alt="Blender 5.0.1" src="https://img.shields.io/badge/Blender-5.0.1-cf6330">
  <img alt="24.68 million reported tokens" src="https://img.shields.io/badge/reported_tokens-24.68M-4f7f58">
  <img alt="Static site" src="https://img.shields.io/badge/site-zero_build-7564b4">
</p>

---

This repository contains the full source artifacts behind an image-to-Blender capability probe across GPT‑5.6 **Luna**, **Terra**, and **Sol**, plus GPT‑5.5 xhigh as a baseline. Every run received the same image and the same instruction, then worked autonomously through Codex with shell and Blender access.

The interesting result is not simply that the largest configuration won. **More thinking raised the ceiling, but quality was not monotonic.** Some medium and high runs broke their central roof geometry; one light run placed sixth overall; Sol xhigh came within two visual points of Sol Ultra at less than one-third of the token spend.

## Headline results

| Choice | Run | Visual score | Time | Reported tokens |
|---|---|---:|---:|---:|
| Best fidelity | **Sol Ultra** | **79 / 100** | 52:32 | 9.47M |
| Practical sweet spot | **Sol xhigh** | **77 / 100** | 16:11 | 2.73M |
| Best value | **Sol Light** | **66 / 100** | 5:12 | 665K |
| Fastest complete run | **Luna Light** | **44 / 100** | 2:07 | 230K |

Scores are manual judgments anchored to the reference image at 100; they are not normalized so the best run automatically scores near 100.

<p align="center">
  <img src="site/assets/social/comparison-grid.jpg" alt="Reference beside Luna xhigh, Terra xhigh, and Sol Ultra benchmark renders" width="1000">
</p>

## The experiment

### Input

- One byte-identical `1672 × 941` PNG for every run
- `2,170,819` bytes
- SHA‑256: `ceaae156b019483c4fb5a0255e6b800118a0462f1207bd1253368eb41311028c`
- Canonical copy: [`gpt-5.6-sol-ultra/reference.png`](gpt-5.6-sol-ultra/reference.png)

### Exact prompt

> Build this in Blender. Create and work in a subfolder named `{run}`.

No scene graph, modeling recipe, asset library, target camera, polygon budget, render settings, or intermediate guidance was provided.

### Environment

- Codex on one Ubuntu workstation
- Blender `5.0.1`
- One primary user turn per configuration
- Required outcome: editable `.blend`, generated Python builder, and final render
- Elapsed time includes shell work, Blender runs, inspection, debugging, and self-correction

### Tested matrix

| Model family | low | medium | high | xhigh | ultra |
|---|:---:|:---:|:---:|:---:|:---:|
| GPT‑5.6 Luna | ✓ | ✓ | ✓ | ✓ | n/a |
| GPT‑5.6 Terra | ✓ | ✓ | ✓ | ✓ | ✓ |
| GPT‑5.6 Sol | ✓ | ✓ | ✓ | ✓ | ✓ |
| GPT‑5.5 baseline | n/a | n/a | n/a | ✓ | n/a |

The original folder names use `light` for telemetry effort `low`, and `extra-high` for `xhigh`. There is no `max` run in the source artifacts, and no Luna Ultra run.

## Full results

| Rank | Run | Score | Time | Tokens | Objects | Builder |
|---:|---|---:|---:|---:|---:|---:|
| 1 | [Sol Ultra](gpt-5.6-sol-ultra/) | **79** | 52:32 | 9.47M | 717 | 1,129 lines |
| 2 | [Sol xhigh](gpt-5.6-sol-extra-high/) | **77** | 16:11 | 2.73M | 508 | 777 lines |
| 3 | [Terra xhigh](gpt-5.6-terra-extra-high/) | **72** | 22:25 | 2.09M | 1,166 | 437 lines |
| 4 | [GPT‑5.5 xhigh](gpt-5.5-xhigh/) | **71** | 21:34 | 1.61M | 991 | 1,075 lines |
| 5 | [Terra Ultra](gpt-5.6-terra-ultra/) | **68** | 23:21 | 1.61M | 871 | 597 lines |
| 6 | [Sol Light](gpt-5.6-sol-light/) | **66** | 5:12 | 665K | 569 | 167 lines |
| 7 | [Luna xhigh](gpt-5.6-luna-extra-high/) | **62** | 11:07 | 2.02M | 543 | 449 lines |
| 8 | [Luna High](gpt-5.6-luna-high/) | **61** | 5:57 | 693K | 519 | 428 lines |
| 9 | [Terra High](gpt-5.6-terra-high/) | **56** | 8:10 | 764K | 439 | 341 lines |
| 10 | [Sol Medium](gpt-5.6-sol-medium/) | **50** | 6:24 | 838K | 611 | 279 lines |
| 11 | [Luna Light](gpt-5.6-luna-light/) | **44** | 2:07 | 230K | 163 | 92 lines |
| 12 | [Terra Medium](gpt-5.6-terra-medium/) | **42** | 4:05 | 246K | 361 | 101 lines |
| 13 | [Sol High](gpt-5.6-sol-high/) | **41** | 9:23 | 1.23M | 652 | 416 lines |
| 14 | [Terra Light](gpt-5.6-terra-light/) | **35** | 3:47 | 245K | 408 | 88 lines |
| 15 | [Luna Medium](gpt-5.6-luna-medium/) | **34** | 3:32 | 248K | 322 | 135 lines |

The audited machine-readable table, including input, cached input, output, reasoning, tool-call, geometry, and file data, is available at [`site/assets/data/benchmark.csv`](site/assets/data/benchmark.csv).

## What the renders show

### 1. Ultra won, narrowly

Sol Ultra produced the closest semantic reconstruction at `79/100`. Sol xhigh reached `77/100` with **28.8% of the tokens** and **30.8% of the time**. The final two visual points cost another `6.74M` tokens and roughly 36 minutes.

### 2. Sol Light was the value surprise

At `665K` tokens and `5:12`, Sol Light ranked sixth and beat nine configurations. Its builder is only 167 lines, but it brute-forced 566 mesh objects into a composition that reads clearly.

### 3. Reasoning effort was non-monotonic

Sol Medium and High produced visibly separated or exploded roof geometry. Terra xhigh outscored Terra Ultra. Luna xhigh spent 2.9× the tokens of Luna High for a one-point visual improvement.

<p align="center">
  <img src="site/assets/social/sol-ladder.jpg" alt="GPT-5.6 Sol results from light through ultra, showing non-monotonic visual quality" width="1000">
</p>

### 4. Every configuration still delivered

All 15 `.blend` files reopen in Blender 5.0.1, and all expected renders are valid and nonblank. Most GPT‑5.6 runs initially used stale Blender API assumptions, especially the `BLENDER_EEVEE_NEXT` enum, and recovered through diagnosis, patching, and re-rendering.

### 5. This is semantic reconstruction, not inverse graphics

None of the generated scripts loads, samples, measures, or camera-calibrates against the reference. The agents infer “cozy low-poly forest cabin” and hand-build a plausible scene from primitives. That is useful visual understanding and tool execution, but it is not strict recovery of the pictured 3D scene.

## What the scripts reveal

The strongest builds were separated less by raw polygon count than by four modeling decisions:

1. **Coherent geometry:** continuous terrain, tapered paths, and dimensionally correct gables instead of stacked decorative slabs.
2. **Composition before detail:** framing trees, a leading path, fence, woodpile, foreground props, and distant mountains.
3. **Lighting hierarchy:** warm local window lights, a broad key, and cooler environmental fill.
4. **Controlled placement:** keeping the path, door, windows, and silhouette readable while adding vegetation.

Sol xhigh is the best engineering balance in this set: five meaningful collections, reusable geometry helpers, deterministic terrain, custom mountains, and 499 meshes. Sol Ultra is the most ambitious. Terra Ultra has the most disciplined placement logic. GPT‑5.5 xhigh is the most software-like standalone builder.

<p align="center">
  <img src="site/assets/social/editorial-reconstruction.jpg" alt="Editorial illustration of a cabin moving from reference image through wireframe to finished geometry" width="1000">
</p>

<p align="center"><sub>The image above is an editorial illustration, not a benchmark output.</sub></p>

## Interactive Sol Ultra model

The page now includes a live Three.js view of the highest-scoring scene. This is an optimized presentation derivative, not a replacement for the original benchmark artifact. The `.blend`, generated builder and final render remain untouched.

The source scene is a textureless, flat-color low-poly build. Its 51 materials preserve color, but they do not carry the Eevee lighting that gave the final render its depth. A generic browser light rig could keep the model small, but it could not reproduce the authored shadows, warm windows and environmental contrast.

| Asset property | Source scene | Web derivative |
|---|---:|---:|
| Mesh objects or primitives | 707 | 2 |
| Evaluated triangles | 51,031 | 49,265 |
| Materials | 51 | 2 unlit materials |
| Image textures | 0 | two 1024 px lighting atlases |
| Texture memory | 0 | about 11.2 MB with mipmaps |
| Binary size | 2.78 MB initial GLB | 597 KB optimized GLB |

The build pipeline:

1. Evaluates the 396 bevel modifiers so the browser receives the intended geometry.
2. Removes the fixed-camera sky card, unsupported volume fog and two foreground crop trees.
3. Consolidates the scene into a subject mesh and an environment mesh, then creates unique non-overlapping UVs for each.
4. Bakes 128-sample Cycles Combined lighting into two 1024 × 1024 lossless PNG masters.
5. Exports those meshes as `KHR_materials_unlit`, so Three.js does not need runtime lights or shadow maps.
6. Converts the embedded delivery textures to WebP, then applies quantization, pruning and Meshopt compression.

Two 1K atlases tested better than one 2K atlas here. They give the cabin its own UV domain, reduce decoded texture memory by half and produce a smaller delivered GLB. WebP keeps the browser path native and simple. KTX2 could reduce GPU memory further, but would add a transcoder for a hover-only asset that already stays near 11 MB. The decision is measured for this scene rather than treated as a universal rule. See Blender's [Cycles baking documentation](https://docs.blender.org/manual/en/5.0/render/cycles/baking.html), the [Three.js glTF loader](https://threejs.org/docs/pages/GLTFLoader.html) and Khronos's [KTX guidance](https://www.khronos.org/ktx/) for the underlying tradeoffs.

The viewer is also intentionally restrained:

- It always keeps the WebP render as the default poster and fallback.
- Fine-pointer desktops warm the 3D asset during idle time, but reveal it only after hover intent.
- Leaving the frame restores the image unless the visitor has interacted with the model.
- Touch devices and save-data connections require an explicit “Explore in 3D” tap.
- Orbit, pitch and zoom are bounded to the useful front hemisphere because the scene was authored for one camera.
- Passive hover does not capture the mouse wheel. Zoom is enabled only after the view is pinned.
- Rendering is event-driven and pauses offscreen, following Three.js's [render-on-demand guidance](https://threejs.org/manual/en/rendering-on-demand.html).
- Drawing resolution is capped by a pixel budget instead of blindly using the device's full pixel ratio.

Rebuild the model and bundled viewer with Blender 5.0.1, Node.js and npm:

```bash
npm ci
npm run build
```

The reproducible export is in [`scripts/build_web_model.py`](scripts/build_web_model.py), the viewer source is in [`src/hero-viewer.js`](src/hero-viewer.js), and the generated asset report is in [`site/assets/models/sol-ultra-diorama.json`](site/assets/models/sol-ultra-diorama.json).

## Repository layout

```text
.
├── gpt-5.5-xhigh/                 # GPT-5.5 baseline: builder, .blend, render
├── gpt-5.6-luna-{light,...}/      # Four Luna configurations
├── gpt-5.6-terra-{light,...}/     # Five Terra configurations
├── gpt-5.6-sol-{light,...}/       # Five Sol configurations
├── site/
│   ├── index.html                 # Zero-build interactive article
│   ├── app.js                     # Result data, filters, chart, dialogs
│   ├── hero-viewer.js             # Bundled Three.js progressive enhancement
│   ├── styles.css                 # Responsive editorial presentation
│   ├── assets/data/benchmark.csv  # Audited benchmark data
│   ├── assets/models/              # Baked atlases, optimized GLB, build report
│   ├── assets/renders/            # Web-optimized reference and renders
│   ├── assets/social/             # Comparison and editorial visuals
│   └── downloads/                 # Normalized .blend and script files
├── src/hero-viewer.js             # Three.js source with bounded OrbitControls
├── scripts/build_web_model.py     # Blender lighting-bake and GLB pipeline
├── scripts/validate.sh            # No-dependency repository checks
├── package.json                   # Pinned Three.js and glTF build tools
└── .github/workflows/validate.yml # CI validation
```

Blender `.blend1` backup files, Python caches, local Codex histories, and Vercel project state are intentionally excluded.

## Explore locally

The article is a zero-build static site:

```bash
python3 -m http.server 4173 -d site
```

Then open [`http://localhost:4173`](http://localhost:4173).

To inspect a result, open the `.blend` in its model folder or use the normalized files under `site/downloads/`.

The Python builders are preserved as generated. Several contain original host-specific output paths or Blender 5.0.1 API assumptions, so inspect paths before rebuilding. A typical headless invocation is:

```bash
cd gpt-5.6-sol-ultra
blender --background --python create_scene.py
```

## Validate the repository

```bash
bash scripts/validate.sh
```

The same checks run in GitHub Actions: JavaScript syntax, artifact counts, CSV totals, public links, and the absence of private/local publication state.

## Methodology and accounting

The primary telemetry source was the local Codex session record for each completed task, corroborated against artifact paths, timestamps, and saved Blender scenes.

- Reported token total = input + output
- Cached input is a subset of input
- Reasoning output is a subset of output
- Sol Ultra and Terra Ultra include marginal usage from spawned child agents
- Child histories inherit a parent token baseline; that inherited baseline was subtracted rather than double-counted
- Dollar cost is not estimated because these were subscription-backed Codex runs without a per-model API billing record

The visual rubric is:

- Composition and camera: 20
- Cabin silhouette and structural coherence: 25
- Environment completeness and depth: 20
- Materials, palette, and lighting: 20
- Handcrafted detail and cleanliness: 15

## Caveats

- One output per configuration is a capability probe, not a variance or reliability study.
- Resolutions, aspect ratios, cameras, Eevee settings, and color management were model-selected rather than normalized.
- Only eight of 15 outputs stayed near the source's 16:9 framing; every Luna output drifted.
- The matrix has no `max` run and no Luna Ultra run.
- Visual scores measure resemblance to this specific reference, not general Blender skill or aesthetic preference.
- More objects, polygons, code, or tokens are not automatically evidence of a better scene.

---

Built and audited by [Ralf Boltshauser](https://www.linkedin.com/in/ralfboltshauser/). If you are running similar agent benchmarks, feel free to reach out.
