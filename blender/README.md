# Valley of Tears

An original dark fantasy environment built in Blender 5.3 through Blender MCP.

The Wardens have wept since the names were lost. Each year, one pilgrim crosses
the old bridge to keep the last sanctuary flame alive.

## Deliverables

- `valley-of-tears.blend`: editable scene, organized collections, two cameras,
  procedural shaders, packed final artwork, and embedded construction scripts.
- `valley-of-tears.png`: 1920 x 1260 wide composition.
- `the-first-warden.png`: 1400 x 1400 closer composition.

The original Blender starter scene is retained as a separate scene. All landscape
geometry, faces, architecture, vegetation, and shaders were generated specifically
for this project. There are no downloaded assets or required external textures.

## Exploring

The main area displays the finished wide artwork. Press Shift+F5 to return that
area to the 3D viewport, then Numpad 0 for the composed camera view. The second
camera is named `Detail | beneath the First Warden`.

The source scripts run in order inside Blender: `build_valley.py`,
`polish_valley.py`, and `finish_valley.py`. They are also embedded as text blocks.

## Ray-Traced Flyby

`valley-of-tears-flyby.blend` adds a separate animated camera and retains both
original cameras. The 12-second route runs from frames 1 through 288 at 24 fps:
river approach, bridge crossing, passage between the Wardens, and the sanctuary.
The route is baked to editable position and quaternion keyframes. Timeline
markers name the main moments, and collection 09 contains a route reference.

The renderer is Cycles with GPU Compute, NVIDIA OptiX, 24 samples, adaptive
sampling, OptiX denoising, motion blur, and 1280 x 840 output. The current Blender
session detects an NVIDIA GeForce RTX 3060 Laptop GPU with 6 GB of VRAM and uses
NVIDIA Vulkan for graphics; restarting Blender was unnecessary.

`add_flyby.py` creates the rig. `render_flyby.py` selects OptiX in its own Blender
process and renders a resumable PNG sequence into `flyby-frames`. Render progress
is recorded in `flyby-render-status.json`. The original still project is retained.

To preview the route in the 3D viewport, use Numpad 0 for the active camera and
Space to play. The completed `valley-of-tears-flyby.mp4` contains all 288 frames
at 24 fps, 1280 x 840, with H.264 video. Encoding and full-file decoding were
verified. The complete sequence is included in `flyby-frames`.
