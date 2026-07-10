import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/addons/libs/meshopt_decoder.module.js";


const INITIAL_CAMERA = new THREE.Vector3(22.2, 15.2, 32);
const INITIAL_TARGET = new THREE.Vector3(-0.15, 2.75, -0.45);


function drawingPixelRatio(width, height) {
  const mobile = matchMedia("(max-width: 700px)").matches;
  const pixelBudget = mobile ? 1_250_000 : 2_000_000;
  const budgetRatio = Math.sqrt(pixelBudget / Math.max(width * height, 1));
  return Math.max(0.8, Math.min(window.devicePixelRatio || 1, budgetRatio, 1.6));
}


function updateStatus(host, message, announce) {
  const status = host.querySelector("[data-viewer-status]");
  if (!status) return;
  status.setAttribute("aria-live", announce ? "polite" : "off");
  status.textContent = message;
}


export async function mountHeroViewer(host, { announce = false } = {}) {
  if (!host || host.dataset.viewerMounted === "true") return null;
  host.dataset.viewerMounted = "true";
  host.dataset.load = "loading";
  updateStatus(host, "Loading interactive 3D preview", announce);

  const canvasMount = host.querySelector("[data-viewer-canvas]");
  const toolbar = host.querySelector("[data-viewer-toolbar]");
  const modelUrl = host.dataset.model;
  const coarsePointer = matchMedia("(pointer: coarse)").matches;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: !coarsePointer,
      depth: true,
      powerPreference: "high-performance",
    });
  } catch (error) {
    host.dataset.load = "failed";
    host.dataset.viewerMounted = "false";
    updateStatus(host, "Static preview. Interactive 3D is unavailable.", announce);
    throw error;
  }

  const canvas = renderer.domElement;
  canvas.className = "model-canvas";
  canvas.setAttribute("aria-hidden", "true");
  canvasMount.append(canvas);

  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.AgXToneMapping;
  renderer.toneMappingExposure = 0.8;
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0xd2b39a, 0.003);

  // 55 mm on a 36 mm horizontal sensor at 16:9 is roughly a 20.7 degree
  // vertical field of view. Matching the authored camera makes the poster-to-3D
  // transition feel like the still image has become draggable.
  const camera = new THREE.PerspectiveCamera(20.7, 16 / 9, 0.1, 140);
  camera.position.copy(INITIAL_CAMERA);

  const controls = new OrbitControls(camera, canvas);
  controls.target.copy(INITIAL_TARGET);
  controls.enableDamping = true;
  controls.dampingFactor = 0.075;
  controls.enablePan = false;
  controls.enableZoom = false;
  controls.enabled = false;
  controls.minDistance = 34;
  controls.maxDistance = 48;
  controls.minPolarAngle = 1.06;
  controls.maxPolarAngle = 1.44;
  controls.minAzimuthAngle = 0.24;
  controls.maxAzimuthAngle = 0.97;
  controls.rotateSpeed = 0.5;
  controls.zoomSpeed = 0.7;
  controls.update();

  let width = 0;
  let height = 0;
  let frameRequest = 0;
  let isVisible = true;
  let viewActive = false;
  let disposed = false;

  function resize() {
    const bounds = canvasMount.getBoundingClientRect();
    const nextWidth = Math.max(1, Math.round(bounds.width));
    const nextHeight = Math.max(1, Math.round(bounds.height));
    if (nextWidth === width && nextHeight === height) return false;
    width = nextWidth;
    height = nextHeight;
    renderer.setPixelRatio(drawingPixelRatio(width, height));
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    return true;
  }

  function renderFrame() {
    frameRequest = 0;
    if (disposed || !viewActive || !isVisible || document.hidden) return;
    resize();
    const controlsChanged = controls.update();
    renderer.render(scene, camera);
    if (controlsChanged) requestRender();
  }

  function requestRender() {
    if (!frameRequest && viewActive && isVisible && !document.hidden && !disposed) {
      frameRequest = requestAnimationFrame(renderFrame);
    }
  }

  controls.addEventListener("change", requestRender);

  const resizeObserver = new ResizeObserver(() => {
    if (viewActive) requestRender();
  });
  resizeObserver.observe(canvasMount);

  const visibilityObserver = new IntersectionObserver((entries) => {
    isVisible = entries[0].isIntersecting;
    if (isVisible && viewActive) requestRender();
  }, { rootMargin: "100px" });
  visibilityObserver.observe(host);

  const onVisibilityChange = () => {
    if (!document.hidden && viewActive) requestRender();
  };
  document.addEventListener("visibilitychange", onVisibilityChange);

  const onContextLost = (event) => {
    event.preventDefault();
    host.dataset.load = "failed";
    host.dataset.view = "poster";
    host.dispatchEvent(new CustomEvent("viewer-error"));
    updateStatus(host, "Static preview. The 3D context was lost.", true);
  };
  canvas.addEventListener("webglcontextlost", onContextLost);

  try {
    const loader = new GLTFLoader();
    loader.setMeshoptDecoder(MeshoptDecoder);
    const gltf = await loader.loadAsync(modelUrl, (event) => {
      if (!event.total || !announce) return;
      const percent = Math.min(99, Math.round((event.loaded / event.total) * 100));
      updateStatus(host, `Loading interactive 3D preview · ${percent}%`, true);
    });

    const model = gltf.scene;
    model.name = "GPT-5.6 Sol Ultra baked web diorama";
    model.traverse((object) => {
      if (!object.isMesh) return;
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      materials.forEach((material) => {
        material.fog = true;
        material.toneMapped = true;
        if (material.map) {
          material.map.anisotropy = Math.min(2, renderer.capabilities.getMaxAnisotropy());
        }
      });
    });
    scene.add(model);
    model.updateMatrixWorld(true);
    model.traverse((object) => {
      if (object !== model) object.matrixAutoUpdate = false;
    });

    // Compile shaders and upload both baked textures while the poster is still
    // opaque. The first hover therefore reveals a complete frame, not a pop-in.
    resize();
    renderer.compile(scene, camera);
    renderer.render(scene, camera);
    host.dataset.load = "ready";
    updateStatus(host, "Interactive 3D preview ready", announce);
  } catch (error) {
    host.dataset.load = "failed";
    host.dataset.view = "poster";
    host.dataset.viewerMounted = "false";
    updateStatus(host, "Static preview. Interactive 3D could not be loaded.", announce);
    disposeViewer();
    throw error;
  }

  function setView(view) {
    viewActive = view === "preview" || view === "pinned";
    controls.enabled = viewActive;
    controls.enableZoom = view === "pinned";
    canvasMount.inert = !viewActive;
    if (toolbar) toolbar.inert = !viewActive;
    if (viewActive) requestRender();
  }

  function resetView() {
    camera.position.copy(INITIAL_CAMERA);
    controls.target.copy(INITIAL_TARGET);
    controls.update();
    requestRender();
  }

  function disposeViewer() {
    disposed = true;
    if (frameRequest) cancelAnimationFrame(frameRequest);
    resizeObserver.disconnect();
    visibilityObserver.disconnect();
    document.removeEventListener("visibilitychange", onVisibilityChange);
    controls.dispose();
    scene.traverse((object) => {
      if (object.geometry) object.geometry.dispose();
      const materials = object.material
        ? (Array.isArray(object.material) ? object.material : [object.material])
        : [];
      materials.forEach((material) => {
        for (const value of Object.values(material)) {
          if (value?.isTexture) value.dispose();
        }
        material.dispose();
      });
    });
    renderer.dispose();
    canvas.remove();
  }

  return { canvas, setView, resetView, disposeViewer };
}
