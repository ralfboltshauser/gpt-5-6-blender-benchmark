import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { MeshoptDecoder } from "three/addons/libs/meshopt_decoder.module.js";


const INITIAL_CAMERA = new THREE.Vector3(22.2, 15.2, 32);
const INITIAL_TARGET = new THREE.Vector3(-0.15, 2.75, -0.45);


function drawingPixelRatio(width, height) {
  const mobile = matchMedia("(max-width: 700px)").matches;
  const pixelBudget = mobile ? 1_250_000 : 2_000_000;
  const budgetRatio = Math.sqrt(pixelBudget / Math.max(width * height, 1));
  return Math.max(0.8, Math.min(window.devicePixelRatio || 1, budgetRatio, 1.6));
}


function updateStatus(host, message) {
  const status = host.querySelector("[data-viewer-status]");
  if (status) status.textContent = message;
}


export async function mountHeroViewer(host) {
  if (!host || host.dataset.viewerMounted === "true") return;
  host.dataset.viewerMounted = "true";
  host.dataset.state = "loading";
  updateStatus(host, "Loading 3D scene");

  const canvasMount = host.querySelector("[data-viewer-canvas]");
  const resetButton = host.querySelector("[data-viewer-reset]");
  const modelUrl = host.dataset.model;
  const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
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
    host.dataset.state = "fallback";
    updateStatus(host, "Static preview");
    return;
  }

  const canvas = renderer.domElement;
  canvas.className = "model-canvas";
  canvas.setAttribute("aria-hidden", "true");
  canvasMount.append(canvas);

  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.AgXToneMapping;
  renderer.toneMappingExposure = 0.92;
  renderer.setClearColor(0x000000, 0);

  const enableShadows = !coarsePointer || window.innerWidth >= 760;
  renderer.shadowMap.enabled = enableShadows;
  renderer.shadowMap.type = THREE.PCFShadowMap;

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0xd9ad82, 0.0075);

  const camera = new THREE.PerspectiveCamera(26, 16 / 9, 0.1, 140);
  camera.position.copy(INITIAL_CAMERA);

  const controls = new OrbitControls(camera, canvas);
  controls.target.copy(INITIAL_TARGET);
  controls.enableDamping = true;
  controls.dampingFactor = 0.075;
  controls.enablePan = false;
  controls.minDistance = 33;
  controls.maxDistance = 49;
  controls.minPolarAngle = 1.02;
  controls.maxPolarAngle = 1.46;
  controls.minAzimuthAngle = 0.08;
  controls.maxAzimuthAngle = 1.14;
  controls.rotateSpeed = 0.55;
  controls.zoomSpeed = 0.75;
  controls.update();

  const pmrem = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment();
  const environmentTarget = pmrem.fromScene(room, 0.04);
  scene.environment = environmentTarget.texture;
  room.traverse((object) => {
    if (object.geometry) object.geometry.dispose();
    if (object.material) object.material.dispose();
  });
  pmrem.dispose();

  const hemisphere = new THREE.HemisphereLight(0xffdfbf, 0x344b3d, 1.1);
  scene.add(hemisphere);

  const key = new THREE.DirectionalLight(0xffc58f, 3.2);
  key.position.set(-13, 24, 15);
  key.target.position.copy(INITIAL_TARGET);
  key.castShadow = enableShadows;
  key.shadow.mapSize.set(coarsePointer ? 512 : 1024, coarsePointer ? 512 : 1024);
  key.shadow.camera.left = -22;
  key.shadow.camera.right = 22;
  key.shadow.camera.top = 22;
  key.shadow.camera.bottom = -22;
  key.shadow.camera.near = 1;
  key.shadow.camera.far = 70;
  key.shadow.bias = -0.0003;
  key.shadow.normalBias = 0.025;
  scene.add(key, key.target);

  const windowGlow = new THREE.PointLight(0xff7c2d, 16, 12, 2);
  windowGlow.position.set(0.2, 3.0, 1.0);
  scene.add(windowGlow);

  let width = 0;
  let height = 0;
  let frameRequest = 0;
  let isVisible = true;
  let disposed = false;
  let userInteracted = false;
  let introEnd = 0;
  let shadowFrames = enableShadows ? 2 : 0;

  function resize() {
    const bounds = canvasMount.getBoundingClientRect();
    const nextWidth = Math.max(1, Math.round(bounds.width));
    const nextHeight = Math.max(1, Math.round(bounds.height));
    if (nextWidth === width && nextHeight === height) return;
    width = nextWidth;
    height = nextHeight;
    renderer.setPixelRatio(drawingPixelRatio(width, height));
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  function renderFrame(time = performance.now()) {
    frameRequest = 0;
    if (disposed || !isVisible || document.hidden) return;
    resize();
    const introActive = !userInteracted && time < introEnd;
    controls.autoRotate = introActive;
    controls.autoRotateSpeed = 0.22;
    const controlsChanged = controls.update(introActive ? 1 / 60 : undefined);
    renderer.render(scene, camera);
    if (shadowFrames > 0) {
      shadowFrames -= 1;
      if (shadowFrames === 0) renderer.shadowMap.autoUpdate = false;
    }
    if (introActive || controlsChanged) requestRender();
  }

  function requestRender() {
    if (!frameRequest && isVisible && !document.hidden && !disposed) {
      frameRequest = requestAnimationFrame(renderFrame);
    }
  }

  function stopIntro() {
    userInteracted = true;
    controls.autoRotate = false;
  }

  controls.addEventListener("change", requestRender);
  canvas.addEventListener("pointerdown", stopIntro, { passive: true });
  canvas.addEventListener("wheel", stopIntro, { passive: true });

  const resizeObserver = new ResizeObserver(requestRender);
  resizeObserver.observe(canvasMount);

  const visibilityObserver = new IntersectionObserver((entries) => {
    isVisible = entries[0].isIntersecting;
    if (isVisible) requestRender();
  }, { rootMargin: "100px" });
  visibilityObserver.observe(host);

  const onVisibilityChange = () => {
    if (!document.hidden) requestRender();
  };
  document.addEventListener("visibilitychange", onVisibilityChange);

  const onContextLost = (event) => {
    event.preventDefault();
    host.dataset.state = "fallback";
    updateStatus(host, "Static preview");
  };
  canvas.addEventListener("webglcontextlost", onContextLost);

  const resetView = () => {
    stopIntro();
    camera.position.copy(INITIAL_CAMERA);
    controls.target.copy(INITIAL_TARGET);
    controls.update();
    requestRender();
  };
  resetButton?.addEventListener("click", resetView);

  try {
    const loader = new GLTFLoader();
    loader.setMeshoptDecoder(MeshoptDecoder);
    const gltf = await loader.loadAsync(modelUrl, (event) => {
      if (!event.total) return;
      const percent = Math.min(99, Math.round((event.loaded / event.total) * 100));
      updateStatus(host, `Loading 3D scene · ${percent}%`);
    });

    const model = gltf.scene;
    model.name = "GPT-5.6 Sol Ultra web diorama";
    model.traverse((object) => {
      if (!object.isMesh) return;
      object.castShadow = enableShadows && !object.name.toLowerCase().includes("water");
      object.receiveShadow = enableShadows;
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      materials.forEach((material) => {
        material.envMapIntensity = material.name.includes("Metal") ? 0.55 : 0.25;
        const texture = material.map;
        if (texture) texture.anisotropy = Math.min(2, renderer.capabilities.getMaxAnisotropy());
      });
    });
    scene.add(model);
    model.updateMatrixWorld(true);
    model.traverse((object) => {
      if (object !== model) object.matrixAutoUpdate = false;
    });

    resize();
    renderer.compile(scene, camera);
    renderer.render(scene, camera);
    introEnd = reducedMotion ? 0 : performance.now() + 2400;
    host.dataset.state = "ready";
    updateStatus(host, "Interactive 3D scene ready");
    requestRender();
  } catch (error) {
    host.dataset.state = "fallback";
    updateStatus(host, "Static preview");
    console.warn("The 3D hero could not be loaded.", error);
  }

  return function disposeViewer() {
    disposed = true;
    if (frameRequest) cancelAnimationFrame(frameRequest);
    resizeObserver.disconnect();
    visibilityObserver.disconnect();
    document.removeEventListener("visibilitychange", onVisibilityChange);
    resetButton?.removeEventListener("click", resetView);
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
    environmentTarget.dispose();
    renderer.dispose();
    canvas.remove();
  };
}
