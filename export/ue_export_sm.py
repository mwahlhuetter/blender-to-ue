import bpy
import mathutils
import os

def export_fbx(output_path, smoothing_type, export_tangents):
    bpy.ops.export_scene.fbx(
        filepath=output_path,
        check_existing=False,
        use_selection=True,
        object_types={'MESH'},
        mesh_smooth_type=smoothing_type,
        add_leaf_bones=False,
        bake_anim=False,
        axis_forward='X',
        axis_up='Z',
        bake_space_transform=False,
        use_space_transform=True,
        use_mesh_modifiers=True,
        use_tspace=export_tangents
    )

def export_mesh(self, context, object, prefix, dir_path, overwrite):
    child_object_count = len(object.children)
    has_children = child_object_count > 0
    filename = prefix + object.name + '.fbx'
    sub_dir = object.ue_sub_folder_path
    output_dir = bpy.path.abspath(os.path.join(dir_path, sub_dir))
    output_path = os.path.join(output_dir, filename)

    if (not overwrite) and os.path.exists(output_path):
        self.report({'WARNING'}, "File " + filename +" already exists. Aborting.")
        return False

    print('Exporting mesh:', object.name)
    print('Output directory:', output_dir)

    if child_object_count > 0:
        plural = 's'if child_object_count > 1 else ''
        print(f'Mesh has {child_object_count} child object{plural}')
    
    if not os.path.exists(output_dir):
        print('Creating directory...')
        os.makedirs(output_dir)

    for child_object in object.children:
        child_object.select_set(True)

    saved_location = object.location.copy()
    object.location = mathutils.Vector((0,0,0))
    export_fbx(output_path, context.scene.ue_smoothing_type, context.scene.ue_export_tangents)
    object.location = saved_location

    for child_object in object.children:
        child_object.select_set(False)

    print(f'Successfully exported: {object.name}')
    return True

def export_meshes(self, context, selected_objects_count, prefix, dir_path, overwrite):
    success_count = 0
    for selected_object in context.selected_objects:
        success = export_mesh(self, context, selected_object, prefix, dir_path, overwrite)
        if success:
            success_count += 1

    self.report({'INFO'}, f'{success_count}/{selected_objects_count} meshes successfully exported')

class UE_OT_ExportStaticMesh(bpy.types.Operator):
    bl_idname = "object.ue_export"
    bl_label = "Export"

    def execute(self, context):
        scene = context.scene
        prefix = scene.ue_export_prefix
        dir_path = bpy.path.abspath(scene.ue_output_path)
        overwrite = scene.ue_overwrite
        selected_objects_count = len(context.selected_objects)

        if (selected_objects_count == 0):
            self.report({'ERROR'}, "Please select a mesh/meshes for export. Aborting.")
            return {'FINISHED'}

        if selected_objects_count == 1:
            success = export_mesh(self, context, context.active_object, prefix, dir_path, overwrite)
            if success:
                self.report({'INFO'}, f'Mesh {context.active_object.name} successfully exported')
            else:
                self.report({'ERROR'}, f'Exporting mesh "{context.active_object.name}" failed')
        elif selected_objects_count > 1:
            export_meshes(self, context, selected_objects_count, prefix, dir_path, overwrite)

        return {'FINISHED'}