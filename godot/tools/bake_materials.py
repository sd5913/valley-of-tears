from pathlib import Path
import bpy,os,json

ROOT=str(Path(__file__).resolve().parents[1] / "assets" / "materials")
os.makedirs(ROOT,exist_ok=True)
original_scene=bpy.context.scene
scene=bpy.data.scenes.new('BAKE | portable valley materials')
bpy.context.window.scene=scene
scene.render.engine='CYCLES'
scene.cycles.device='GPU'
scene.cycles.samples=1
scene.render.bake.margin=8
bpy.ops.mesh.primitive_plane_add(size=20)
plane=bpy.context.object
materials=[('basalt','Basalt | rain-darkened striated stone'),('limestone','Wardens | weathered pale limestone'),('sanctuary','Sanctuary | ancient chalk and lichen'),('moss','Moss | deep velvet green'),('bark','Trees | charcoal bark')]
completed=[]
try:
    for key,name in materials:
        source=bpy.data.materials[name]
        material=source.copy()
        plane.data.materials.clear();plane.data.materials.append(material)
        nodes=material.node_tree.nodes;links=material.node_tree.links
        image=bpy.data.images.new('BAKE | '+key,width=2048,height=2048,alpha=False)
        image.filepath_raw=ROOT+'/'+key+'_albedo.png';image.file_format='PNG'
        target=nodes.new('ShaderNodeTexImage');target.image=image
        nodes.active=target
        bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'})
        image.save()
        height=bpy.data.images.new('BAKE | '+key+' height',width=2048,height=2048,alpha=False)
        height.colorspace_settings.name='Non-Color';height.filepath_raw=ROOT+'/'+key+'_height.png';height.file_format='PNG'
        target.image=height;nodes.active=target
        bump=next(n for n in nodes if n.type=='BUMP')
        output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
        emission=nodes.new('ShaderNodeEmission')
        links.new(bump.inputs['Height'].links[0].from_socket,emission.inputs['Color'])
        links.new(emission.outputs[0],output.inputs['Surface'])
        bpy.ops.object.bake(type='EMIT')
        height.save()
        completed.append(key)
        bpy.data.materials.remove(material)
    # The actual Blender world becomes a portable HDR panorama.
    scene.world=original_scene.world
    plane.hide_render=True
    camera_data=bpy.data.cameras.new('BAKE | cloud panorama')
    camera=bpy.data.objects.new('BAKE | cloud panorama',camera_data)
    scene.collection.objects.link(camera)
    camera_data.type='PANO';camera_data.panorama_type='EQUIRECTANGULAR'
    scene.camera=camera
    scene.render.resolution_x=2048;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='16'
    scene.render.filepath=ROOT+'/storm-sky.exr'
    bpy.ops.render.render(write_still=True)
    result={'baked_materials':completed,'resolution':2048,'sky':scene.render.filepath}
finally:
    bpy.context.window.scene=original_scene
    bpy.data.scenes.remove(scene)
