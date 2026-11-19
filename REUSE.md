# Source And Reuse Ledger

## Accepted Sources

- Blender scene: `blender/valley-of-tears.blend`.
- Animated extension: `blender/valley-of-tears-flyby.blend`.
- Construction scripts: `blender/build_valley.py`, `blender/polish_valley.py`,
  and `blender/finish_valley.py`.
- Camera and rendering scripts: `blender/add_flyby.py`,
  `blender/render_flyby.py`, and `blender/encode_flyby.py`.
- Godot source asset: `godot/assets/valley.glb`, containing 687 mesh instances.
- Material and light provenance: `godot/assets/source-manifest.json`.

The original local Godot game template at
`Work/sd5913/templates/godot-game-template` was inspected. It is a small 2D game
without a reusable 3D flight controller or environment pipeline. The Godot
adaptation therefore uses the existing Blender scene and a small native camera
controller.

## Export Adaptation

Blender's official glTF exporter preserves the meshes. Ninety-five curves are
temporarily converted to meshes so facial seams, tear filaments, and other
details survive export. Blender volumetric objects are excluded because their
materials do not transfer as volumes through this glTF pipeline.

Procedural Blender shader graphs do not transfer through glTF. The original
basalt, limestone, sanctuary stone, moss, and bark colors and height fields are
baked to 2048-square images with Cycles. Native Godot materials use these colors
and generated normal maps with world triplanar mapping. The original procedural
world is baked to a 2048 x 1024 HDR panorama. Godot-native shaders and fog restore
water movement and atmosphere.

The axis conversion is Blender `(x, y, z)` to Godot `(x, z, -y)`.

## Versions And Notices

Tested with Blender 5.3.0 and Godot 4.7.2 stable, installed Arch Linux build
`ed1daf0bf`. No external source package is vendored and no downloaded art or
third-party asset pack is included. Tool-generated files retain their metadata.

Regeneration scripts resolve their paths relative to their own files. Run
Blender scripts with `blender --background <scene.blend> --python <script.py>`;
the flyby renderer expects a working NVIDIA OptiX device. Rebuilding the scene
starts with `build_valley.py`, followed by `polish_valley.py`, `finish_valley.py`,
and `add_flyby.py`, reopening the saved scene between stages. The checked-in
editable scenes and baked assets can be opened without running these scripts.
