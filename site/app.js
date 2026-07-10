const runs = [
  {
    slug: "gpt-5-5-xhigh", family: "baseline", familyLabel: "GPT-5.5", name: "GPT‑5.5 xhigh", effort: "xhigh",
    score: 79, geometry: 37, composition: 17, finish: 15, accuracy: 10, duration: 1293566, tokens: 1605339, input: 1569908, cached: 1398400, output: 35431, reasoning: 3958, tools: 32,
    objects: 991, meshes: 981, polygons: 7974, lines: 1075, dimensions: "1600 × 900",
    verdict: "Third overall under the geometry-first rubric: excellent cabin logic, weaker scene framing.",
    note: "Possibly the strongest individual cabin model: convincing logs, shingles, masonry chimney, porch and wood treatment. A large dark wedge at left, sparse depth and an oversized central cabin pull it away from the reference.",
    engineering: "The most reusable standalone script: typed helpers, named collections, a path-aware terrain, relative paths and render-engine fallback. Its 981 mesh objects make the scene effective but bloated.",
    alt: "GPT-5.5 xhigh output showing a detailed low-poly log cabin in a sparse forest clearing"
  },
  {
    slug: "gpt-5-6-luna-light", family: "luna", familyLabel: "Luna", name: "Luna · Light", effort: "low",
    score: 46, geometry: 19, composition: 14, finish: 8, accuracy: 5, duration: 126626, tokens: 229902, input: 225304, cached: 148480, output: 4598, reasoning: 293, tools: 10,
    objects: 163, meshes: 158, polygons: 1312, lines: 92, dimensions: "960 × 640",
    verdict: "The fastest finish; recognizable, but structurally simplified.",
    note: "The front-on cabin is boxy, the stacked roof slabs miss the steep silhouette, the chimney is absent and the surrounding forest reads as sparse stage scenery.",
    engineering: "A clean factory reset and deterministic seed deliver the basic ingredients in only 92 lines. Flat primitives and a partial gable explain the incomplete roof reasoning.",
    alt: "Luna Light output showing a tall boxy wooden cabin framed by simple low-poly trees"
  },
  {
    slug: "gpt-5-6-luna-medium", family: "luna", familyLabel: "Luna", name: "Luna · Medium", effort: "medium",
    score: 39, geometry: 9, composition: 15, finish: 11, accuracy: 4, duration: 211618, tokens: 248289, input: 238531, cached: 176128, output: 9758, reasoning: 842, tools: 9,
    objects: 322, meshes: 316, polygons: 2529, lines: 135, dimensions: "960 × 720",
    verdict: "The weakest full scene: its roof geometry separates from the cabin.",
    note: "Metallic-looking roof panels float away from a narrow, tall cabin. Blown emissive areas and added scene detail cannot compensate for the failed primary silhouette.",
    engineering: "The only script with no scene reset. It retains Blender's default camera and light, and a rerun would accumulate the complete scene.",
    alt: "Luna Medium output with visibly floating roof panels above a narrow cabin"
  },
  {
    slug: "gpt-5-6-luna-high", family: "luna", familyLabel: "Luna", name: "Luna · High", effort: "high",
    score: 74, geometry: 32, composition: 18, finish: 16, accuracy: 8, duration: 357218, tokens: 693414, input: 679741, cached: 574464, output: 13673, reasoning: 2377, tools: 22,
    objects: 519, meshes: 511, polygons: 5806, lines: 428, dimensions: "960 × 600",
    verdict: "A coherent, beautiful cabin that ranks sixth despite missing scene coverage.",
    note: "The lighting is attractive, but the roof is too squat, chimney blocks look odd and much of the reference's leading path and environmental story is missing.",
    engineering: "It adds mountains, water, forest layers, a custom gable, shingles, props and local lights. Cleanup is partly a no-op, and it creates 63 materials for a flat-color scene.",
    alt: "Luna High output showing a compact warmly lit cabin among rocks and low-poly trees"
  },
  {
    slug: "gpt-5-6-luna-xhigh", family: "luna", familyLabel: "Luna", name: "Luna · xhigh", effort: "xhigh",
    score: 69, geometry: 28, composition: 19, finish: 13, accuracy: 9, duration: 666506, tokens: 2021244, input: 1996535, cached: 1824768, output: 24709, reasoning: 6331, tools: 45,
    objects: 543, meshes: 533, polygons: 5048, lines: 449, dimensions: "1120 × 760",
    verdict: "More complete than Luna High, but five points lower at 2.9× the tokens.",
    note: "It covers the path, fence, lantern, porch, trees, mountains, stump, axe and logs. A centered non-wide frame, oversized nested roof and underexposure reduce resemblance.",
    engineering: "A robust factory reset, detailed helper layer and explicit output produce a complete scene. Its ground remains a decorated flat cylinder, and paths are host-specific.",
    alt: "Luna xhigh output showing a richly detailed low-poly cabin and dark forest environment"
  },
  {
    slug: "gpt-5-6-terra-light", family: "terra", familyLabel: "Terra", name: "Terra · Light", effort: "low",
    score: 39, geometry: 13, composition: 13, finish: 8, accuracy: 5, duration: 227479, tokens: 244572, input: 236702, cached: 203008, output: 7870, reasoning: 289, tools: 9,
    objects: 408, meshes: 404, polygons: 2892, lines: 88, dimensions: "1100 × 780",
    verdict: "A dense tiny script that spends its effort on the wrong geometry.",
    note: "Severe stacked roof slabs, a floating ridge beam, no convincing chimney, sparse scenery and muddy orange-green lighting dominate the result.",
    engineering: "Only 88 compressed lines create 404 meshes, including 98 roof pieces. Object-only cleanup and disproportionate roof generation make it fragile and hard to maintain.",
    alt: "Terra Light output showing a cabin with exaggerated stacked roof geometry in a dark orange forest"
  },
  {
    slug: "gpt-5-6-terra-medium", family: "terra", familyLabel: "Terra", name: "Terra · Medium", effort: "medium",
    score: 45, geometry: 17, composition: 13, finish: 9, accuracy: 6, duration: 244992, tokens: 245519, input: 236760, cached: 212480, output: 8759, reasoning: 324, tools: 9,
    objects: 361, meshes: 358, polygons: 3090, lines: 101, dimensions: "900 × 700",
    verdict: "Fast and feature-rich, but the framing hides its work.",
    note: "An enormous foreground tree obscures the cabin. The narrow frame, stacked roof strips, crushed shadows and orange-heavy grade make the scene difficult to read.",
    engineering: "Surprisingly complete in 101 lines, including a path, logs, shingles, mountains, forest and depth of field. It still uses object-only cleanup, dense one-line loops and weak local lighting.",
    alt: "Terra Medium output with a large foreground pine obscuring a small cabin"
  },
  {
    slug: "gpt-5-6-terra-high", family: "terra", familyLabel: "Terra", name: "Terra · High", effort: "high",
    score: 60, geometry: 25, composition: 15, finish: 12, accuracy: 8, duration: 489633, tokens: 764253, input: 750997, cached: 625408, output: 13256, reasoning: 1991, tools: 25,
    objects: 439, meshes: 435, polygons: 3988, lines: 341, dimensions: "1152 × 648",
    verdict: "Clean custom geometry, but too tight and too sparse.",
    note: "The cabin is recognizable and includes several correct props, yet large trees occlude it. Smooth roof surfaces, misaligned chimney blocks and a coarse forest remain visible.",
    engineering: "A major jump to factory reset, custom faceted ground and a tapered path ribbon. Architecture is compact and restrained, but the background omits the mountain geometry its materials anticipate.",
    alt: "Terra High output showing a close wooden cabin partly hidden by large low-poly trees"
  },
  {
    slug: "gpt-5-6-terra-xhigh", family: "terra", familyLabel: "Terra", name: "Terra · xhigh", effort: "xhigh",
    score: 77, geometry: 29, composition: 21, finish: 16, accuracy: 11, duration: 1345498, tokens: 2086590, input: 2064218, cached: 1974272, output: 22372, reasoning: 5938, tools: 53,
    objects: 1166, meshes: 1159, polygons: 15563, lines: 437, dimensions: "1680 × 945",
    verdict: "Strong staging and color; crossed braces and protruding roof beams keep it fourth.",
    note: "Rich ground, forest, path, fence, lantern and prop treatment make it one of the closest scenes. Crossed roof braces and a protruding rear beam are clear structural artifacts.",
    engineering: "Factory reset, script-relative output and strong detail are offset by brute-force proliferation: 1,159 meshes, individual ground facets and separate grass pieces with no collection organization.",
    alt: "Terra xhigh output showing a rich low-poly forest cabin scene with dense ground detail"
  },
  {
    slug: "gpt-5-6-terra-ultra", family: "terra", familyLabel: "Terra", name: "Terra · Ultra", effort: "ultra",
    score: 70, geometry: 27, composition: 19, finish: 14, accuracy: 10, duration: 1401255, tokens: 1612629, input: 1576987, cached: 1385984, output: 35642, reasoning: 12903, tools: 35,
    objects: 871, meshes: 862, polygons: 8140, lines: 597, dimensions: "1120 × 630",
    verdict: "Attractive shell and mood, but visible levitation is a major geometry penalty.",
    note: "The roof, chimney, gable and log shell are clean, but the stone plinth, porch and lowest stair visibly float above the terrain. The brown-green palette and simplified depth also limit the input match.",
    engineering: "One of the most disciplined builders: local RNG, true reset, coherent height-field terrain and rejection sampling protect the composition. It still creates 234 separate grass objects and no outliner collections.",
    alt: "Terra Ultra output showing a structurally clean dark wooden cabin in a simple forest"
  },
  {
    slug: "gpt-5-6-sol-light", family: "sol", familyLabel: "Sol", name: "Sol · Light", effort: "low",
    score: 75, geometry: 34, composition: 18, finish: 14, accuracy: 9, duration: 312099, tokens: 665037, input: 657071, cached: 612864, output: 7966, reasoning: 1007, tools: 25,
    objects: 569, meshes: 566, polygons: 5496, lines: 167, dimensions: "1000 × 563",
    verdict: "The value winner: fifth overall at light effort.",
    note: "The cabin is clean and well staged with chimney, porch, path, forest and foreground props. A plain roof, coarse materials and globally orange lighting leave distance to the reference.",
    engineering: "A correct reset and only 167 lines generate 566 meshes across logs, shingles, path stones, grass, mountains, props and porch. It is compressed brute force, with only two area lights and high exposure.",
    alt: "Sol Light output showing a clean warmly lit cabin, path and foreground logs"
  },
  {
    slug: "gpt-5-6-sol-medium", family: "sol", familyLabel: "Sol", name: "Sol · Medium", effort: "medium",
    score: 62, geometry: 21, composition: 19, finish: 14, accuracy: 8, duration: 384463, tokens: 838177, input: 827714, cached: 774400, output: 10463, reasoning: 1080, tools: 30,
    objects: 611, meshes: 606, polygons: 5741, lines: 279, dimensions: "720 × 450",
    verdict: "Good staging cannot hide a conflicting roof assembly.",
    note: "Scene staging and the prop checklist are strong, but roof panels, beams and planes visibly separate. Dotted side windows are another conspicuous artifact.",
    engineering: "Clean reset, readable helpers, custom gable, segmented logs and a good sun/fill/lantern lighting hierarchy. It uses 606 meshes for the benchmark's lowest-resolution output.",
    alt: "Sol Medium output showing a forest cabin with roof beams and panels visibly separating"
  },
  {
    slug: "gpt-5-6-sol-high", family: "sol", familyLabel: "Sol", name: "Sol · High", effort: "high",
    score: 57, geometry: 14, composition: 21, finish: 15, accuracy: 7, duration: 563444, tokens: 1233805, input: 1215449, cached: 1141248, output: 18356, reasoning: 3578, tools: 33,
    objects: 652, meshes: 643, polygons: 6101, lines: 416, dimensions: "1280 × 720",
    verdict: "Excellent staging and color, capped by an exploded roof.",
    note: "Camera and environmental storytelling are good, but the roof planes, rafters and beams are exploded and floating. This is a modeling failure, not render noise.",
    engineering: "The builder introduces a triangulated meadow, tapered path, custom gable, detailed props and three-tier lighting. A no-op cleanup remains, and the final roof assembly fails visually.",
    alt: "Sol High output with an attractive forest environment and visibly exploded cabin roof geometry"
  },
  {
    slug: "gpt-5-6-sol-xhigh", family: "sol", familyLabel: "Sol", name: "Sol · xhigh", effort: "xhigh",
    score: 85, geometry: 35, composition: 23, finish: 15, accuracy: 12, duration: 971295, tokens: 2729678, input: 2696097, cached: 2557952, output: 33581, reasoning: 10244, tools: 52,
    objects: 508, meshes: 499, polygons: 5770, lines: 777, dimensions: "1280 × 720",
    verdict: "Runner-up: strong geometry and composition, with flatter color depth than Ultra.",
    note: "A clean, grounded cabin with a coherent steep roof, strong path and nearly the full prop checklist. Repeated trees, shallow atmosphere and a monochromatic amber-olive palette keep it seven points behind Ultra.",
    engineering: "Best overall engineering balance: five collections, continuous height logic, triangulated terrain, irregular mountains, a real gable prism and compact grass tufts in only 499 meshes.",
    alt: "Sol xhigh output showing a detailed warm cabin, winding path and layered low-poly trees"
  },
  {
    slug: "gpt-5-6-sol-ultra", family: "sol", familyLabel: "Sol", name: "Sol · Ultra", effort: "ultra",
    score: 92, geometry: 38, composition: 24, finish: 17, accuracy: 13, duration: 3151862, tokens: 9465944, input: 9381999, cached: 8944896, output: 83945, reasoning: 31441, tools: 142,
    objects: 717, meshes: 707, polygons: 8164, lines: 1129, dimensions: "1600 × 900",
    verdict: "Clear winner: the strongest combined geometry, composition, color depth and input match.",
    note: "The cabin is grounded, the steep roof and chimney make structural sense, and the path, fence, lantern, stump, axe, logs, rocks and mushrooms are placed coherently. Varied greens, warm wood and layered depth make it the richest output, though the distant valley and golden haze still trail the source.",
    engineering: "The most ambitious system: ten collections, jittered terrain, path, water, haze, layered mountains, segmented walls, 112 shingles and renderer tuning. Five child agents contributed to 142 tool calls; rerun cleanup and portability remain imperfect.",
    alt: "Sol Ultra output showing the benchmark's most complete low-poly cabin, path, props and forest"
  }
];

