# Cozy Low-Poly Forest Cabin

This folder contains a fully procedural Blender 5.0 reconstruction of the supplied cabin reference. The scene uses modeled geometry rather than image textures: individual wall courses, roof shingles, chimney bricks, porch boards, stone blocks, windows, lanterns, trees, terrain facets, path tiles, rocks, shrubs, grass, mushrooms, a fence, water, mountains, firewood, stump, and axe.

## Files

- `cozy_forest_cabin.blend` — finished editable Blender scene
- `cozy_forest_cabin.png` — final 1600×900 EEVEE render
- `create_scene.py` — deterministic scene generator and renderer
- `reference.png` — supplied visual reference

## Rebuild

From this folder:

```bash
blender -b --python create_scene.py
```

The script recreates the scene from an empty file, saves the `.blend`, and writes the final PNG. Blender 5.0.1 and the `BLENDER_EEVEE` engine were used. The scene is organized into named collections for terrain, background, cabin, roof, porch, props, vegetation, details, lights, and camera.
