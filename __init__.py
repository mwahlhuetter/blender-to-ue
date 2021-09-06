# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Unreal Engine Export",
    "author" : "Michael Wahlhuetter",
    "description" : "A simple addon for a better workflow for UE",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D > UI > Unreal Export",
    "warning" : "",
    "category" : "Import-Export"
}

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

class UE_OT_ApplySubFolder(bpy.types.Operator):
    bl_idname = "object.ue_apply_sub_folder"
    bl_label = "Set Sub Folder For Selected Objects"

    def execute(self, context):
        activeObject = bpy.context.active_object
        selectedObjects = bpy.context.selected_objects

        print(f'Apply {activeObject.ue_sub_folder_path} to selected obejcts')

        for selectedObject in selectedObjects:
            selectedObject.ue_sub_folder_path = activeObject.ue_sub_folder_path

        return {'FINISHED'}

class UE_OT_ExportButton(bpy.types.Operator):
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


class UE_PT_Global_Properties(bpy.types.Panel):
    bl_label = "Global Properties"
    bl_category = "Unreal Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    bpy.types.Scene.ue_export_prefix = bpy.props.StringProperty(
        name="Prefix",
        maxlen=64,
        default="SM_")

    bpy.types.Scene.ue_output_path = bpy.props.StringProperty(
        name = "Export Dir",
        maxlen = 1024,
        default = "//",
        subtype = 'DIR_PATH')

    bpy.types.Scene.ue_overwrite = bpy.props.BoolProperty(
        name="Override Existing",
        description=(''),
        default=True
        )

    bpy.types.Scene.ue_export_tangents = bpy.props.BoolProperty(
        name="Export Tangents",
        default=True
        )

    bpy.types.Scene.ue_smoothing_type = bpy.props.EnumProperty(
        name="Smoothing",
        items=[
            ('OFF', "Normals Only", "", 0),
            ('FACE', "Face", "", 1),
            ],
        default="FACE"
        )

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        overwrite = layout.row(align=True)
        overwrite.prop(scene, 'ue_overwrite')

        overwrite = layout.row()
        overwrite.prop(scene, 'ue_export_tangents')

        smoothingType = layout.row()
        smoothingType.prop(scene, 'ue_smoothing_type')

        filePath = layout.column()
        filePath.prop(scene, 'ue_export_prefix')
        filePath.prop(scene, 'ue_output_path')

        export = layout.row()
        export.scale_y = 1.5
        export.operator("object.ue_export", icon = "EXPORT")

class UE_PT_Object_Properties(bpy.types.Panel):
    bl_label = "Object Properties"
    bl_category = "Unreal Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    bpy.types.Object.ue_sub_folder_path = bpy.props.StringProperty(
        name="Sub Folder",
        maxlen=1024,
        default="",
        subtype='NONE'
        )

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        activeObject = context.active_object
        selectedObjects = context.selected_objects

        objCount = len(selectedObjects)

        if objCount == 0:
            layout.row().label(text='Selection Empty')
            return

        if objCount == 1:
            subFolder = layout.row()
            subFolder.prop(activeObject, 'ue_sub_folder_path', icon="FILE_FOLDER")

            assetType = layout.row()
            assetType.prop(activeObject, 'name', text="", icon='OBJECT_DATA')
            return

        if objCount > 1:
            subFolder = layout.row()
            subFolder.prop(activeObject, 'ue_sub_folder_path', icon="FILE_FOLDER")

            applySubFolder = layout.row()
            applySubFolder.operator("object.ue_apply_sub_folder", icon = "CHECKMARK")

            objCountLabel = layout.row().label(text=f'{objCount} Objects Selected')
            selectedObjectsBox = layout.box()
            for selectedObject in selectedObjects:
                meshInfo = selectedObjectsBox.row()
                meshInfo.label(text=selectedObject.name)
                meshInfo.label(text=selectedObject.ue_sub_folder_path)


def register():
    bpy.utils.register_class(UE_OT_ExportButton)
    bpy.utils.register_class(UE_OT_ApplySubFolder)
    bpy.utils.register_class(UE_PT_Global_Properties)
    bpy.utils.register_class(UE_PT_Object_Properties)

def unregister():
    bpy.utils.unregister_class(UE_PT_Object_Properties)
    bpy.utils.unregister_class(UE_PT_Global_Properties)
    bpy.utils.unregister_class(UE_OT_ApplySubFolder)
    bpy.utils.unregister_class(UE_OT_ExportButton)

# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()