const gallery = document.querySelector("#gallery");
const scoreboardBody = document.querySelector("#scoreboard-body");
const dialog = document.querySelector("#run-dialog");
const familyColors = { luna: "#7564b4", terra: "#4f7f58", sol: "#cf6330", baseline: "#343741" };

const formatTokens = value => value >= 1_000_000 ? `${(value / 1_000_000).toFixed(2)}M` : `${Math.round(value / 1_000)}K`;
const formatDuration = ms => {
  const seconds = Math.round(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  return `${minutes}:${String(seconds % 60).padStart(2, "0")}`;
};
const formatNumber = value => new Intl.NumberFormat("en-US").format(value);

function renderGallery() {
  gallery.innerHTML = runs.map(run => `
    <article class="result-card" data-family="${run.family}">
      <button class="result-open" type="button" data-slug="${run.slug}">
        <span class="sr-only">Open details for </span>
        <div class="result-image">
          <img src="assets/renders/${run.slug}.webp" alt="" loading="lazy" decoding="async">
          <span class="score-chip">${run.score}/100</span>
        </div>
        <div class="result-title-row">
          <h3>${run.name}</h3>
          <span class="family-tag ${run.family}">${run.familyLabel}</span>
        </div>
        <p class="result-meta"><span>${formatDuration(run.duration)}</span><span>${formatTokens(run.tokens)} tokens</span><span>${formatNumber(run.objects)} objects</span></p>
      </button>
    </article>
  `).join("");
}

function sortedRuns(mode) {
  const copy = [...runs];
  if (mode === "tokens-asc") return copy.sort((a, b) => a.tokens - b.tokens);
  if (mode === "time-asc") return copy.sort((a, b) => a.duration - b.duration);
  if (mode === "geometry-desc") return copy.sort((a, b) => b.geometry - a.geometry || compareWeightedScore(a, b));
  if (mode === "composition-desc") return copy.sort((a, b) => b.composition - a.composition || compareWeightedScore(a, b));
  if (mode === "finish-desc") return copy.sort((a, b) => b.finish - a.finish || compareWeightedScore(a, b));
  if (mode === "accuracy-desc") return copy.sort((a, b) => b.accuracy - a.accuracy || compareWeightedScore(a, b));
  return copy.sort(compareWeightedScore);
}

function compareWeightedScore(a, b) {
  return b.score - a.score
    || b.geometry - a.geometry
    || b.composition - a.composition
    || b.finish - a.finish
    || b.accuracy - a.accuracy;
}

function renderScoreboard(mode = "score-desc") {
  scoreboardBody.innerHTML = sortedRuns(mode).map(run => `
    <tr class="score-row" data-slug="${run.slug}" tabindex="0" aria-label="Open ${run.name} audit">
      <td><div class="table-run"><img src="assets/renders/${run.slug}.webp" alt="" loading="lazy"><div><strong>${run.name}</strong><span>${run.familyLabel} / ${run.effort}</span></div></div></td>
      <td class="score-value">${run.score}</td>
      <td>${run.geometry}<small>/40</small></td>
      <td>${run.composition}<small>/25</small></td>
      <td>${run.finish}<small>/20</small></td>
      <td>${run.accuracy}<small>/15</small></td>
      <td>${formatDuration(run.duration)}</td>
      <td>${formatTokens(run.tokens)}</td>
    </tr>
  `).join("");
}

function openRun(slug) {
  const run = runs.find(item => item.slug === slug);
  if (!run) return;
  document.querySelector("#dialog-image").src = `assets/renders/${run.slug}.webp`;
  document.querySelector("#dialog-image").alt = run.alt;
  document.querySelector("#dialog-family").textContent = `${run.familyLabel} / ${run.effort} effort`;
  document.querySelector("#dialog-title").textContent = run.name;
  document.querySelector("#dialog-verdict").textContent = run.verdict;
  document.querySelector("#dialog-note").textContent = run.note;
  document.querySelector("#dialog-engineering").textContent = run.engineering;
  document.querySelector("#dialog-blend").href = `downloads/${run.slug}/scene.blend`;
  document.querySelector("#dialog-script").href = `downloads/${run.slug}/scene.py`;
  document.querySelector("#dialog-metrics").innerHTML = [
    ["Weighted score", `${run.score} / 100`],
    ["Geometry", `${run.geometry} / 40`],
    ["Composition", `${run.composition} / 25`],
    ["Visual finish", `${run.finish} / 20`],
    ["Input match", `${run.accuracy} / 15`],
    ["Elapsed", formatDuration(run.duration)],
    ["Total tokens", formatTokens(run.tokens)],
    ["Cached input", formatTokens(run.cached)],
    ["Output tokens", formatTokens(run.output)],
    ["Tool calls", formatNumber(run.tools)],
    ["Scene objects", formatNumber(run.objects)],
    ["Mesh polygons", formatNumber(run.polygons)],
    ["Render", run.dimensions],
    ["Builder", `${formatNumber(run.lines)} lines`]
  ].map(([label, value]) => `<div><dt>${label}</dt><dd>${value}</dd></div>`).join("");
  dialog.showModal();
}

function renderChart() {
  const svg = document.querySelector("#value-chart");
  const width = 1100, height = 400;
  const margin = { top: 24, right: 35, bottom: 48, left: 44 };
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;
  const minX = Math.log10(200_000), maxX = Math.log10(10_000_000);
  const minY = 30, maxY = 95;
  const x = value => margin.left + ((Math.log10(value) - minX) / (maxX - minX)) * plotW;
  const y = value => margin.top + (1 - ((value - minY) / (maxY - minY))) * plotH;
  const xTicks = [250_000, 500_000, 1_000_000, 2_000_000, 5_000_000, 10_000_000];
  const yTicks = [30, 40, 50, 60, 70, 80, 90];
  const abbreviation = run => run.family === "baseline" ? "5.5 X" : `${run.familyLabel.slice(0, 2)} ${run.effort === "ultra" ? "U" : run.effort === "xhigh" ? "X" : run.effort[0].toUpperCase()}`;

  const grid = [
    ...yTicks.map(tick => `<line class="chart-grid" x1="${margin.left}" y1="${y(tick)}" x2="${width - margin.right}" y2="${y(tick)}"></line><text class="chart-axis-label" x="${margin.left - 10}" y="${y(tick) + 3}" text-anchor="end">${tick}</text>`),
    ...xTicks.map(tick => `<line class="chart-grid" x1="${x(tick)}" y1="${margin.top}" x2="${x(tick)}" y2="${height - margin.bottom}"></line><text class="chart-axis-label" x="${x(tick)}" y="${height - 21}" text-anchor="middle">${formatTokens(tick)}</text>`)
  ].join("");
  const labelOffsets = {
    "gpt-5-6-luna-light": [9, -12],
    "gpt-5-6-luna-high": [10, 15],
    "gpt-5-6-terra-medium": [14, 7],
    "gpt-5-6-terra-light": [14, -12],
    "gpt-5-6-luna-medium": [14, 18],
    "gpt-5-6-sol-light": [9, -14]
  };
  const points = runs.map(run => {
    const [dx, dy] = labelOffsets[run.slug] || [9, -8];
    return `
      <g role="button" tabindex="0" data-chart-slug="${run.slug}" aria-label="${abbreviation(run)}" aria-description="${run.name}: score ${run.score}, ${formatTokens(run.tokens)} tokens">
        <circle class="chart-point" cx="${x(run.tokens)}" cy="${y(run.score)}" r="6" fill="${familyColors[run.family]}"><title>${run.name}: ${run.score}/100 · ${formatTokens(run.tokens)} tokens</title></circle>
        <text class="chart-point-label" x="${x(run.tokens) + dx}" y="${y(run.score) + dy}">${abbreviation(run)}</text>
      </g>
    `;
  }).join("");
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.innerHTML = `${grid}<text class="chart-axis-label" x="${margin.left}" y="14">WEIGHTED SCORE</text><text class="chart-axis-label" x="${width - margin.right}" y="${height - 4}" text-anchor="end">REPORTED TOKENS · LOG SCALE</text>${points}`;
}

renderGallery();
renderScoreboard();
renderChart();

function setupPromptCycle() {
  const cycle = document.querySelector("[data-run-cycle]");
  const card = cycle?.closest(".prompt-card");
  if (!cycle || !card) return;

  const labels = runs
    .slice()
    .sort(compareWeightedScore)
    .map(run => run.slug
      .replace(/^gpt-(\d)-(\d)-/, "gpt-$1.$2-")
      .replace("-extra-high", "-xhigh"));
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
  let index = 0;
  let timer = 0;
  let changeTimer = 0;

  const update = (animate = true) => {
    const next = labels[index];
    index = (index + 1) % labels.length;
    if (!animate || reducedMotion.matches) {
      cycle.textContent = next;
      cycle.classList.remove("is-changing");
      return;
    }
    cycle.classList.add("is-changing");
    window.clearTimeout(changeTimer);
    changeTimer = window.setTimeout(() => {
      cycle.textContent = next;
      cycle.classList.remove("is-changing");
    }, 140);
  };

  const stop = () => {
    window.clearInterval(timer);
    timer = 0;
  };
  const start = () => {
    if (reducedMotion.matches || timer || document.hidden) return;
    timer = window.setInterval(() => update(true), 1900);
  };

  update(false);
  card.addEventListener("pointerenter", stop);
  card.addEventListener("pointerleave", start);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stop();
    else start();
  });
  reducedMotion.addEventListener?.("change", () => {
    stop();
    if (!reducedMotion.matches) start();
  });
  start();
}

