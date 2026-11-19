# Saved Checkpoint

The local repository is `/home/venetanji/Projects/valley-of-tears`.
The public GitHub repository is `https://github.com/sd5913/valley-of-tears`,
configured as `origin`.

## Preserved

- Editable original and animated Blender scenes, construction scripts, and
  camera keyframes.
- Final wide and close artwork, completed H.264 flyby, and all 288 PNG frames.
- Godot project, exported geometry, baked texture maps, HDR sky, shaders,
  flight controls, verification scripts, and two final GPU previews.
- The original working folders remain at
  `/home/venetanji/Pictures/valley-of-tears` and
  `/home/venetanji/Projects/valley-of-tears-godot`.

The repository copy is the checkpoint to continue from. Godot's `.godot` import
cache and intermediate diagnostic screenshots are omitted. Blender backup files
remain in the original working folder. All source assets required to reopen
either application are included in Git.

## Known Limits

The free camera has no collision. Screen-space reflections depend on the view;
the reflection probe and sky supply the fallback. The Godot adaptation retains
the original atmosphere but uses real-time rasterization rather than Cycles.
Godot reports seven texture RIDs still allocated during Forward+ process
shutdown; the live visual and input checks complete without script errors.

## Verified In This Repository

- Godot camera tests: 12 behavior checks passed.
- Native NVIDIA Forward+ rendering and six input/framebuffer checks passed.
- A fresh Godot editor asset import completed without script or import errors.
- The complete MP4 decoded successfully with FFmpeg.
- All 288 sequential PNG frames are present; all Python sources parse.
- Both saved Blender scenes opened with no missing external image dependencies.
- Every individual source or asset file is below 100 MB.
- A deliberately broken camera state correctly makes the test harness exit 1.

## Tomorrow

Open `godot/project.godot`, or play the finished video under `blender/`.
The installed Omarchy app launcher entry is **Valley of Tears**. Its installer
and artwork icon are preserved in `desktop/`; run `python3 desktop/install.py`
to reinstall it after moving or cloning the checkout.
The repository includes the complete frame sequence, so its Git history is
several hundred megabytes. Every individual file is below 100 MB. Git LFS is
not installed or required for this checkpoint. Continue work on the `main`
branch and push future commits to `origin`.
