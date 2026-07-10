# Low-poly forest cabin

This folder contains a fully procedural Blender 5.0 scene inspired by the supplied reference.

- `low_poly_forest_cabin.blend` — editable scene with organized collections
- `low_poly_forest_cabin.png` — final 1280×720 Eevee render
- `build_scene.py` — deterministic scene generator

The scene is self-contained and uses no external textures or assets. To rebuild it:

```bash
blender --background --python build_scene.py
```