setupPromptCycle();

document.addEventListener("click", event => {
  const open = event.target.closest("[data-slug]");
  if (open) openRun(open.dataset.slug);
  const point = event.target.closest("[data-chart-slug]");
  if (point) openRun(point.dataset.chartSlug);
});

document.addEventListener("keydown", event => {
  const target = event.target.closest(".score-row, [data-chart-slug]");
  if (target && (event.key === "Enter" || event.key === " ")) {
    event.preventDefault();
    openRun(target.dataset.slug || target.dataset.chartSlug);
  }
});

document.querySelectorAll(".filter").forEach(button => button.addEventListener("click", () => {
  const filter = button.dataset.filter;
  document.querySelectorAll(".filter").forEach(item => {
    const active = item === button;
    item.classList.toggle("active", active);
    item.setAttribute("aria-pressed", String(active));
  });
  let visible = 0;
  document.querySelectorAll(".result-card").forEach(card => {
    const show = filter === "all" || card.dataset.family === filter;
    card.hidden = !show;
    if (show) visible += 1;
  });
  document.querySelector("#result-count").textContent = `Showing ${visible} output${visible === 1 ? "" : "s"}`;
}));

document.querySelector("#sort-results").addEventListener("change", event => renderScoreboard(event.target.value));
document.querySelector(".dialog-close").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", event => {
  if (event.target === dialog) dialog.close();
});
document.querySelector("#copy-prompt").addEventListener("click", async event => {
  const prompt = "Build this in Blender. Create and work in a subfolder named {run}.";
  try {
    await navigator.clipboard.writeText(prompt);
    event.currentTarget.textContent = "Copied";
    setTimeout(() => { event.currentTarget.textContent = "Copy prompt"; }, 1800);
  } catch {
    event.currentTarget.textContent = "Select the prompt above";
  }
});

