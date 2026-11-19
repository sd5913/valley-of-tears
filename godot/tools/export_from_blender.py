from pathlib import Path
import bpy
import os
import json

ROOT=str(Path(__file__).resolve().parents[1])
scene=bpy.context.scene
scene.frame_set(1)
assert scene.name=='VALLEY OF TEARS | The Weeping Wardens'
old_selection=list(bpy.context.selected_objects)
old_active=bpy.context.view_layer.objects.active
temporary=bpy.data.collections.new('TEMP | glTF curve conversion')
scene.collection.children.link(temporary)
created=[]
excluded=[]

try:
    for obj in scene.objects:
        obj.select_set(False)
    graph=bpy.context.evaluated_depsgraph_get()
    for obj in list(scene.objects):
        if obj.hide_render or obj.type not in {'MESH','CURVE'}:
            continue
        materials=list(obj.data.materials)
        if any(m and m.use_nodes and any(n.type=='PRINCIPLED_VOLUME' for n in m.node_tree.nodes) for m in materials):
            excluded.append(obj.name)
            continue
        if obj.type=='CURVE':
            data=bpy.data.meshes.new_from_object(obj.evaluated_get(graph),depsgraph=graph)
            if not data.vertices:
                bpy.data.meshes.remove(data)
                continue
            copy=bpy.data.objects.new(obj.name+' | glTF mesh',data)
            copy.matrix_world=obj.matrix_world.copy()
            temporary.objects.link(copy)
            copy.select_set(True)
            created.append((copy,data))
        else:
            obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=ROOT+'/assets/valley.glb',export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_cameras=False,export_lights=False,export_extras=True,export_materials='EXPORT',export_yup=True)
    material_names=sorted({slot.material.name for obj in scene.objects if obj.type in {'MESH','CURVE'} for slot in obj.material_slots if slot.material})
    point_lights=[{'name':o.name,'position':[o.location.x,o.location.z,-o.location.y],'color':list(o.data.color),'power':o.data.energy,'radius':o.data.shadow_soft_size} for o in scene.objects if o.type=='LIGHT' and o.data.type=='POINT']
    manifest={'source':bpy.data.filepath,'scene':scene.name,'axis_conversion':'Blender (x,y,z) -> Godot (x,z,-y)','converted_curves':len(created),'excluded_volume_objects':excluded,'materials':material_names,'point_lights':point_lights,'portable_asset':'assets/valley.glb'}
    with open(ROOT+'/assets/source-manifest.json','w') as handle:
        json.dump(manifest,handle,indent=2)
    result={'glb':ROOT+'/assets/valley.glb','bytes':os.path.getsize(ROOT+'/assets/valley.glb'),'converted_curves':len(created),'excluded_volume_objects':excluded}
finally:
    for obj,data in created:
        bpy.data.objects.remove(obj,do_unlink=True)
        if data.users==0:bpy.data.meshes.remove(data)
    bpy.data.collections.remove(temporary)
    for obj in bpy.context.selected_objects:obj.select_set(False)
    for obj in old_selection:obj.select_set(True)
    bpy.context.view_layer.objects.active=old_active