function setupHeroViewer() {
  const host = document.querySelector("[data-model-viewer]");
  if (!host) return;
  const launchButton = host.querySelector("[data-viewer-launch]");
  const launchLabel = host.querySelector("[data-viewer-launch-label]");
  const resetButton = host.querySelector("[data-viewer-reset]");
  const showImageButton = host.querySelector("[data-viewer-poster]");
  const toolbar = host.querySelector("[data-viewer-toolbar]");
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  const saveData = Boolean(connection?.saveData);
  const hoverPreview = matchMedia("(hover: hover) and (pointer: fine)").matches && !saveData;
  const manualStart = !hoverPreview;
  host.dataset.enhanced = "true";
  host.dataset.manual = String(manualStart);
  host.dataset.load = "idle";
  host.dataset.view = "poster";
  toolbar.inert = true;

  let controller = null;
  let loadPromise = null;
  let pointerInside = false;
  let pinned = false;
  let suppressHover = false;
  let hoverTimer = 0;

  const setView = view => {
    host.dataset.view = view;
    controller?.setView(view);
  };

  const setLaunchLabel = label => {
    launchLabel.textContent = label;
  };

  const start = ({ announce = false } = {}) => {
    if (controller) return Promise.resolve(controller);
    if (loadPromise) return loadPromise;
    launchButton.disabled = true;
    if (announce) setLaunchLabel("Loading 3D");
    loadPromise = import("./hero-viewer.js")
      .then(({ mountHeroViewer }) => mountHeroViewer(host, { announce }))
      .then(viewer => {
        if (!viewer) throw new Error("The 3D viewer did not initialize.");
        controller = viewer;
        launchButton.disabled = false;
        setLaunchLabel("Open 3D scene");
        if (pinned) setView("pinned");
        else if (pointerInside && !suppressHover) setView("preview");
        else setView("poster");
        return viewer;
      })
      .catch(error => {
        controller = null;
        loadPromise = null;
        pinned = false;
        host.dataset.load = "failed";
        setView("poster");
        launchButton.disabled = false;
        setLaunchLabel("Retry 3D");
        console.warn("The 3D viewer module could not be loaded.", error);
        return null;
      });
    return loadPromise;
  };

  const announceReady = () => {
    const status = host.querySelector("[data-viewer-status]");
    if (!status) return;
    status.setAttribute("aria-live", "polite");
    status.textContent = "Interactive 3D preview ready";
  };

  const pinViewer = event => {
    const keyboardActivation = event?.detail === 0;
    pinned = true;
    suppressHover = false;
    setView("pinned");
    start({ announce: true }).then(viewer => {
      if (!viewer || !pinned) return;
      setView("pinned");
      announceReady();
      if (keyboardActivation) showImageButton.focus({ preventScroll: true });
    });
  };

  const showPoster = () => {
    pinned = false;
    suppressHover = true;
    setView("poster");
    launchButton.focus({ preventScroll: true });
  };

  launchButton.addEventListener("click", pinViewer);
  resetButton.addEventListener("click", () => controller?.resetView());
  showImageButton.addEventListener("click", showPoster);
  host.addEventListener("click", event => {
    if (event.target.closest("button") || host.dataset.view !== "poster") return;
    pinViewer(event);
  });

  host.addEventListener("pointerenter", () => {
    if (!hoverPreview) return;
    pointerInside = true;
    suppressHover = false;
    clearTimeout(hoverTimer);
    hoverTimer = setTimeout(() => {
      if (!pointerInside || suppressHover || pinned) return;
      setView("preview");
      start().then(viewer => {
        if (viewer && pointerInside && !pinned && !suppressHover) setView("preview");
      });
    }, 120);
  });

  host.addEventListener("pointerleave", () => {
    pointerInside = false;
    suppressHover = false;
    clearTimeout(hoverTimer);
    if (!pinned) setView("poster");
  });

  // Any deliberate canvas interaction pins the live view. Passive hover does
  // not capture the wheel, so the page remains easy to scroll.
  host.addEventListener("pointerdown", event => {
    if (event.target.closest("canvas") && host.dataset.view === "preview") {
      pinned = true;
      setView("pinned");
    }
  });

  host.addEventListener("viewer-error", () => {
    controller?.disposeViewer();
    controller = null;
    loadPromise = null;
    pinned = false;
    host.dataset.viewerMounted = "false";
    launchButton.disabled = false;
    setLaunchLabel("Retry 3D");
    setView("poster");
  });

  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && host.dataset.view !== "poster") showPoster();
  });

  if (!hoverPreview) return;

  const loadObserver = new IntersectionObserver((entries) => {
    if (!entries[0].isIntersecting) return;
    loadObserver.disconnect();
    const warm = () => start({ announce: false });
    if ("requestIdleCallback" in window) requestIdleCallback(warm, { timeout: 1800 });
    else setTimeout(warm, 600);
  }, { rootMargin: "250px" });
  loadObserver.observe(host);
}

setupHeroViewer();
